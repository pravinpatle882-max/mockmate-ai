import os
import json
import re
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Lazy loading of SentenceTransformer model to ensure fast server boot
_st_model = None
_st_attempted = False

def get_sentence_transformer_model():
    global _st_model, _st_attempted
    if not _st_attempted:
        _st_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            _st_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"SentenceTransformer load notice: {e}")
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
    except Exception:
        words_answer = set(re.findall(r'\w+', answer.lower()))
        words_expected = set(re.findall(r'\w+', expected.lower()))
        if not words_expected:
            return 0.5
        intersection = words_answer.intersection(words_expected)
        union = words_answer.union(words_expected)
        return len(intersection) / len(union) if union else 0.0

def compute_semantic_similarity(answer: str, expected: str) -> float:
    """
    Computes semantic vector similarity score (0.0 to 1.0) using Sentence Transformers,
    with instant TF-IDF n-gram cosine similarity fallback.
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

    tfidf_sim = compute_tfidf_similarity(answer, expected)
    return round(min(1.0, tfidf_sim * 1.15), 2)

def compute_keyword_coverage(candidate: str, expected: str) -> float:
    """Computes technical keyword coverage ratio between candidate response and expected answer."""
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "up", "about", "into", "over", "after", "this", "that", "these", "those",
        "it", "its", "what", "which", "how", "when", "where", "who", "why", "be", "been", "being", "have", "has"
    }
    cand_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', candidate.lower())) - stop_words
    exp_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', expected.lower())) - stop_words
    
    if not exp_words:
        return 0.5
    
    overlap = cand_words.intersection(exp_words)
    return len(overlap) / len(exp_words)

def evaluate_answer(
    question_text: str,
    expected_answer: str,
    candidate_answer: str
) -> Dict[str, Any]:
    """
    Rigorously evaluates candidate answer against reference answer across 5 dimensions:
    Technical Accuracy (30%), Factual Correctness (25%), Prompt Relevance (20%),
    Communication Quality (15%), and Grammar (10%).
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
            "feedback": "No response was provided for this question.",
            "strengths": ["None noted due to empty submission"],
            "weaknesses": ["Empty answer submission"],
            "suggestions": ["Ensure all questions are attempted with detailed technical explanations."]
        }

    # Step 1: Compute Vector Similarity & Keyword Coverage
    sim_score = compute_semantic_similarity(candidate_answer, expected_answer)
    kw_coverage = compute_keyword_coverage(candidate_answer, expected_answer)

    # Step 2: Gemini API Multi-Factor Evaluation (if key set)
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""
            You are a Principal Software Architect evaluating a technical candidate's interview answer.

            Question Prompt: {question_text}
            Authoritative Expected Reference Answer: {expected_answer}
            Candidate's Submitted Answer: {candidate_answer}
            Computed Vector Semantic Similarity: {sim_score:.2f}
            Keyword Coverage Ratio: {kw_coverage:.2f}

            Evaluation Rubric (Score each dimension strictly from 0.0 to 10.0):
            - technical (Weight 30%): Depth of technical knowledge, correct terminology, and architectural concepts.
            - accuracy (Weight 25%): Precision of factual statements, absence of technical hallucinations.
            - relevance (Weight 20%): Direct address of all parts of the question prompt.
            - communication (Weight 15%): Clarity, logical flow, and professional structure.
            - grammar (Weight 10%): Syntactic and grammatical correctness.

            Return strictly valid JSON without markdown wrapping or extra text outside JSON:
            {{
                "technical": 8.5,
                "accuracy": 8.0,
                "relevance": 9.0,
                "communication": 8.0,
                "grammar": 9.0,
                "overall": 8.5,
                "feedback": "Detailed constructive evaluation paragraph...",
                "strengths": ["Itemized strength 1", "Itemized strength 2"],
                "weaknesses": ["Itemized area for improvement 1"],
                "suggestions": ["Actionable recommendation 1", "Actionable recommendation 2"]
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
            
            tech = float(parsed.get("technical", 7.0))
            acc = float(parsed.get("accuracy", 7.0))
            rel = float(parsed.get("relevance", 7.0))
            comm = float(parsed.get("communication", 7.0))
            gram = float(parsed.get("grammar", 8.0))
            
            calc_overall = round((tech * 0.30) + (acc * 0.25) + (rel * 0.20) + (comm * 0.15) + (gram * 0.10), 1)

            return {
                "technical": tech,
                "accuracy": acc,
                "relevance": rel,
                "grammar": gram,
                "communication": comm,
                "overall": calc_overall,
                "semantic_similarity": round(float(sim_score), 2),
                "feedback": str(parsed.get("feedback", "Solid technical effort.")),
                "strengths": list(parsed.get("strengths", ["Addressed core prompt"])),
                "weaknesses": list(parsed.get("weaknesses", ["Elaborate with practical trade-offs"])),
                "suggestions": list(parsed.get("suggestions", ["Review key underlying principles"]))
            }
        except Exception as e:
            print(f"Gemini API Evaluation notice: {e}. Utilizing Heuristic Evaluation Engine.")

    # Step 3: Enriched Heuristic Evaluation Engine (Demo Mode)
    words = candidate_answer.split()
    word_count = len(words)
    
    # Heavy penalty for short / non-technical answers
    if word_count < 4:
        tech_base = 2.0
        acc_base = 2.0
        rel_base = 2.0
        comm_base = 2.0
    elif word_count < 10:
        tech_base = 4.5
        acc_base = 4.5
        rel_base = 5.0
        comm_base = 5.0
    else:
        tech_base = 6.0
        acc_base = 6.0
        rel_base = 6.5
        comm_base = 6.5

    # Composite similarity bonus (vector similarity + keyword coverage)
    composite_sim = (sim_score * 0.65) + (kw_coverage * 0.35)
    sim_boost = composite_sim * 4.0

    tech_score = round(max(1.0, min(10.0, tech_base + sim_boost)), 1)
    acc_score = round(max(1.0, min(10.0, acc_base + sim_boost * 0.95)), 1)
    rel_score = round(max(1.0, min(10.0, rel_base + sim_boost * 0.85)), 1)
    
    capitalized = candidate_answer[0].isupper() if candidate_answer else False
    ended_punc = candidate_answer[-1] in ".!?" if candidate_answer else False
    gram_score = round(min(10.0, 6.0 + (2.0 if capitalized else 0) + (2.0 if ended_punc else 0)), 1)
    comm_score = round(max(1.0, min(10.0, comm_base + (word_count / 15.0) + (1.5 if composite_sim > 0.4 else 0))), 1)

    overall_score = round((tech_score * 0.30) + (acc_score * 0.25) + (rel_score * 0.20) + (comm_score * 0.15) + (gram_score * 0.10), 1)

    strengths = []
    weaknesses = []
    suggestions = []

    if sim_score >= 0.65:
        strengths.append("High semantic alignment with expected technical principles.")
    elif sim_score >= 0.4:
        strengths.append("Demonstrates basic understanding of core concepts.")

    if kw_coverage >= 0.4:
        strengths.append("Utilizes relevant technical domain terminology.")
    
    if word_count >= 25:
        strengths.append("Provides a detailed, thorough explanation.")
    elif word_count >= 12:
        strengths.append("Clear and concise response structure.")

    if sim_score < 0.45:
        weaknesses.append("Missing key technical terminology and architectural reference points.")
    if word_count < 15:
        weaknesses.append("Response is brief; elaborating with examples or trade-offs increases technical depth.")
    if gram_score < 7.0:
        weaknesses.append("Punctuation or capitalization can be improved for professional formatting.")

    if not strengths:
        strengths.append("Attempted the technical prompt.")
    if not weaknesses:
        weaknesses.append("Consider illustrating concepts with code snippets or system architecture trade-offs.")

    suggestions.append(f"Review core fundamentals for: {question_text[:50]}...")
    suggestions.append("Structure answers using the 3-part framework: Definition -> Mechanics/Trade-offs -> Code Example.")
    suggestions.append("Include relevant domain terminology to strengthen overall technical accuracy.")

    feedback_msg = (
        f"Semantic Similarity: {int(sim_score * 100)}% | Technical Keyword Match: {int(kw_coverage * 100)}%. "
        f"{'Excellent technical depth!' if overall_score >= 7.5 else 'Good effort. Incorporate precise technical terminology and concrete examples.'}"
    )

    return {
        "technical": tech_score,
        "accuracy": acc_score,
        "relevance": rel_score,
        "grammar": gram_score,
        "communication": comm_score,
        "overall": overall_score,
        "semantic_similarity": round(float(sim_score), 2),
        "feedback": feedback_msg,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions
    }
