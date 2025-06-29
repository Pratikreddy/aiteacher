#!/usr/bin/env python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langserve import add_routes
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import os
import json
import traceback
from dotenv import load_dotenv
from langchain.schema.runnable import RunnableLambda

load_dotenv()

app = FastAPI(
    title="AI Teacher Server",
    version="1.0",
    description="An adaptive AI teacher that personalizes learning based on student history",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

class TeacherInput(BaseModel):
    """Input for the AI teacher endpoint."""
    topic: str = Field(..., description="The topic to teach")
    student_history: str = Field(default="", description="Historical data about the student")
    education_level: str = Field(default="undergraduate", description="Current education level")
    department: str = Field(default="Computer Science", description="Student's department")
    teacher_instructions: str = Field(default="", description="Special instructions for the teacher")
    previous_responses: List[Dict[str, Any]] = Field(default=[], description="Previous Q&A in the session")

teacher_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an adaptive AI teacher specializing in personalized education. 
You MUST respond in JSON format with the following structure:
{{
    "question": "Your question here",
    "difficulty_level": "easy/medium/hard",
    "concept_tested": "The specific concept being tested",
    "hints": ["hint1", "hint2", "hint3"],
    "dos_and_donts": {{
        "dos": ["Do this", "Remember to do that"],
        "donts": ["Don't do this", "Avoid that"]
    }},
    "expected_answer_points": ["key point 1", "key point 2"],
    "knowledge_gaps_detected": ["gap1", "gap2"],
    "suggested_topics": ["topic1", "topic2"],
    "progress_assessment": {{
        "current_understanding": "percentage (0-100)",
        "strengths": ["strength1", "strength2"],
        "areas_for_improvement": ["area1", "area2"],
        "learning_velocity": "slow/moderate/fast",
        "concept_mastery": {{
            "current_topic": 0.7,
            "prerequisites": 0.5
        }}
    }},
    "teaching_strategy": {{
        "next_question_approach": "reinforce/advance/review",
        "focus_areas": ["specific concept to emphasize"],
        "avoid_areas": ["concepts to skip for now"]
    }},
    "student_learning_profile": {{
        "shows_improvement": true,
        "responds_well_to_hints": true,
        "needs_more_examples": true,
        "ready_for_harder_concepts": false
    }}
}}

IMPORTANT: Analyze the previous Q&A session deeply:
- Track if student used hints and if they helped
- Notice if student is making the same mistakes
- Identify if they're truly learning or just memorizing
- Detect frustration or confusion patterns
- Adjust your teaching based on their learning velocity

Previous Q&A in this session:
{previous_responses_str}

Student Profile:
- Education Level: {education_level}
- Department: {department}
- Historical Performance: {student_history}

Teacher Instructions: {teacher_instructions}

Your task is to ask questions about: {topic}

CRITICAL ANALYSIS REQUIRED:
1. If student scored low but showed improvement after hints, note this
2. If student keeps making the same mistake, address it directly
3. If student shows they don't understand fundamentals, go back to basics
4. Track learning velocity - are they getting faster/better?
5. Provide dos and don'ts specific to their mistakes
6. Analyze if previous dos/don'ts were followed"""),
    ("human", "Generate a question and assessment for the topic: {topic}")
])

model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    model_kwargs={"response_format": {"type": "json_object"}}
)

def format_previous_responses(responses: List[Dict[str, Any]]) -> str:
    """Format previous responses with rich learning data"""
    if not responses:
        return "No previous questions in this session"
    
    formatted = []
    for i, resp in enumerate(responses, 1):
        # Convert score to string if it's a number
        score = resp.get('score', 'N/A')
        if isinstance(score, (int, float)):
            score = str(score)
        
        # Rich formatting with learning indicators
        entry = f"""Question {i}: {resp.get('question', '')}
Answer {i}: {resp.get('answer', '')}
Score: {score}%
Hints Used: {resp.get('hints_used', 'Unknown')}
Time Taken: {resp.get('time_taken', 'Unknown')} seconds
Learning Indicators: {json.dumps(resp.get('learning_indicators', {}), indent=2)}
Dos/Don'ts Provided: {json.dumps(resp.get('dos_donts_provided', {}), indent=2)}
Improvement Shown: {resp.get('improvement_from_hints', 'Unknown')}
Concept Grasped: {resp.get('concept_grasped', 'Unknown')}
Teaching Effectiveness: {json.dumps(resp.get('teaching_effectiveness', {}), indent=2)}"""
        
        formatted.append(entry)
    
    return "\n---\n".join(formatted)

def preprocess_teacher_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess the input to format previous_responses"""
    try:
        # Debug logging
        print(f"DEBUG: Received input_data: {json.dumps(input_data, indent=2)}")
        
        # Handle both direct dict and nested input structure
        if 'input' in input_data:
            actual_data = input_data['input']
        else:
            actual_data = input_data
            
        previous_responses_str = format_previous_responses(actual_data.get('previous_responses', []))
        
        processed = {
            "topic": actual_data.get('topic', 'General'),
            "student_history": actual_data.get('student_history', ''),
            "education_level": actual_data.get('education_level', 'undergraduate'),
            "department": actual_data.get('department', 'Computer Science'),
            "teacher_instructions": actual_data.get('teacher_instructions', ''),
            "previous_responses_str": previous_responses_str
        }
        
        print(f"DEBUG: Processed data: {json.dumps(processed, indent=2)}")
        return processed
        
    except Exception as e:
        print(f"ERROR in preprocess_teacher_input: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=422, detail=f"Error processing input: {str(e)}")

teacher_chain = teacher_prompt | model

# Create a preprocessing runnable
teacher_runnable = RunnableLambda(preprocess_teacher_input) | teacher_chain

add_routes(
    app,
    teacher_runnable.with_types(input_type=TeacherInput),
    path="/teacher",
)

class AnswerEvaluationInput(BaseModel):
    """Input for evaluating student answers."""
    question: str = Field(..., description="The question that was asked")
    student_answer: str = Field(..., description="The student's answer")
    expected_points: List[str] = Field(..., description="Expected answer points")
    topic: str = Field(..., description="The topic being studied")
    student_history: str = Field(default="", description="Historical data about the student")
    previous_responses: List[Dict[str, Any]] = Field(default=[], description="Previous Q&A in the session")
    hints_used: bool = Field(default=False, description="Whether hints were used")
    time_taken: float = Field(default=0, description="Time taken to answer in seconds")
    dos_donts_provided: Dict[str, List[str]] = Field(default={}, description="Dos and don'ts provided with question")

evaluation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI teacher evaluating a student's answer.
You MUST respond in JSON format with the following structure:
{{
    "score": "0-100",
    "correct_points": ["point1", "point2"],
    "missed_points": ["point1", "point2"],
    "misconceptions": ["misconception1", "misconception2"],
    "feedback": "Detailed feedback for the student",
    "next_question_difficulty": "easier/same/harder",
    "understanding_level": "poor/fair/good/excellent",
    "specific_gaps": ["gap1", "gap2"],
    "remedial_suggestions": ["suggestion1", "suggestion2"],
    "learning_indicators": {{
        "shows_improvement": true,
        "understood_hints": true,
        "self_corrected": false,
        "grasped_concept": true,
        "ready_to_advance": false
    }},
    "dos_donts_assessment": {{
        "followed_dos": ["which dos they followed"],
        "violated_donts": ["which donts they violated"],
        "new_dos": ["new dos based on this answer"],
        "new_donts": ["new donts based on this answer"]
    }},
    "teaching_effectiveness": {{
        "hints_were_helpful": true,
        "question_was_appropriate": true,
        "student_engagement": "low/medium/high"
    }}
}}

Question asked: {question}
Expected points: {expected_points}
Student's answer: {student_answer}
Topic: {topic}
Student history: {student_history}
Previous responses: {previous_responses_str}

DEEP ANALYSIS REQUIRED:
1. Did the student actually understand or just repeat?
2. Are they making progress from previous attempts?
3. Do they need more fundamental review?
4. What specific dos and don'ts would help them?
5. Check if they followed previous dos and don'ts"""),
    ("human", "Evaluate this answer and provide detailed feedback.")
])

def preprocess_evaluation_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess the evaluation input"""
    try:
        # Handle both direct dict and nested input structure
        if 'input' in input_data:
            actual_data = input_data['input']
        else:
            actual_data = input_data
            
        previous_responses_str = format_previous_responses(actual_data.get('previous_responses', []))
        
        processed = {
            "question": actual_data.get('question', ''),
            "student_answer": actual_data.get('student_answer', ''),
            "expected_points": actual_data.get('expected_points', []),
            "topic": actual_data.get('topic', ''),
            "student_history": actual_data.get('student_history', ''),
            "previous_responses_str": previous_responses_str
        }
        
        return processed
        
    except Exception as e:
        print(f"ERROR in preprocess_evaluation_input: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Error processing input: {str(e)}")

evaluation_chain = evaluation_prompt | model

# Create a preprocessing runnable for evaluation
evaluation_runnable = RunnableLambda(preprocess_evaluation_input) | evaluation_chain

add_routes(
    app,
    evaluation_runnable.with_types(input_type=AnswerEvaluationInput),
    path="/evaluate",
)

@app.post("/debug/teacher")
async def debug_teacher_endpoint(request_body: Dict[str, Any]):
    """Debug endpoint to test the teacher chain"""
    try:
        print(f"DEBUG ENDPOINT - Received: {json.dumps(request_body, indent=2)}")
        
        # Extract input
        if 'input' in request_body:
            input_data = request_body['input']
        else:
            input_data = request_body
            
        # Process the input
        processed = preprocess_teacher_input({'input': input_data})
        print(f"DEBUG ENDPOINT - Processed: {json.dumps(processed, indent=2)}")
        
        # Call the chain
        result = teacher_chain.invoke(processed)
        print(f"DEBUG ENDPOINT - Result: {result}")
        
        return {"status": "success", "processed_input": processed, "result": result.content}
        
    except Exception as e:
        print(f"DEBUG ENDPOINT - Error: {str(e)}")
        print(f"DEBUG ENDPOINT - Traceback: {traceback.format_exc()}")
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)