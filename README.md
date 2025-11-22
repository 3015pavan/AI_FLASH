# 📚 AI Flashcard Generator

A comprehensive AI-powered study platform with flashcard generation, MCQ quizzes, and learning analytics.

## ✨ Features

### 🎴 Flashcard Generation
- **Multiple Input Methods**: Paste text, upload PDF, or use examples
- **AI-Powered**: T5 model generates contextual Q&A pairs
- **Summary Generation**: Get key points from study material
- **Interactive UI**: Flip cards with smooth animations
- **Export**: Download flashcards as JSON

### 🎯 MCQ Quiz System
- **Concept-Based Questions**: Tests understanding, not verbatim repetition
- **Smart Distractors**: Wrong options from related flashcards
- **Immediate Feedback**: See explanations with correct answers
- **Quiz Analytics**: Score, time, answer breakdown
- **Retake Quizzes**: Shuffle options anytime

### 📊 Progress Dashboard
- **Learning Metrics**: Flashcards generated, quizzes taken, average score, learning streak
- **Visual Analytics**: 
  - Score trend (30-day chart)
  - Performance by topic
  - Correct vs incorrect distribution
- **Detailed Activity Log**: All quiz attempts with timestamps
- **Local Database**: SQLite storage (100% offline)

## 🚀 Quick Start

### Installation
```bash
cd ai_flashcard_generator
pip install -r requirements.txt
streamlit run app.py
```

### Open in Browser
```
http://localhost:8501
```

## 📖 How to Use

### 1️⃣ Generate Flashcards
1. Enter text or upload PDF
2. Click **✨ Generate Flashcards**
3. Flip cards to review
4. Download as JSON (optional)

### 2️⃣ Take MCQ Quiz
1. Generate ≥4 flashcards first
2. Go to **Take Quiz** in sidebar
3. Answer concept-based MCQs
4. View score and explanations

### 3️⃣ Monitor Progress
1. Click **Progress Dashboard**
2. View KPI cards and charts
3. Track learning trends
4. Analyze topic performance

## 📁 File Structure

```
├── app.py                 # Main app with navigation
├── generate_simple.py     # Flashcard generation
├── quiz.py                # MCQ generation & scoring
├── dashboard.py           # Database & analytics
├── pages_quiz.py          # Quiz page UI
├── pages_dashboard.py     # Dashboard page UI
├── requirements.txt       # Dependencies
└── progress.db            # SQLite database (auto-created)
```

## 🗄️ Database Schema

### quiz_attempts Table
```sql
id, date, topic, score_percentage, total_questions, 
correct_answers, incorrect_answers, time_taken_seconds, flashcards_used
```

### global_metrics Table
```sql
total_flashcards_generated, total_quizzes_taken, 
highest_score, last_quiz_date
```

## ⚙️ Configuration

### Sidebar Settings
- **Number of Flashcards**: 6-15 (default: 10)
- **Beam Search Quality**: 3-8 (higher = better quality, slower)

### Advanced Options
- Refresh Dashboard
- Clear all data

## 📊 Key Metrics

- **Average Score**: Calculated from all quiz attempts
- **Learning Streak**: Consecutive days with quizzes
- **Score Trend**: Daily average over last 30 days
- **Topic Stats**: Best/worst score by topic

## 🎯 Example Workflow

```
1. Paste machine learning concepts
   ↓
2. Generate 10 flashcards
   ↓
3. Review and flip cards
   ↓
4. Take MCQ quiz (85% score)
   ↓
5. View progress dashboard
   ↓
6. Retake next day to build streak
```

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Not enough flashcards for quiz" | Generate ≥4 flashcards first |
| Quiz not showing | No flashcards in session - generate first |
| Dashboard empty | Take quiz first to populate data |
| Database error | Delete `progress.db` and restart |

## 📦 Dependencies

- streamlit (web framework)
- PyTorch (ML computations)
- Transformers (T5 model)
- PyPDF2 (PDF extraction)
- plotly/matplotlib (charts)
- pandas (data handling)

## 🔐 Privacy

✅ **100% Local** - All processing offline  
✅ **No APIs** - No cloud uploads  
✅ **SQLite DB** - Data in `progress.db` only  
✅ **Open Source** - Full transparency  

## 📊 Performance Tips

- Use 10-12 flashcards for optimal quiz experience
- Provide detailed, well-structured text
- Review before taking quiz
- Retake after 24 hours to reinforce

## 🚀 Advanced Usage

### Custom Quiz Topic
```python
# In app.py, modify before starting quiz
st.session_state.current_topic = "Your Topic Name"
```

### Export Progress Data
```bash
# View database
sqlite3 progress.db "SELECT * FROM quiz_attempts;"
```

## 📝 Future Enhancements

- [ ] Spaced repetition algorithm
- [ ] AI-powered difficulty adjustment
- [ ] Multi-language support
- [ ] Collaborative features
- [ ] Mobile app

## ❓ FAQ

**Q: Can I use this offline?**  
A: Yes, completely offline after initial setup.

**Q: How accurate are generated flashcards?**  
A: Depends on input quality. Longer, structured text = better results.

**Q: Can I export progress?**  
A: Flashcards export as JSON. Progress is in SQLite `progress.db`.

**Q: What if quiz questions are too hard?**  
A: Add more context to input text. Use Beam Search quality 4-5 instead.

## 🤝 Contributing

Found issues? Have improvements? Submit feedback or contributions!

## 📞 Support

For issues:
1. Check Troubleshooting section
2. Verify all dependencies installed
3. Restart Streamlit server
4. Delete `progress.db` if database errors

---

**Ready to learn? Start with:** `streamlit run app.py`  
**Then visit:** http://localhost:8501

🎓 **Happy Learning!** 📚✨
