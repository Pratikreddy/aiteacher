from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class ConceptMastery(BaseModel):
    concept: str
    mastery_level: float = Field(ge=0, le=1)  # 0 to 1
    last_tested: datetime
    attempts: int
    average_score: float

class StudentProfile(BaseModel):
    student_id: str
    department: str
    education_level: str
    learning_style: Optional[str] = None
    
    # Comprehensive tracking
    total_questions_answered: int = 0
    total_study_time_minutes: float = 0
    
    # Subject-wise performance
    subject_performance: Dict[str, float] = {}
    
    # Concept mastery tracking
    concept_mastery: Dict[str, ConceptMastery] = {}
    
    # Learning patterns
    best_performance_time: Optional[str] = None  # morning/afternoon/evening
    average_response_time: float = 0
    preferred_question_types: List[str] = []
    
    # Weakness tracking
    fundamental_gaps: List[Dict[str, Any]] = []
    recurring_mistakes: List[Dict[str, Any]] = []
    
    # Progress metrics
    learning_velocity: float = 0  # How fast they improve
    retention_rate: float = 0  # How well they remember
    
class Question(BaseModel):
    question_id: str
    question_text: str
    topic: str
    subtopic: Optional[str]
    concept_tested: str
    difficulty_level: DifficultyLevel
    expected_answer_points: List[str]
    hints: List[str]
    
    # Metadata
    bloom_taxonomy_level: str  # remember/understand/apply/analyze/evaluate/create
    estimated_time_minutes: float
    prerequisites: List[str] = []
    
class Answer(BaseModel):
    answer_id: str
    question_id: str
    student_id: str
    answer_text: str
    timestamp: datetime
    time_taken_seconds: float
    
    # Evaluation
    score: float
    correct_points: List[str]
    missed_points: List[str]
    misconceptions: List[str]
    
    # Context
    hints_used: int = 0
    attempt_number: int = 1

class LearningSession(BaseModel):
    session_id: str
    student_id: str
    start_time: datetime
    end_time: Optional[datetime]
    topic: str
    
    # Session data
    questions_asked: List[Question] = []
    answers_given: List[Answer] = []
    
    # Session metrics
    average_score: float = 0
    difficulty_progression: List[str] = []
    concepts_covered: List[str] = []
    knowledge_gaps_identified: List[str] = []
    
    # Recommendations
    next_topics: List[str] = []
    remedial_topics: List[str] = []
    
class TeacherInput(BaseModel):
    """Enhanced input for the AI teacher endpoint."""
    topic: str = Field(..., description="The topic to teach")
    student_profile: Optional[StudentProfile] = None
    session_context: Optional[LearningSession] = None
    teacher_instructions: str = Field(default="", description="Special instructions")
    
    # New fields for better tracking
    learning_objective: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    focus_on_gaps: bool = True
    adaptive_difficulty: bool = True

class AnalyticsData(BaseModel):
    """Analytics for tracking student progress"""
    student_id: str
    
    # Performance trends
    performance_trend: List[Dict[str, Any]]  # score over time
    concept_mastery_map: Dict[str, float]
    
    # Learning insights
    strongest_concepts: List[str]
    weakest_concepts: List[str]
    recommended_focus_areas: List[str]
    
    # Predictive metrics
    estimated_time_to_mastery: Dict[str, float]  # concept -> hours
    risk_areas: List[str]  # concepts at risk of forgetting
    
    # Comparative analysis
    percentile_in_cohort: float
    comparison_to_average: Dict[str, float]