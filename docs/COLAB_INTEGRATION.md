# 🎓 Google Colab Integration Guide

## Overview
This guide explains how to run and demonstrate the AI Flashcard Tutor project in Google Colab for presentations, training, or remote access.

## 📋 Prerequisites
- Google Account with access to Colab
- GitHub repository (already available: puneeth-webdev218/AI-FLASHCARD-TUTOR)

---

## 🚀 Colab Notebook Structure

### Cell 1: Project Setup & Installation
```python
# Clone the repository
!git clone https://github.com/puneeth-webdev218/AI-FLASHCARD-TUTOR.git
%cd AI-FLASHCARD-TUTOR

# Install dependencies
!pip install -q transformers torch datasets scikit-learn numpy pandas streamlit tqdm PyPDF2 matplotlib plotly

# Install additional packages for Colab
!pip install -q pyngrok  # For exposing Streamlit app
```

### Cell 2: Verify Installation
```python
# Verify imports
import sys
import torch
import transformers
import streamlit
from pathlib import Path

print(f"✅ Python version: {sys.version}")
print(f"✅ PyTorch version: {torch.__version__}")
print(f"✅ Transformers version: {transformers.__version__}")
print(f"✅ Streamlit version: {streamlit.__version__}")
print(f"✅ CUDA available: {torch.cuda.is_available()}")
```

### Cell 3: Display Project Structure
```python
# Display project structure
!tree -L 2 -I '__pycache__|*.pyc'
# Or use: !find . -type f -name "*.py" | head -20
```

### Cell 4: Test Flashcard Generator
```python
# Add src to path
sys.path.insert(0, str(Path.cwd() / 'src'))

from generate_simple import FlashcardGenerator

# Create generator instance
generator = FlashcardGenerator(model_dir='models/flashcard_t5')

# Test with sample text
sample_text = """
Machine learning is a subset of artificial intelligence that provides systems 
the ability to automatically learn and improve from experience without being 
explicitly programmed. It focuses on computer programs that can access data and 
use it to learn for themselves.
"""

print("🎴 Generating flashcards...")
flashcards = generator.generate_flashcards(sample_text, num_flashcards=5)

# Display results
for idx, card in enumerate(flashcards, 1):
    print(f"\n{'='*60}")
    print(f"📌 Flashcard {idx}")
    print(f"{'='*60}")
    print(f"❓ Question: {card['question']}")
    print(f"✅ Answer: {card['answer']}")
```

### Cell 5: Test Quiz Generator
```python
from quiz import QuizGenerator

# Create quiz from flashcards
quiz_gen = QuizGenerator()
quiz_questions = quiz_gen.generate_quiz_questions(flashcards)

print(f"\n🎯 Generated {len(quiz_questions)} quiz questions:\n")

for idx, q in enumerate(quiz_questions, 1):
    print(f"\nQuestion {idx}: {q['question']}")
    for i, opt in enumerate(q['options']):
        marker = "✓" if i == q['correct_index'] else " "
        print(f"  [{marker}] {chr(65+i)}. {opt}")
```

### Cell 6: Test Database & Analytics
```python
from dashboard import ProgressDatabase
import pandas as pd

# Initialize database
db = ProgressDatabase()

# Create sample quiz attempt
db.save_quiz_attempt(
    topic="Machine Learning Basics",
    score_percentage=85.0,
    total_questions=10,
    correct_answers=8,
    incorrect_answers=2,
    time_taken_seconds=120,
    flashcards_used=10
)

# Get all attempts
attempts = db.get_all_attempts()
df = pd.DataFrame(attempts)
print("\n📊 Quiz Attempts:")
print(df)

# Get metrics
metrics = db.get_overall_metrics()
print(f"\n📈 Overall Metrics:")
print(f"  Total Flashcards: {metrics['total_flashcards']}")
print(f"  Total Quizzes: {metrics['total_quizzes']}")
print(f"  Average Score: {metrics['avg_score']:.2f}%")
```

### Cell 7: Launch Streamlit App (with ngrok)
```python
# Install and setup ngrok
!npm install -g localtunnel

# Run Streamlit in background
!streamlit run app.py &>/dev/null &

# Wait for server to start
import time
time.sleep(5)

# Expose with localtunnel
!lt --port 8501 --subdomain ai-flashcard-demo

print("\n✅ Streamlit app is running!")
print("📱 Access your app at the URL shown above")
print("⚠️ Keep this cell running to maintain the connection")
```

### Alternative Cell 7: Using Ngrok (Requires Auth Token)
```python
from pyngrok import ngrok
import threading

# Set your ngrok auth token (get from https://dashboard.ngrok.com/get-started/your-authtoken)
# ngrok.set_auth_token("YOUR_NGROK_TOKEN_HERE")

# Run Streamlit in background thread
def run_streamlit():
    !streamlit run app.py --server.port 8501 --server.headless true

thread = threading.Thread(target=run_streamlit)
thread.start()

# Wait for server to start
time.sleep(5)

# Create tunnel
public_url = ngrok.connect(8501)
print(f"\n✅ Streamlit app is running!")
print(f"🌐 Public URL: {public_url}")
print(f"⚠️ Keep this cell running to maintain the tunnel")
```

### Cell 8: Demo - Generate Flashcards from PDF
```python
from google.colab import files
import PyPDF2
import io

# Upload PDF file
print("📤 Upload a PDF file to generate flashcards:")
uploaded = files.upload()

# Extract text from PDF
for filename in uploaded.keys():
    pdf_file = io.BytesIO(uploaded[filename])
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + " "
    
    print(f"\n✅ Extracted {len(text)} characters from {filename}")
    
    # Generate flashcards
    print("\n🎴 Generating flashcards from PDF...")
    flashcards = generator.generate_flashcards(text[:1000], num_flashcards=8)
    
    # Display results
    for idx, card in enumerate(flashcards, 1):
        print(f"\n{'='*60}")
        print(f"📌 Flashcard {idx}")
        print(f"{'='*60}")
        print(f"❓ {card['question']}")
        print(f"✅ {card['answer']}")
```

### Cell 9: Export Results
```python
import json
from datetime import datetime

# Export flashcards to JSON
output_data = {
    "generated_at": datetime.now().isoformat(),
    "total_flashcards": len(flashcards),
    "flashcards": flashcards,
    "quiz_questions": quiz_questions if 'quiz_questions' in locals() else []
}

# Save to file
output_file = f"flashcards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=2)

# Download file
files.download(output_file)
print(f"✅ Downloaded: {output_file}")
```

### Cell 10: Cleanup
```python
# Stop Streamlit server
!pkill -f streamlit

# Kill ngrok tunnel
if 'ngrok' in locals():
    ngrok.kill()

print("✅ Cleanup complete")
```

---

## 📝 Complete Colab Notebook Template

Save this as `AI_Flashcard_Tutor_Demo.ipynb`:

```json
{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "gpuType": "T4"
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    },
    "accelerator": "GPU"
  },
  "cells": [
    {
      "cell_type": "markdown",
      "source": [
        "# 📚 AI Flashcard Tutor - Demo\n",
        "Interactive demonstration of AI-powered flashcard generation and quiz system.\n",
        "\n",
        "**Features:**\n",
        "- 🎴 AI-powered flashcard generation\n",
        "- 🎯 Concept-based MCQ quizzes\n",
        "- 📊 Progress tracking & analytics\n",
        "- 📄 PDF support\n",
        "- 💾 100% offline (after setup)"
      ],
      "metadata": {
        "id": "header"
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# Cell 1: Setup & Installation\n",
        "# ... (Copy Cell 1 code here)"
      ],
      "metadata": {
        "id": "setup"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}
```

---

## 🎯 Key Changes Needed for Colab

### 1. **Database Path** (Already done in your project)
```python
# In src/dashboard.py - already uses data/progress.db
DB_FILE = 'data/progress.db'
```

### 2. **Model Loading**
```python
# In src/generate_simple.py - already handles missing models gracefully
# No changes needed - falls back to demo mode
```

### 3. **File Uploads**
Add this helper to `src/utils.py`:
```python
def handle_colab_upload():
    """Handle file uploads in Google Colab"""
    try:
        from google.colab import files
        uploaded = files.upload()
        return uploaded
    except ImportError:
        return None  # Not in Colab
```

### 4. **Streamlit in Colab**
The main challenge is running Streamlit in Colab. Options:
- Use `pyngrok` for tunneling
- Use `localtunnel` for temporary URLs
- Run headless and interact via Python API only

---

## 🔍 Demonstration Flow

### For Presentations:
1. **Introduction** - Show project structure (Cell 3)
2. **Core Demo** - Generate flashcards (Cell 4)
3. **Quiz Demo** - Show MCQ generation (Cell 5)
4. **Analytics** - Display progress tracking (Cell 6)
5. **Live App** - Launch Streamlit (Cell 7)
6. **PDF Demo** - Upload and process PDF (Cell 8)

### For Training:
1. Start with setup (Cells 1-2)
2. Walk through each module individually (Cells 4-6)
3. Show full integration (Cell 7)
4. Let participants upload their own content (Cell 8)

---

## 📊 Comparison: Local vs Colab

| Feature | Local Setup | Google Colab |
|---------|------------|--------------|
| **Setup Time** | 5-10 min | 2-3 min |
| **GPU Access** | Depends on hardware | Free T4 GPU |
| **Persistence** | Permanent | Session-based |
| **Internet** | After setup, offline | Always required |
| **Sharing** | Deploy separately | Share notebook link |
| **Best For** | Production use | Demos, training |

---

## 🛠️ Troubleshooting Colab

### Issue: Streamlit won't start
```python
# Check if port is in use
!lsof -ti:8501 | xargs kill -9
!streamlit run app.py --server.port 8502
```

### Issue: Module not found
```python
# Ensure path is set
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))
```

### Issue: Database locked
```python
# Reset database
!rm -f data/progress.db
from dashboard import ProgressDatabase
db = ProgressDatabase()  # Creates new DB
```

---

## 📚 Additional Resources

- **Ngrok Setup**: https://dashboard.ngrok.com/get-started/setup
- **Streamlit in Colab**: https://discuss.streamlit.io/t/streamlit-on-colab/
- **Colab Guides**: https://colab.research.google.com/notebooks/

---

## ✅ Next Steps

1. Create the Colab notebook file
2. Test each cell individually
3. Add your ngrok auth token (if using ngrok)
4. Share the notebook link for demos
5. Consider creating a YouTube walkthrough

**Colab Notebook URL**: After creating, share via:
- File → Share → Get shareable link
- Add to GitHub README.md
