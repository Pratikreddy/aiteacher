# AI Teacher - Adaptive Learning Platform

An intelligent tutoring system that adapts to student knowledge levels using OpenAI's GPT-4o model. Built with Streamlit and LangServe.

## Features

- **Adaptive Questioning**: Questions adjust difficulty based on student performance
- **Knowledge Gap Detection**: Identifies weak areas, even from earlier education levels
- **Progress Tracking**: Visual charts showing learning progress over time
- **PES University Integration**: Department-specific subjects and topics
- **JSON Mode**: Structured responses from GPT-4o for consistent formatting
- **Real-time Evaluation**: Immediate feedback on student answers
- **Topic Suggestions**: Recommends related topics based on performance

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   - The `.env` file is already configured with your OpenAI API key
   - Make sure not to commit this file to version control

3. **Start the LangServe Backend**
   ```bash
   python server.py
   ```
   The server will start on http://localhost:8000

4. **Start the Streamlit Frontend**
   In a new terminal:
   ```bash
   streamlit run app.py
   ```
   The app will open in your browser at http://localhost:8501

## Usage

1. **Select Department**: Choose from PES University departments
2. **Choose Topic**: Select a predefined topic or enter a custom one
3. **Set Education Level**: From High School to PhD
4. **Add Student History**: Paste any historical performance data
5. **Teacher Instructions**: Optional special instructions for the AI
6. **Generate Questions**: Click to get adaptive questions
7. **Submit Answers**: Type your answer and get instant feedback
8. **Track Progress**: View performance charts and knowledge gaps

## Architecture

- **Backend**: FastAPI with LangServe for LLM orchestration
- **Frontend**: Streamlit for interactive UI
- **LLM**: OpenAI GPT-4o with JSON mode for structured responses
- **Visualization**: Plotly for progress tracking charts

## API Endpoints

- `/teacher/invoke`: Generate adaptive questions
- `/evaluate/invoke`: Evaluate student answers
- `/teacher/playground`: Interactive API testing
- `/docs`: API documentation

## Key Components

1. **Adaptive Question Generation**
   - Considers student history and education level
   - Adjusts difficulty based on performance
   - Identifies fundamental knowledge gaps

2. **Answer Evaluation**
   - Scores answers on a 0-100 scale
   - Provides detailed feedback
   - Identifies misconceptions
   - Suggests remedial topics

3. **Progress Tracking**
   - Line charts for score progression
   - Knowledge gap visualization
   - Strength and weakness analysis

## Notes

- The system can identify knowledge gaps from earlier grades (e.g., 9th grade math issues for engineering students)
- All responses are in JSON format for consistent parsing
- Session state is maintained for continuous learning experience