# AI Teacher - Project Summary

## Overview
AI Teacher is an adaptive learning platform that uses OpenAI's GPT-4o model to provide personalized education. It dynamically adjusts question difficulty based on student performance and identifies knowledge gaps, even from earlier education levels.

## Project Structure
```
aiteacher/
├── .env.example          # Example environment variables
├── .gitignore           # Git ignore file
├── README.md            # Project documentation
├── app.py               # Streamlit frontend (600+ lines)
├── models.py            # Pydantic data models
├── requirements.txt     # Python dependencies
├── server.py            # FastAPI/LangServe backend (300+ lines)
├── test_api.py          # API test file
└── test_second_question.py # Additional test file
```

## Key Components

### Frontend (app.py)
- **Framework**: Streamlit
- **Features**:
  - PES University branded UI with custom CSS
  - Interactive question-answer interface
  - Real-time progress tracking with Plotly charts
  - Session state management
  - Knowledge gap visualization
  - Performance metrics dashboard

### Backend (server.py)
- **Framework**: FastAPI with LangServe
- **Endpoints**:
  - `/teacher/invoke` - Generate adaptive questions
  - `/evaluate/invoke` - Evaluate student answers
  - `/teacher/playground` - Interactive API testing
  - `/docs` - API documentation
- **LLM Integration**: OpenAI GPT-4o with JSON mode

### Data Models (models.py)
- **StudentProfile**: Comprehensive student tracking
- **Question**: Question metadata and difficulty
- **Answer**: Student responses and evaluation
- **LearningSession**: Session-based learning data
- **ConceptMastery**: Topic-wise mastery tracking
- **AnalyticsData**: Performance analytics

## Core Functionality

### Adaptive Learning Algorithm
1. **Initial Assessment**: Starts with medium difficulty
2. **Performance Tracking**: Monitors scores and response patterns
3. **Difficulty Adjustment**: 
   - Score > 80%: Increase difficulty
   - Score < 50%: Decrease difficulty
   - 50-80%: Maintain current level
4. **Knowledge Gap Detection**: Identifies weak areas from any education level
5. **Remedial Suggestions**: Recommends topics for improvement

### Question Generation
- Context-aware questions based on:
  - Student history
  - Education level
  - Department (PES University specific)
  - Previous responses in session
  - Teacher instructions

### Answer Evaluation
- Scores on 0-100 scale
- Identifies correct/missed points
- Detects misconceptions
- Provides detailed feedback
- Suggests next topics

## Technical Stack
- **Frontend**: Streamlit 1.46.1
- **Backend**: FastAPI 0.115.6, LangServe 0.3.1
- **LLM**: OpenAI GPT-4o (via langchain-openai)
- **Visualization**: Plotly 5.24.1
- **Data Processing**: Pandas, NumPy
- **Environment**: Python with dotenv

## Deployment
- **Backend Server**: Runs on http://localhost:8000
- **Frontend App**: Runs on http://localhost:8501
- **GitHub Repository**: https://github.com/Pratikreddy/aiteacher

## Security
- API keys stored in .env (not committed)
- CORS enabled for development
- .gitignore configured for Python projects

## Usage Flow
1. Select department and topic
2. Set education level
3. Add optional student history
4. Generate adaptive question
5. Submit answer
6. Receive evaluation and feedback
7. View progress charts
8. Get next question (adjusted difficulty)

## Future Enhancements
- Multi-language support
- Voice interaction
- Collaborative learning
- Mobile app
- Advanced analytics dashboard
- Integration with LMS systems