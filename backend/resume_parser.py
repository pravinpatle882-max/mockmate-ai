import re
from typing import List
from pypdf import PdfReader

# Tech skills dictionary / taxonomy
SKILL_PATTERNS = [
    "python", "javascript", "react", "react.js", "node.js", "express", "fastapi", "django",
    "flask", "sql", "postgresql", "mysql", "mongodb", "sqlite", "nosql",
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "data structures", "algorithms", "c++", "java", "c#", "go", "rust",
    "html", "css", "tailwind", "bootstrap", "git", "docker", "kubernetes",
    "aws", "azure", "gcp", "rest api", "graphql", "system design", "agile"
]

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_skills_from_text(text: str) -> List[str]:
    if not text:
        return []
    
    text_lower = text.lower()
    found_skills = set()

    for skill in SKILL_PATTERNS:
        # Match as whole word or phrase
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            # Normalize title
            found_skills.add(skill.capitalize() if len(skill) > 3 else skill.upper())

    # Map nicely formatted skill names
    format_map = {
        "PYTHON": "Python", "JAVASCRIPT": "JavaScript", "REACT": "React.js", "REACT.JS": "React.js",
        "NODE.JS": "Node.js", "FASTAPI": "FastAPI", "SQL": "SQL", "MACHINE LEARNING": "Machine Learning",
        "DEEP LEARNING": "Deep Learning", "NLP": "NLP", "DATA STRUCTURES": "Data Structures",
        "SYSTEM DESIGN": "System Design", "AWS": "AWS", "DOCKER": "Docker", "REST API": "REST APIs"
    }

    cleaned = [format_map.get(s, s) for s in found_skills]
    return sorted(list(set(cleaned)))
