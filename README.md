# 🎯 Vetri AI Interview Coach

An AI-powered interview preparation platform that generates personalized questions, evaluates answers in real-time, and provides comprehensive feedback using Google's Gemini AI.

---

## ✨ Features

- **Personalized Question Generation** - AI generates questions based on your job role, experience level, and skills
- **Real-time Answer Evaluation** - Instant AI-powered evaluation with scores from 0-100
- **Detailed Feedback** - Get strengths, areas for improvement, and suggested answers
- **Multiple Interview Types** - HR, Technical, and Mixed interview modes
- **Difficulty Levels** - Easy, Medium, and Hard question difficulties
- **Progress Tracking** - Visual progress bar showing interview completion
- **Comprehensive Reports** - Overall score, performance analysis, and personalized learning recommendations
- **Modern User Interface** - Clean, responsive design with smooth animations
- **Mobile Responsive** - Works perfectly on all devices

---

## 🛠️ Tech Stack

- **Backend**: Flask 2.3.3 (Python)
- **AI**: Google Gemini AI (gemini-pro)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Deployment**: Render.com with Gunicorn
- **Static Files**: WhiteNoise

---

## 📁 Project Structure
vetri-ai-interview-coach/
├── backend/
│ ├── app.py # Main Flask application
│ ├── wsgi.py # WSGI entry point
│ ├── requirements.txt # Python dependencies
│ ├── utils/
│ │ ├── gemini_helper.py # Gemini API integration
│ │ └── interview_generator.py
│ └── models/
│ └── interview.py # Data models
├── frontend/
│ ├── index.html
│ ├── style.css
│ └── script.js
├── venv/ # Virtual environment
├── .env # Environment variables
├── .gitignore
├── render.yaml # Render deployment config
└── README.md

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- Git
- Google Gemini API Key

### Local Setup

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/vetri-ai-interview-coach.git
cd vetri-ai-interview-coach