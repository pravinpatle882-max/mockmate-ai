from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    domain = Column(String(50), nullable=False)
    difficulty = Column(String(30), nullable=False)
    mode = Column(String(20), default="Text") # Text or Voice
    total_score = Column(Float, default=0.0)
    status = Column(String(20), default="in_progress") # in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="interview", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question = Column(Text, nullable=False)
    expected_answer = Column(Text, nullable=False)
    difficulty = Column(String(30), nullable=True)

    interview = relationship("Interview", back_populates="questions")
    responses = relationship("Response", back_populates="question", cascade="all, delete-orphan")

class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer = Column(Text, nullable=False)
    technical_score = Column(Float, default=0.0)
    accuracy_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    grammar_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    semantic_similarity = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)   # JSON string list
    weaknesses = Column(Text, nullable=True)  # JSON string list
    suggestions = Column(Text, nullable=True) # JSON string list

    interview = relationship("Interview", back_populates="responses")
    question = relationship("Question", back_populates="responses")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    extracted_text = Column(Text, nullable=True)
    extracted_skills = Column(Text, nullable=True) # comma separated or JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")
