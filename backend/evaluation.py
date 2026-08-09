import os
import json
import re
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Lazy loading of sentence transformer model to prevent slow startup
_st_model = None
_st_attempted = False

def get_sentence_transformer_model():
    global _st_model, _st_attempted
    if not _st_attempted:
        _st_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            # Load with local cache check
            _st_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"SentenceTransformer load info: {e}")
            _st_model = False
    return _st_model

def compute_tfidf_similarity(answer: str, expected: str) -> float:
    """Fast, lightweight TF-IDF n-gram cosine similarity using scikit-learn."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        tfidf = vectorizer.fit_transform([answer, expected])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return float(sim)
    except Exception as e:
        # Simple word overlap / Jaccard similarity fallback
        words_answer = set(re.findall(r'\w+', answer.lower()))
        words_expected = set(re.findall(r'\w+', expected.lower()))
        if not words_expected:
            return 0.5
        intersection = words_answer.intersection(words_expected)
        union = words_answer.union(words_expected)
        return len(intersection) / len(union) if union else 0.0

def compute_semantic_similarity(answer: str, expected: str) -> float:
    """
    Computes semantic similarity score (0.0 to 1.0) using Sentence Transformers,
    with instant TF-IDF cosine similarity fallback.
    """
    if not answer or not expected:
        return 0.0

    model = get_sentence_transformer_model()
    if model:
        try:
            embeddings = model.encode([answer, expected], convert_to_tensor=True)
            from sentence_transformers import util
            sim = util.cos_sim(embeddings[0], embeddings[1]).item()
            return max(0.0, min(1.0, float(sim)))
        except Exception as e:
            print(f"Cos sim transformer notice: {e}")

    # High-speed TF-IDF fallback
    tfidf_sim = compute_tfidf_similarity(answer, expected)
    return round(min(1.0, tfidf_sim * 1.2), 2)

def evaluate_answer(
    question_text: str,
    expected_answer: str,
    candidate_answer: str
) -> Dict[str, Any]:
    """
    Evaluates candidate answer against expected answer using Gemini API or rule-based fallback.
    Returns numeric scores 0-10 and structured feedback.
    """
    candidate_answer = candidate_answer.strip()
    if not candidate_answer:
        return {
            "technical": 0.0,
            "accuracy": 0.0,
            "relevance": 0.0,
            "grammar": 0.0,
            "communication": 0.0,
            "overall": 0.0,
            "semantic_similarity": 0.0,
            "feedback": "No answer was provided by the candidate.",
            "strengths": ["Submitted answer"],
            "weaknesses": ["Empty response"],
            "suggestions": ["Make sure to attempt answering all questions."]
        }

    # Step 1: Compute Semantic Similarity
    sim_score = compute_semantic_similarity(candidate_answer, expected_answer)

    # Step 2: Gemini API Evaluation (if key present)
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""
            You are an expert technical interviewer evaluating a candidate's response.

            Question: {question_text}
            Expected Reference Answer: {expected_answer}
            Candidate's Answer: {candidate_answer}
            Semantic Similarity Index: {sim_score:.2f}

            Provide a rigorous evaluation on scale 0-10 for:
            - technical (technical accuracy & depth)
            - accuracy (correctness of facts)
            - relevance (directness of response to prompt)
            - grammar (language correctness)
            - communication (clarity & structure)

            Return strictly JSON with format:
            {{
                "technical": 8.0,
                "accuracy": 8.0,
                "relevance": 9.0,
                "grammar": 8.0,
                "communication": 7.0,
                "overall": 8.0,
                "feedback": "Detailed constructive feedback paragraph...",
                "strengths": ["Strength 1", "Strength 2"],
                "weaknesses": ["Weakness 1"],
                "suggestions": ["Suggestion 1", "Suggestion 2"]
            }}
            """

            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```"):
                clean_text = clean_text.split("```")[1]
                if clean_text.startswith("json"):
                    clean_text = clean_text[4:]
            clean_text = clean_text.strip()

            parsed = json.loads(clean_text)
            return {
                "technical": float(parsed.get("technical", 7.0)),
                "accuracy": float(parsed.get("accuracy", 7.0)),
                "relevance": float(parsed.get("relevance", 7.0)),
                "grammar": float(parsed.get("grammar", 8.0)),
                "communication": float(parsed.get("communication", 7.0)),
                "overall": float(parsed.get("overall", 7.2)),
                "semantic_similarity": round(float(sim_score), 2),
                "feedback": str(parsed.get("feedback", "Good effort addressing the question.")),
                "strengths": list(parsed.get("strengths", ["Addressed core prompt"])),
                "weaknesses": list(parsed.get("weaknesses", ["Can elaborate with practical code examples"])),
                "suggestions": list(parsed.get("suggestions", ["Review key underlying principles"]))
            }
        except Exception as e:
            print(f"Gemini API Evaluation failed: {e}. Falling back to Rule-based Evaluation Engine.")

    # Step 3: Heuristic Evaluation Engine (Demo Mode)
    word_count = len(candidate_answer.split())
    sim_component = sim_score * 10.0

    if word_count < 5:
        length_penalty = 3.0
    elif word_count < 15:
        length_penalty = 1.5
    else:
        length_penalty = 0.0

    tech_score = round(max(1.0, min(10.0, sim_component * 0.9 + 2.0 - length_penalty)), 1)
    acc_score = round(max(1.0, min(10.0, sim_component * 0.95 + 1.5 - length_penalty)), 1)
    rel_score = round(max(2.0, min(10.0, sim_component * 0.8 + 3.0)), 1)
    
    capitalized = candidate_answer[0].isupper() if candidate_answer else False
    ended_punc = candidate_answer[-1] in ".!?" if candidate_answer else False
    gram_score = round(min(10.0, 7.0 + (1.5 if capitalized else 0) + (1.5 if ended_punc else 0)), 1)

    comm_score = round(min(10.0, max(2.0, min(9.5, word_count / 4.0) + (2.0 if sim_score > 0.4 else 0))), 1)
    
    overall = round((tech_score * 0.3) + (acc_score * 0.25) + (rel_score * 0.2) + (gram_score * 0.1) + (comm_score * 0.15), 1)

    strengths = []
    weaknesses = []
    suggestions = []

    if sim_score > 0.6:
        strengths.append("Demonstrates good alignment with core expected technical concepts.")
    if word_count >= 20:
        strengths.append("Provided a thorough, detailed explanation.")
    elif word_count >= 10:
        strengths.append("Clear and concise response.")

    if sim_score < 0.4:
        weaknesses.append("Missing key technical terminology and core reference points.")
    if word_count < 15:
        weaknesses.append("Answer is somewhat brief and could include more depth or practical examples.")
    if gram_score < 7:
        weaknesses.append("Minor punctuation and sentence formatting improvements needed.")

    if not strengths:
        strengths.append("Good effort in addressing the question prompt.")
    if not weaknesses:
        weaknesses.append("Response could be enhanced with a real-world code snippet or architecture diagram.")

    suggestions.append(f"Review key fundamentals related to: {question_text[:50]}...")
    suggestions.append("Structure technical answers using the STAR format or clear step-by-step points.")
    suggestions.append("Include practical examples or trade-offs to boost overall technical depth.")

    return {
        "technical": float(tech_score),
        "accuracy": float(acc_score),
        "relevance": float(rel_score),
        "grammar": float(gram_score),
        "communication": float(comm_score),
        "overall": float(overall),
        "semantic_similarity": round(float(sim_score), 2),
        "feedback": f"Your response achieved a semantic similarity of {int(sim_score*100)}% with the target technical answer. "
                    f"{'Great technical grounding!' if overall >= 7.5 else 'Consider adding more specific domain terminology and concrete examples.'}",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions
    }
