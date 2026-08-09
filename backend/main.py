import os
import json
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .database import engine, Base, get_db
from .models import User, Interview, Question, Response, Resume
from .schemas import (
    UserRegister, UserLogin, Token, UserResponse,
    CreateInterviewRequest, SubmitAnswerRequest, DetailedInterviewResult,
    InterviewHistoryItem, DashboardStats, TranscribeResponse, QuestionSchema
)
from .auth import (
    get_password_hash, verify_password, create_access_token, get_current_user
)
from .ai_engine import generate_questions, GEMINI_API_KEY
from .evaluation import evaluate_answer
from .resume_parser import extract_text_from_pdf, extract_skills_from_text
from .speech import transcribe_audio_file
from .report_generator import generate_pdf_report

load_dotenv()

# Create SQLite tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MockMate AI - Intelligent Interview Preparation & Performance Evaluation",
    description="Intelligent AI Interviewer with Gemini, Semantic Evaluation & Analytics",
    version="1.0.0"
)

# Enable CORS for local dev / frontend SPA / mobile devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory Setup
UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Mount uploads & reports as static folders
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")

# --- AUTH ENDPOINTS ---

@app.post("/auth/register", response_model=Token)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_name": new_user.name,
        "user_email": new_user.email
    }

@app.post("/auth/login", response_model=Token)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_name": user.name,
        "user_email": user.email
    }

@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- RESUME ENDPOINTS ---

@app.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    save_path = os.path.join(UPLOADS_DIR, f"user_{current_user.id}_{file.filename}")
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    text = extract_text_from_pdf(save_path)
    skills = extract_skills_from_text(text)

    existing_resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if existing_resume:
        existing_resume.filename = file.filename
        existing_resume.extracted_text = text
        existing_resume.extracted_skills = json.dumps(skills)
        db.commit()
        db.refresh(existing_resume)
        resume_obj = existing_resume
    else:
        new_resume = Resume(
            user_id=current_user.id,
            filename=file.filename,
            extracted_text=text,
            extracted_skills=json.dumps(skills)
        )
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
        resume_obj = new_resume

    return {
        "id": resume_obj.id,
        "filename": resume_obj.filename,
        "extracted_skills": skills,
        "message": "Resume processed successfully"
    }

@app.get("/resume/current")
def get_current_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        return {"has_resume": False, "extracted_skills": []}
    
    skills = json.loads(resume.extracted_skills) if resume.extracted_skills else []
    return {
        "has_resume": True,
        "filename": resume.filename,
        "extracted_skills": skills,
        "created_at": resume.created_at
    }

# --- INTERVIEW ENDPOINTS ---

@app.post("/interview/create")
def create_interview(
    req: CreateInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    skills = []
    if req.use_resume_skills:
        resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
        if resume and resume.extracted_skills:
            skills = json.loads(resume.extracted_skills)

    interview = Interview(
        user_id=current_user.id,
        domain=req.domain,
        difficulty=req.difficulty,
        mode=req.mode,
        status="in_progress",
        total_score=0.0
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    raw_questions = generate_questions(
        domain=req.domain,
        difficulty=req.difficulty,
        num_questions=req.num_questions,
        resume_skills=skills
    )

    created_questions = []
    for q_item in raw_questions:
        q_obj = Question(
            interview_id=interview.id,
            question=q_item["question"],
            expected_answer=q_item.get("expected_answer", ""),
            difficulty=q_item.get("difficulty", req.difficulty)
        )
        db.add(q_obj)
        db.commit()
        db.refresh(q_obj)
        created_questions.append({
            "id": q_obj.id,
            "question": q_obj.question,
            "difficulty": q_obj.difficulty
        })

    return {
        "interview_id": interview.id,
        "domain": interview.domain,
        "difficulty": interview.difficulty,
        "mode": interview.mode,
        "questions": created_questions,
        "is_demo_mode": not bool(GEMINI_API_KEY)
    }

@app.post("/interview/submit-answer")
def submit_answer(
    req: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == req.interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    question = db.query(Question).filter(Question.id == req.question_id, Question.interview_id == interview.id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    eval_res = evaluate_answer(
        question_text=question.question,
        expected_answer=question.expected_answer,
        candidate_answer=req.answer
    )

    existing_resp = db.query(Response).filter(
        Response.interview_id == interview.id,
        Response.question_id == question.id
    ).first()

    if existing_resp:
        existing_resp.answer = req.answer
        existing_resp.technical_score = eval_res["technical"]
        existing_resp.accuracy_score = eval_res["accuracy"]
        existing_resp.relevance_score = eval_res["relevance"]
        existing_resp.grammar_score = eval_res["grammar"]
        existing_resp.communication_score = eval_res["communication"]
        existing_resp.overall_score = eval_res["overall"]
        existing_resp.semantic_similarity = eval_res["semantic_similarity"]
        existing_resp.feedback = eval_res["feedback"]
        existing_resp.strengths = json.dumps(eval_res["strengths"])
        existing_resp.weaknesses = json.dumps(eval_res["weaknesses"])
        existing_resp.suggestions = json.dumps(eval_res["suggestions"])
        db.commit()
    else:
        new_resp = Response(
            interview_id=interview.id,
            question_id=question.id,
            answer=req.answer,
            technical_score=eval_res["technical"],
            accuracy_score=eval_res["accuracy"],
            relevance_score=eval_res["relevance"],
            grammar_score=eval_res["grammar"],
            communication_score=eval_res["communication"],
            overall_score=eval_res["overall"],
            semantic_similarity=eval_res["semantic_similarity"],
            feedback=eval_res["feedback"],
            strengths=json.dumps(eval_res["strengths"]),
            weaknesses=json.dumps(eval_res["weaknesses"]),
            suggestions=json.dumps(eval_res["suggestions"])
        )
        db.add(new_resp)
        db.commit()

    return {"message": "Answer submitted and evaluated successfully", "status": "ok"}

@app.post("/interview/complete/{interview_id}")
def complete_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    responses = db.query(Response).filter(Response.interview_id == interview.id).all()
    if responses:
        avg_score = sum(r.overall_score for r in responses) / len(responses)
        interview.total_score = round(avg_score, 1)
    
    interview.status = "completed"
    db.commit()

    return {"message": "Interview completed", "interview_id": interview.id, "total_score": interview.total_score}

@app.get("/interview/history", response_model=List[InterviewHistoryItem])
def get_interview_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interviews = db.query(Interview).filter(Interview.user_id == current_user.id).order_by(Interview.created_at.desc()).all()
    history = []
    for item in interviews:
        q_count = db.query(Question).filter(Question.interview_id == item.id).count()
        history.append({
            "id": item.id,
            "domain": item.domain,
            "difficulty": item.difficulty,
            "mode": item.mode,
            "total_score": item.total_score,
            "status": item.status,
            "created_at": item.created_at,
            "questions_count": q_count
        })
    return history

@app.get("/interview/{interview_id}", response_model=DetailedInterviewResult)
def get_interview_details(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    questions = db.query(Question).filter(Question.interview_id == interview.id).all()
    responses = db.query(Response).filter(Response.interview_id == interview.id).all()

    resp_results = []
    all_strengths, all_weaknesses, all_suggestions = [], [], []
    tech_scores, acc_scores, rel_scores, gram_scores, comm_scores = [], [], [], [], []

    for r in responses:
        s_list = json.loads(r.strengths) if r.strengths else []
        w_list = json.loads(r.weaknesses) if r.weaknesses else []
        sug_list = json.loads(r.suggestions) if r.suggestions else []

        all_strengths.extend(s_list)
        all_weaknesses.extend(w_list)
        all_suggestions.extend(sug_list)

        tech_scores.append(r.technical_score)
        acc_scores.append(r.accuracy_score)
        rel_scores.append(r.relevance_score)
        gram_scores.append(r.grammar_score)
        comm_scores.append(r.communication_score)

        resp_results.append({
            "question_id": r.question_id,
            "answer": r.answer,
            "technical": r.technical_score,
            "accuracy": r.accuracy_score,
            "relevance": r.relevance_score,
            "grammar": r.grammar_score,
            "communication": r.communication_score,
            "overall": r.overall_score,
            "semantic_similarity": r.semantic_similarity,
            "feedback": r.feedback or "",
            "strengths": s_list,
            "weaknesses": w_list,
            "suggestions": sug_list
        })

    def calc_avg(lst):
        return round(sum(lst)/len(lst), 1) if lst else 0.0

    return {
        "id": interview.id,
        "domain": interview.domain,
        "difficulty": interview.difficulty,
        "mode": interview.mode,
        "total_score": interview.total_score,
        "status": interview.status,
        "created_at": interview.created_at,
        "overall_technical": calc_avg(tech_scores),
        "overall_accuracy": calc_avg(acc_scores),
        "overall_relevance": calc_avg(rel_scores),
        "overall_grammar": calc_avg(gram_scores),
        "overall_communication": calc_avg(comm_scores),
        "strengths": list(dict.fromkeys(all_strengths))[:6],
        "weaknesses": list(dict.fromkeys(all_weaknesses))[:6],
        "suggestions": list(dict.fromkeys(all_suggestions))[:6],
        "responses": resp_results,
        "questions": [{"id": q.id, "question": q.question, "expected_answer": q.expected_answer, "difficulty": q.difficulty} for q in questions]
    }

@app.get("/interview/{interview_id}/pdf")
def download_interview_pdf(
    interview_id: int,
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    questions = db.query(Question).filter(Question.interview_id == interview.id).all()
    responses = db.query(Response).filter(Response.interview_id == interview.id).all()

    resp_results = []
    all_strengths, all_weaknesses, all_suggestions = [], [], []
    tech_scores, acc_scores, rel_scores, gram_scores, comm_scores = [], [], [], [], []

    for r in responses:
        s_list = json.loads(r.strengths) if r.strengths else []
        w_list = json.loads(r.weaknesses) if r.weaknesses else []
        sug_list = json.loads(r.suggestions) if r.suggestions else []

        all_strengths.extend(s_list)
        all_weaknesses.extend(w_list)
        all_suggestions.extend(sug_list)

        tech_scores.append(r.technical_score)
        acc_scores.append(r.accuracy_score)
        rel_scores.append(r.relevance_score)
        gram_scores.append(r.grammar_score)
        comm_scores.append(r.communication_score)

        resp_results.append({
            "question_id": r.question_id,
            "answer": r.answer,
            "technical": r.technical_score,
            "accuracy": r.accuracy_score,
            "relevance": r.relevance_score,
            "grammar": r.grammar_score,
            "communication": r.communication_score,
            "overall": r.overall_score,
            "semantic_similarity": r.semantic_similarity,
            "feedback": r.feedback or "",
            "strengths": s_list,
            "weaknesses": w_list,
            "suggestions": sug_list
        })

    def calc_avg(lst):
        return round(sum(lst)/len(lst), 1) if lst else 0.0

    details = {
        "id": interview.id,
        "domain": interview.domain,
        "difficulty": interview.difficulty,
        "mode": interview.mode,
        "total_score": interview.total_score,
        "status": interview.status,
        "created_at": interview.created_at,
        "overall_technical": calc_avg(tech_scores),
        "overall_accuracy": calc_avg(acc_scores),
        "overall_relevance": calc_avg(rel_scores),
        "overall_grammar": calc_avg(gram_scores),
        "overall_communication": calc_avg(comm_scores),
        "strengths": list(dict.fromkeys(all_strengths))[:6],
        "weaknesses": list(dict.fromkeys(all_weaknesses))[:6],
        "suggestions": list(dict.fromkeys(all_suggestions))[:6],
        "responses": resp_results,
        "questions": [{"id": q.id, "question": q.question, "expected_answer": q.expected_answer, "difficulty": q.difficulty} for q in questions]
    }

    pdf_filename = f"report_interview_{interview_id}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
    generate_pdf_report(details, pdf_path)
    return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_filename)

# --- SPEECH TRANSCRIPTION ENDPOINT ---

@app.post("/speech/transcribe", response_model=TranscribeResponse)
async def transcribe_speech(
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    if file:
        temp_audio_path = os.path.join(UPLOADS_DIR, f"temp_{file.filename}")
        with open(temp_audio_path, "wb") as f:
            content = await file.read()
            f.write(content)
        text = transcribe_audio_file(temp_audio_path)
        try:
            os.remove(temp_audio_path)
        except Exception:
            pass
        return {"text": text}
    
    return {"text": "Voice response transcribed successfully."}

# --- DASHBOARD ENDPOINT ---

@app.get("/dashboard", response_model=DashboardStats)
def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interviews = db.query(Interview).filter(Interview.user_id == current_user.id, Interview.status == "completed").order_by(Interview.created_at.asc()).all()
    
    total_interviews = len(interviews)
    if total_interviews > 0:
        avg_score = round(sum(i.total_score for i in interviews) / total_interviews, 1)
        best_score = round(max(i.total_score for i in interviews), 1)
    else:
        avg_score = 0.0
        best_score = 0.0

    recent = db.query(Interview).filter(Interview.user_id == current_user.id).order_by(Interview.created_at.desc()).limit(5).all()
    recent_items = []
    for item in recent:
        q_count = db.query(Question).filter(Question.interview_id == item.id).count()
        recent_items.append({
            "id": item.id,
            "domain": item.domain,
            "difficulty": item.difficulty,
            "mode": item.mode,
            "total_score": item.total_score,
            "status": item.status,
            "created_at": item.created_at,
            "questions_count": q_count
        })

    domain_map = {}
    for item in interviews:
        if item.domain not in domain_map:
            domain_map[item.domain] = []
        domain_map[item.domain].append(item.total_score)

    domain_breakdown = [
        {"domain": d, "count": len(scores), "avg_score": round(sum(scores)/len(scores), 1)}
        for d, scores in domain_map.items()
    ]

    score_trends = [
        {"date": item.created_at.strftime("%b %d"), "score": item.total_score, "domain": item.domain}
        for item in interviews
    ]

    responses = db.query(Response).join(Interview).filter(Interview.user_id == current_user.id).all()
    all_s, all_w = [], []
    for r in responses:
        if r.strengths:
            all_s.extend(json.loads(r.strengths))
        if r.weaknesses:
            all_w.extend(json.loads(r.weaknesses))

    strong_areas = list(dict.fromkeys(all_s))[:5] if all_s else [
        "Structured technical explanations",
        "Core fundamental concepts",
        "Clear articulation"
    ]
    weak_areas = list(dict.fromkeys(all_w))[:5] if all_w else [
        "In-depth architectural trade-offs",
        "Exact system complexity analysis"
    ]

    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    skills = json.loads(resume.extracted_skills) if (resume and resume.extracted_skills) else []

    return {
        "total_interviews": total_interviews,
        "average_score": avg_score,
        "best_score": best_score,
        "recent_interviews": recent_items,
        "strong_areas": strong_areas,
        "weak_areas": weak_areas,
        "score_trends": score_trends,
        "domain_breakdown": domain_breakdown,
        "extracted_skills": skills
    }

# --- SERVE SPA FRONTEND ---
@app.get("/")
def read_root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "MockMate AI System API is running successfully!"}

@app.get("/{full_path:path}")
def serve_frontend_or_404(full_path: str):
    file_path = os.path.join(FRONTEND_DIR, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Not Found")
