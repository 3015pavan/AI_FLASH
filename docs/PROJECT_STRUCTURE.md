# 📁 Project Structure

```
AI-FLASHCARD-TUTOR/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
│
├── src/                        # Source code modules
│   ├── __init__.py
│   ├── generate.py             # Flashcard generation (full)
│   ├── generate_simple.py      # Flashcard generation (lightweight)
│   ├── quiz.py                 # Quiz generation and scoring
│   ├── dashboard.py            # Database and analytics
│   ├── pages_quiz.py           # Quiz page UI
│   ├── pages_dashboard.py      # Dashboard page UI
│   └── utils.py                # Utility functions
│
├── models/                     # AI models
│   └── flashcard_t5/           # T5 model for flashcard generation
│       ├── config.json
│       ├── metadata.json
│       └── README.md
│
├── data/                       # Application data
│   └── progress.db             # SQLite database (auto-created)
│
└── docs/                       # Documentation
    └── QUICK_START.md          # Quick start guide
```

## 📦 Core Components

### Main Application
- **app.py**: Entry point with Streamlit UI and navigation

### Source Modules (`src/`)
- **generate_simple.py**: Lightweight flashcard generator (production-ready)
- **generate.py**: Full-featured flashcard generator with ML
- **quiz.py**: MCQ quiz generation with smart distractors
- **dashboard.py**: Database management and progress analytics
- **pages_quiz.py**: Quiz page UI components
- **pages_dashboard.py**: Dashboard page UI with charts
- **utils.py**: Text processing and validation utilities

### Models (`models/`)
- **flashcard_t5/**: Fine-tuned T5 model for Q&A generation

### Data (`data/`)
- **progress.db**: SQLite database storing quiz attempts and metrics

### Documentation (`docs/`)
- Quick start guides and additional documentation

## 🔧 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main application with UI and navigation |
| `requirements.txt` | Python package dependencies |
| `README.md` | Comprehensive project documentation |
| `.gitignore` | Git ignore patterns |

## 🗄️ Database Schema

### Tables
- **quiz_attempts**: Individual quiz records with scores
- **global_metrics**: Aggregate learning statistics

## 🚀 Running the Application

From the project root:
```bash
streamlit run app.py
```

The application will automatically:
1. Load the T5 model from `models/flashcard_t5/`
2. Create/connect to `data/progress.db`
3. Initialize source modules from `src/`
