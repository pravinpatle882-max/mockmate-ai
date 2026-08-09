from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# Auth Schemas
class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_name: str
    user_email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

# Interview Schemas
class CreateInterviewRequest(BaseModel):
    domain: str
    difficulty: str
    num_questions: int = 5
    mode: str = "Text" # Text or Voice
    use_resume_skills: bool = False

class QuestionSchema(BaseModel):
    id: int
    question: str
    expected_answer: Optional[str] = None
    difficulty: Optional[str] = None

    class Config:
        from_attributes = True

class SubmitAnswerRequest(BaseModel):
    interview_id: int
    question_id: int
    answer: str

class ResponseEvaluationResult(BaseModel):
    question_id: int
    answer: str
    technical: float
    accuracy: float
    relevance: float
    grammar: float
    communication: float
    overall: float
    semantic_similarity: float
    feedback: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]

class DetailedInterviewResult(BaseModel):
    id: int
    domain: str
    difficulty: str
    mode: str
    total_score: float
    status: str
    created_at: datetime
    overall_technical: float
    overall_accuracy: float
    overall_relevance: float
    overall_grammar: float
    overall_communication: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    responses: List[ResponseEvaluationResult]
    questions: List[QuestionSchema]

class InterviewHistoryItem(BaseModel):
    id: int
    domain: str
    difficulty: str
    mode: str
    total_score: float
    status: str
    created_at: datetime
    questions_count: int

# Resume & Dashboard Schemas
class ResumeResponse(BaseModel):
    id: int
    filename: str
    extracted_skills: List[str]
    created_at: datetime

class DashboardStats(BaseModel):
    total_interviews: int
    average_score: float
    best_score: float
    recent_interviews: List[InterviewHistoryItem]
    strong_areas: List[str]
    weak_areas: List[str]
    score_trends: List[dict] # [{date: "2026-08-09", score: 8.5}]
    domain_breakdown: List[dict] # [{domain: "Software Development", count: 4, avg_score: 8.2}]
    extracted_skills: List[str]

class TranscribeResponse(BaseModel):
    text: str
