import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from typing import Dict, List
import time
import traceback

st.set_page_config(
    page_title="PES University - AI Teacher",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for PES University branding and consistent UI
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-weight: 600;
        background-color: #1e3a8a;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1e40af;
    }
    .pes-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-card {
        background: #f8fafc;
        border: 2px solid #e2e8f0;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        text-align: center;
        border: 1px solid #e2e8f0;
        height: 100%;
    }
    .score-excellent { 
        background: #10b981; 
        color: white; 
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .score-good { 
        background: #f59e0b; 
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .score-poor { 
        background: #ef4444; 
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        font-size: 16px;
    }
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    /* Make all input boxes same height */
    .stTextArea > div > div > textarea,
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        min-height: 40px;
    }
    .error-box {
        background: #fee2e2;
        border: 1px solid #ef4444;
        padding: 1rem;
        border-radius: 10px;
        color: #991b1b;
        margin: 1rem 0;
    }
    .debug-info {
        background: #f3f4f6;
        padding: 1rem;
        border-radius: 10px;
        font-family: monospace;
        font-size: 12px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

LANGSERVE_URL = "http://localhost:8000"

PES_DEPARTMENTS = {
    "Computer Science and Engineering": ["Data Structures", "Algorithms", "Machine Learning", "Database Systems", "Operating Systems", "Computer Networks"],
    "Electronics and Communication": ["Digital Electronics", "Signal Processing", "VLSI Design", "Communication Systems", "Embedded Systems"],
    "Mechanical Engineering": ["Thermodynamics", "Fluid Mechanics", "Machine Design", "Manufacturing", "Robotics", "CAD/CAM"],
    "Civil Engineering": ["Structural Analysis", "Concrete Technology", "Transportation", "Geotechnical", "Environmental"],
    "Electrical and Electronics": ["Power Systems", "Control Systems", "Electrical Machines", "Power Electronics"],
    "Biotechnology": ["Molecular Biology", "Genetics", "Biochemistry", "Bioinformatics", "Immunology"],
    "Architecture": ["Design Studio", "Building Construction", "Urban Planning", "Sustainable Design"],
    "Management Studies": ["Marketing", "Finance", "HR Management", "Operations", "Business Analytics"]
}

EDUCATION_LEVELS = ["High School", "UG Year 1", "UG Year 2", "UG Year 3", "UG Year 4", "Masters", "PhD"]

# Initialize session state
if 'session_data' not in st.session_state:
    st.session_state.session_data = {
        'qa_history': [],
        'current_question': None,
        'scores': [],
        'knowledge_gaps': set(),
        'suggested_topics': set(),
        'total_questions': 0,
        'current_understanding': 0,
        'debug_mode': False,
        'answer_start_time': None,
        'hints_viewed': False,
        'current_dos_donts': {}
    }

def call_teacher_api(topic: str, student_history: str, education_level: str, department: str, teacher_instructions: str, previous_responses: List[Dict]):
    """Call the teacher API with proper error handling"""
    try:
        payload = {
            "input": {
                "topic": topic,
                "student_history": student_history,
                "education_level": education_level,
                "department": department,
                "teacher_instructions": teacher_instructions,
                "previous_responses": previous_responses
            }
        }
        
        if st.session_state.session_data['debug_mode']:
            st.code(f"API Request:\n{json.dumps(payload, indent=2)}", language="json")
        
        response = requests.post(
            f"{LANGSERVE_URL}/teacher/invoke",
            json=payload,
            timeout=30
        )
        
        if st.session_state.session_data['debug_mode']:
            st.code(f"API Response Status: {response.status_code}", language="text")
        
        if response.status_code == 200:
            result = response.json()
            return json.loads(result['output']['content'])
        else:
            error_detail = f"API Error {response.status_code}: {response.text}"
            st.error(error_detail)
            if st.session_state.session_data['debug_mode']:
                st.code(error_detail, language="text")
            return None
            
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return None
    except Exception as e:
        error_msg = f"Error calling teacher API: {str(e)}"
        st.error(error_msg)
        if st.session_state.session_data['debug_mode']:
            st.code(traceback.format_exc(), language="python")
        return None

def call_evaluation_api(question: str, student_answer: str, expected_points: List[str], topic: str, 
                       student_history: str, previous_responses: List[Dict], hints_used: bool, 
                       time_taken: float, dos_donts_provided: Dict):
    """Call the evaluation API with proper error handling and rich context"""
    try:
        payload = {
            "input": {
                "question": question,
                "student_answer": student_answer,
                "expected_points": expected_points,
                "topic": topic,
                "student_history": student_history,
                "previous_responses": previous_responses,
                "hints_used": hints_used,
                "time_taken": time_taken,
                "dos_donts_provided": dos_donts_provided
            }
        }
        
        response = requests.post(
            f"{LANGSERVE_URL}/evaluate/invoke",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.loads(result['output']['content'])
        else:
            st.error(f"Evaluation API Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error calling evaluation API: {str(e)}")
        return None

def create_progress_chart():
    """Create a clean line chart for progress tracking"""
    if len(st.session_state.session_data['scores']) > 0:
        df = pd.DataFrame({
            'Question': [f"Q{i+1}" for i in range(len(st.session_state.session_data['scores']))],
            'Score': st.session_state.session_data['scores']
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Question'],
            y=df['Score'],
            mode='lines+markers',
            name='Score',
            line=dict(color='#1e3a8a', width=3),
            marker=dict(size=10, color='#3730a3'),
            fill='tozeroy',
            fillcolor='rgba(30, 58, 138, 0.1)'
        ))
        
        fig.add_hline(y=70, line_dash="dash", line_color="green", 
                      annotation_text="Good Performance", annotation_position="right")
        fig.add_hline(y=40, line_dash="dash", line_color="orange", 
                      annotation_text="Needs Improvement", annotation_position="right")
        
        fig.update_layout(
            title="Performance Trend",
            xaxis_title="Questions",
            yaxis_title="Score (%)",
            yaxis=dict(range=[0, 100]),
            height=300,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
    return None

# PES University Header
st.markdown("""
<div class='pes-header'>
    <h1 style='margin: 0; font-size: 2.5rem;'>🎓 PES University - AI Teacher</h1>
    <p style='margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;'>
        Adaptive Learning Platform for PES Students
    </p>
</div>
""", unsafe_allow_html=True)

# Debug mode toggle
with st.expander("🔧 Developer Options"):
    st.session_state.session_data['debug_mode'] = st.checkbox("Enable Debug Mode", value=st.session_state.session_data['debug_mode'])

# Top metrics - removed accuracy as requested
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <h2 style='color: #3730a3; margin: 0;'>{st.session_state.session_data['total_questions']}</h2>
        <p style='color: #64748b; margin: 0;'>Questions Asked</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_score = sum(st.session_state.session_data['scores']) / len(st.session_state.session_data['scores']) if st.session_state.session_data['scores'] else 0
    st.markdown(f"""
    <div class='metric-card'>
        <h2 style='color: #10b981; margin: 0;'>{avg_score:.0f}</h2>
        <p style='color: #64748b; margin: 0;'>Average Score</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <h2 style='color: #f59e0b; margin: 0;'>{st.session_state.session_data['current_understanding']}%</h2>
        <p style='color: #64748b; margin: 0;'>Understanding</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main content
main_col, side_col = st.columns([3, 1])

with main_col:
    st.markdown("### 📚 Learning Configuration")
    
    # Configuration in a clean grid with consistent sizing
    config_col1, config_col2, config_col3 = st.columns(3)
    
    with config_col1:
        department = st.selectbox(
            "PES Department",
            options=list(PES_DEPARTMENTS.keys()),
            help="Select your department at PES University"
        )
        
        education_level = st.selectbox(
            "Education Level",
            options=EDUCATION_LEVELS,
            index=1
        )
    
    with config_col2:
        subject_topics = PES_DEPARTMENTS[department]
        topic = st.selectbox(
            "Subject/Topic",
            options=subject_topics
        )
        
        custom_topic = st.text_input(
            "Or Custom Topic",
            placeholder="Enter custom topic..."
        )
        
        if custom_topic:
            topic = custom_topic
    
    with config_col3:
        student_history = st.text_area(
            "Student Background",
            placeholder="E.g., Strong in math, weak in programming...",
            height=68
        )
        
        teacher_instructions = st.text_area(
            "Teaching Preferences",
            placeholder="E.g., Use simple examples, focus on practical applications...",
            height=68
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate Question Button
    if st.button("🚀 Generate New Question", type="primary", use_container_width=True):
        with st.spinner("AI Teacher is preparing a personalized question..."):
            # Prepare previous responses - ensure score is a string
            previous_responses = []
            for qa in st.session_state.session_data['qa_history']:
                previous_responses.append({
                    "question": qa.get('question', ''),
                    "answer": qa.get('answer', ''),
                    "score": str(qa.get('score', 0))  # Convert to string
                })
            
            result = call_teacher_api(
                topic=topic,
                student_history=student_history,
                education_level=education_level,
                department=department,
                teacher_instructions=teacher_instructions,
                previous_responses=previous_responses
            )
            
            if result:
                st.session_state.session_data['current_question'] = result
                st.session_state.session_data['total_questions'] += 1
                
                # Reset tracking for new question
                st.session_state.session_data['answer_start_time'] = time.time()
                st.session_state.session_data['hints_viewed'] = False
                
                # Store dos and don'ts
                if 'dos_and_donts' in result:
                    st.session_state.session_data['current_dos_donts'] = result['dos_and_donts']
                
                # Update knowledge gaps and suggestions
                if 'knowledge_gaps_detected' in result:
                    st.session_state.session_data['knowledge_gaps'].update(result['knowledge_gaps_detected'])
                if 'suggested_topics' in result:
                    st.session_state.session_data['suggested_topics'].update(result['suggested_topics'])
                
                # Update understanding
                if 'progress_assessment' in result:
                    st.session_state.session_data['current_understanding'] = int(result['progress_assessment'].get('current_understanding', 0))
                
                st.rerun()
    
    # Display current question
    if st.session_state.session_data['current_question']:
        question = st.session_state.session_data['current_question']
        
        st.markdown(f"""
        <div class='question-card'>
            <h3 style='color: #1e3a8a; margin-bottom: 1rem;'>📝 Question #{st.session_state.session_data['total_questions']}</h3>
            <p style='font-size: 1.2rem; line-height: 1.8; color: #1f2937;'>{question['question']}</p>
            <div style='margin-top: 1rem;'>
                <span style='background: #dbeafe; color: #1e40af; padding: 0.3rem 0.8rem; border-radius: 15px; margin-right: 1rem; font-size: 0.9rem;'>
                    Difficulty: {question.get('difficulty_level', 'medium').upper()}
                </span>
                <span style='background: #e0e7ff; color: #3730a3; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.9rem;'>
                    Testing: {question.get('concept_tested', 'General')}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Hints - track when viewed
        if question.get('hints'):
            with st.expander("💡 Need hints?"):
                st.session_state.session_data['hints_viewed'] = True
                for i, hint in enumerate(question['hints'], 1):
                    st.info(f"**Hint {i}:** {hint}")
        
        # Dos and Don'ts
        if question.get('dos_and_donts'):
            with st.expander("✅ Dos and Don'ts"):
                col_dos, col_donts = st.columns(2)
                with col_dos:
                    st.success("**✅ Do:**")
                    for do in question['dos_and_donts'].get('dos', []):
                        st.write(f"• {do}")
                with col_donts:
                    st.error("**❌ Don't:**")
                    for dont in question['dos_and_donts'].get('donts', []):
                        st.write(f"• {dont}")
        
        # Answer input
        student_answer = st.text_area(
            "Your Answer:",
            placeholder="Type your answer here...",
            height=150,
            key=f"answer_{st.session_state.session_data['total_questions']}"
        )
        
        # Submit button
        if st.button("✅ Submit Answer", type="secondary", use_container_width=True):
            if student_answer.strip():
                with st.spinner("Evaluating your answer..."):
                    # Calculate time taken
                    time_taken = time.time() - st.session_state.session_data.get('answer_start_time', time.time())
                    
                    # Prepare enriched previous responses
                    enriched_previous_responses = []
                    for qa in st.session_state.session_data['qa_history']:
                        enriched_previous_responses.append({
                            "question": qa.get('question', ''),
                            "answer": qa.get('answer', ''),
                            "score": str(qa.get('score', 0)),
                            "hints_used": qa.get('hints_used', False),
                            "time_taken": qa.get('time_taken', 0),
                            "dos_donts_provided": qa.get('dos_donts_provided', {}),
                            "learning_indicators": qa.get('learning_indicators', {}),
                            "teaching_effectiveness": qa.get('teaching_effectiveness', {})
                        })
                    
                    evaluation = call_evaluation_api(
                        question=question['question'],
                        student_answer=student_answer,
                        expected_points=question.get('expected_answer_points', []),
                        topic=topic,
                        student_history=student_history,
                        previous_responses=enriched_previous_responses,
                        hints_used=st.session_state.session_data.get('hints_viewed', False),
                        time_taken=time_taken,
                        dos_donts_provided=st.session_state.session_data.get('current_dos_donts', {})
                    )
                    
                    if evaluation:
                        score = int(evaluation.get('score', 0))
                        st.session_state.session_data['scores'].append(score)
                        
                        # Save to history with rich data
                        st.session_state.session_data['qa_history'].append({
                            "question": question['question'],
                            "answer": student_answer,
                            "score": score,
                            "hints_used": st.session_state.session_data.get('hints_viewed', False),
                            "time_taken": time_taken,
                            "dos_donts_provided": st.session_state.session_data.get('current_dos_donts', {}),
                            "learning_indicators": evaluation.get('learning_indicators', {}),
                            "teaching_effectiveness": evaluation.get('teaching_effectiveness', {}),
                            "concept_grasped": evaluation.get('learning_indicators', {}).get('grasped_concept', False),
                            "improvement_from_hints": evaluation.get('learning_indicators', {}).get('understood_hints', False)
                        })
                        
                        # Display score
                        if score >= 80:
                            st.markdown(f"<div class='score-excellent'>🎉 Excellent! Score: {score}%</div>", unsafe_allow_html=True)
                        elif score >= 60:
                            st.markdown(f"<div class='score-good'>👍 Good job! Score: {score}%</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='score-poor'>📚 Keep learning! Score: {score}%</div>", unsafe_allow_html=True)
                        
                        # Feedback
                        st.markdown(f"**Feedback:** {evaluation.get('feedback', 'No feedback available')}")
                        
                        # Additional details
                        col_detail1, col_detail2 = st.columns(2)
                        
                        with col_detail1:
                            if evaluation.get('missed_points'):
                                with st.expander("❌ Points you missed"):
                                    for point in evaluation['missed_points']:
                                        st.write(f"• {point}")
                        
                        with col_detail2:
                            if evaluation.get('misconceptions'):
                                with st.expander("⚠️ Common misconceptions"):
                                    for misc in evaluation['misconceptions']:
                                        st.write(f"• {misc}")
                        
                        # Show dos and don'ts assessment if available
                        if evaluation.get('dos_donts_assessment'):
                            assessment = evaluation['dos_donts_assessment']
                            if assessment.get('violated_donts'):
                                st.warning(f"⚠️ You violated these don'ts: {', '.join(assessment['violated_donts'])}")
                            if assessment.get('followed_dos'):
                                st.success(f"✅ Good job following: {', '.join(assessment['followed_dos'])}")
                        
                        # Update knowledge gaps
                        if evaluation.get('specific_gaps'):
                            st.session_state.session_data['knowledge_gaps'].update(evaluation['specific_gaps'])
            else:
                st.warning("Please write an answer before submitting!")

with side_col:
    st.markdown("### 📊 Progress")
    
    # Progress chart
    progress_chart = create_progress_chart()
    if progress_chart:
        st.plotly_chart(progress_chart, use_container_width=True)
    else:
        st.info("Complete questions to see progress")
    
    # Knowledge gaps
    if st.session_state.session_data['knowledge_gaps']:
        st.markdown("#### 🎯 Focus Areas")
        for gap in list(st.session_state.session_data['knowledge_gaps'])[:5]:
            st.markdown(f"• {gap}")
    
    # Suggested topics
    if st.session_state.session_data['suggested_topics']:
        st.markdown("#### 💡 Next Topics")
        for topic in list(st.session_state.session_data['suggested_topics'])[:3]:
            st.markdown(f"• {topic}")

# Footer
st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
col_footer1, col_footer2, col_footer3 = st.columns([2, 2, 1])

with col_footer1:
    st.markdown("**PES University** - Adaptive Learning Platform")

with col_footer3:
    if st.button("🔄 Reset Session"):
        st.session_state.session_data = {
            'qa_history': [],
            'current_question': None,
            'scores': [],
            'knowledge_gaps': set(),
            'suggested_topics': set(),
            'total_questions': 0,
            'current_understanding': 0,
            'debug_mode': st.session_state.session_data['debug_mode'],
            'answer_start_time': None,
            'hints_viewed': False,
            'current_dos_donts': {}
        }
        st.rerun()