# 🎓 AI Flashcard Tutor

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.22+-red.svg)](https://streamlit.io/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-orange.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent flashcard generation system powered by **T5 Transformer** model. Automatically converts study materials into interactive flashcards and MCQ quizzes with comprehensive analytics tracking.

---

## 📋 Table of Contents

- [Features](#-features)
- [ML Pipeline Overview](#-ml-pipeline-overview)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Training](#-training)
- [Evaluation](#-evaluation)
- [Technology Stack](#-technology-stack)

---

## ✨ Features

### 🤖 **AI-Powered Generation**
- **Automatic Question Generation**: T5 transformer converts context into meaningful questions
- **Smart Answer Extraction**: Intelligent answer identification from text
- **Multi-format Support**: PDF, TXT, direct text input
- **Text Summarization**: Generate concise summaries of study material

### 🎯 **Interactive Quiz System**
- **MCQ Generation**: Concept-based multiple-choice questions
- **Smart Distractors**: Context-aware wrong answer generation
- **Real-time Scoring**: Instant feedback and performance tracking
- **Retake Capability**: Shuffle and retake quizzes anytime

### 📊 **Analytics Dashboard**
- **Progress Tracking**: Historical performance visualization
- **Topic Analysis**: Per-topic performance metrics
- **Learning Trends**: 30-day score trends with Plotly charts
- **Comprehensive Stats**: Global metrics, learning streaks, activity logs

### 💾 **Data Management**
- **SQLite Database**: Persistent quiz attempt storage
- **Session Management**: Streamlit session state for user data
- **Export Capabilities**: JSON export for flashcards
- **Privacy-First**: 100% local processing, no cloud APIs

---

## 🔬 ML Pipeline Overview

### **End-to-End Machine Learning Workflow**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ML PIPELINE ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────┘

1. DATA COLLECTION
   ├── SQuAD v1.1 Dataset (87,599 training examples)
   ├── Context-Question-Answer triplets
   └── Train/Val/Test split (80/10/10)

2. DATA PREPROCESSING
   ├── Text Tokenization (T5Tokenizer - SentencePiece)
   ├── Text-to-Text Format: "generate question: <context>"
   ├── Sequence Padding/Truncation (max_length=512)
   ├── Special Token Handling ([CLS], [SEP], [PAD])
   └── Token ID Conversion (vocabulary size: 32,128)

3. MODEL ARCHITECTURE (T5-base)
   ├── Encoder: 12 transformer layers
   │   ├── Multi-Head Self-Attention (8 heads)
   │   ├── Feed-Forward Networks
   │   └── Layer Normalization + Residual Connections
   │
   ├── Decoder: 12 transformer layers
   │   ├── Masked Self-Attention
   │   ├── Cross-Attention (to encoder)
   │   └── Feed-Forward Networks
   │
   ├── Hidden Dimensions: 512
   ├── Total Parameters: 220 million
   └── Pre-training: C4 dataset (750GB of text)

4. TRAINING (Supervised Fine-tuning)
   ├── Learning Type: Supervised Learning
   ├── Task: Sequence-to-Sequence Text Generation
   ├── Loss Function: Cross-Entropy (token-level classification)
   ├── Optimizer: AdamW (learning_rate=1e-4, weight_decay=0.01)
   ├── Scheduler: Linear warmup (500 steps) + decay
   ├── Batch Size: 16 (with gradient accumulation)
   ├── Epochs: 3-5
   ├── Regularization: Dropout (0.1), Gradient Clipping (1.0)
   └── Hardware: GPU (CUDA) recommended, CPU fallback

5. INFERENCE (Autoregressive Generation)
   ├── Decoding Strategy: Beam Search (num_beams=6)
   ├── Generation Process:
   │   ├── Encoder processes input context
   │   ├── Decoder generates tokens one-by-one
   │   ├── Each token = classification over 32k vocabulary
   │   └── Continues until [EOS] or max_length
   │
   ├── Hyperparameters:
   │   ├── Temperature: 0.7 (creativity control)
   │   ├── Top-p: 0.9 (nucleus sampling)
   │   ├── Repetition Penalty: 1.2
   │   └── Length Penalty: 1.0
   │
   └── Output: Variable-length question text

6. EVALUATION
   ├── Generation Quality Metrics:
   │   ├── BLEU Score (translation quality metric)
   │   ├── ROUGE-1/2/L (summarization metrics)
   │   └── Perplexity (language model confidence)
   │
   ├── Task-Specific Metrics:
   │   ├── Question Relevance (manual evaluation)
   │   ├── Answer Accuracy
   │   └── Fluency Assessment
   │
   └── Performance Metrics:
       ├── Training Loss Curve
       ├── Validation Loss
       └── Inference Speed (tokens/second)

7. DEPLOYMENT
   ├── Web Application: Streamlit
   ├── Model Serving: HuggingFace Transformers
   ├── Database: SQLite3 (analytics & progress tracking)
   ├── Document Processing: PyPDF2
   └── Visualization: Plotly + Matplotlib
```

### **ML Task Classification**

| Aspect | Classification |
|--------|---------------|
| **Learning Type** | Supervised Learning (Deep Learning) |
| **Task Category** | Sequence-to-Sequence (Seq2Seq) |
| **Architecture** | Transformer (Encoder-Decoder) |
| **Domain** | Natural Language Processing (NLP) |
| **Application** | Generative AI (Text Generation) |
| **Output Type** | Variable-length text sequences |
| **Training Method** | Transfer Learning + Fine-tuning |
| **Loss Function** | Cross-Entropy (token classification × sequence_length) |

**Key Insight**: This project uses **Classification** internally (32,128-class classification per token), but chains multiple classifications together autoregressively to generate complete sequences. This makes it **Sequence-to-Sequence Generation**, not traditional classification or regression.

---

## 📁 Project Structure

```
AI-FLASHCARD-TUTOR/
│
├── app.py                          # Main Streamlit application entry point
├── requirements.txt                # Python dependencies (production)
├── README.md                       # Comprehensive project documentation
├── .gitignore                      # Git ignore rules
│
├── config/                         # 🎛️ Configuration Management
│   ├── __init__.py                 # Module initialization
│   ├── config.yaml                 # Centralized configuration (YAML)
│   └── model_config.py             # Config loader & parser class
│
├── src/                            # 🔧 Source Code Modules
│   ├── __init__.py
│   │
│   ├── models/                     # 🤖 ML Model Components
│   │   ├── __init__.py
│   │   ├── generate_simple.py      # Lightweight flashcard generator
│   │   └── generate.py             # Full-featured generator (advanced)
│   │
│   ├── inference/                  # 🎯 Inference & Prediction
│   │   ├── __init__.py
│   │   └── quiz.py                 # Quiz generation & MCQ logic
│   │
│   ├── features/                   # 📊 Application Features
│   │   ├── __init__.py
│   │   ├── dashboard.py            # Database operations & analytics
│   │   ├── pages_quiz.py           # Quiz UI page components
│   │   └── pages_dashboard.py      # Analytics UI page components
│   │
│   ├── utils/                      # 🛠️ Utility Functions
│   │   ├── __init__.py
│   │   └── utils.py                # Helper functions
│   │
│   └── training/                   # 🎓 Training Utilities (future)
│       └── __init__.py
│
├── scripts/                        # 📜 ML Pipeline Scripts
│   ├── train.py                    # Training/fine-tuning script (SQuAD)
│   └── evaluate.py                 # Evaluation script (BLEU, ROUGE)
│
├── models/                         # 💾 Saved Models & Checkpoints
│   └── flashcard_t5/               # Fine-tuned T5 model directory
│       ├── config.json             # Model architecture configuration
│       ├── metadata.json           # Training metadata & hyperparameters
│       ├── README.md               # Model-specific documentation
│       └── pytorch_model.bin       # Model weights (~440MB)
│
├── data/                           # 📂 Data Storage
│   ├── progress.db                 # SQLite database (quiz attempts, metrics)
│   ├── cache/                      # Cached data (tokenized inputs, etc.)
│   ├── raw/                        # Raw datasets (SQuAD, custom)
│   └── processed/                  # Processed/preprocessed data
│
├── notebooks/                      # 📓 Jupyter Notebooks
│   └── (exploratory data analysis, model experiments)
│
├── docs/                           # 📚 Documentation
│   ├── QUICK_START.md              # Quick installation & usage guide
│   ├── PROJECT_STRUCTURE.md        # Detailed structure explanation
│   └── COLAB_INTEGRATION.md        # Google Colab integration guide
│
└── tests/                          # ✅ Unit Tests (future)
    └── __init__.py
```

### **Directory Purpose Table**

| Directory | Purpose | Key Responsibilities |
|-----------|---------|---------------------|
| `config/` | Configuration management | Centralized settings, hyperparameters, paths |
| `src/models/` | ML model loading & inference | T5 model, tokenizer, generation logic |
| `src/inference/` | Prediction & generation | Quiz creation, question generation |
| `src/features/` | Application functionality | UI components, database operations |
| `src/utils/` | Helper functions | Text processing, file I/O, utilities |
| `scripts/` | ML pipeline execution | Training, evaluation, data processing |
| `models/` | Model storage | Checkpoints, fine-tuned weights |
| `data/` | Data management | Database, datasets, cache |
| `notebooks/` | Experimentation | EDA, prototyping, analysis |
| `docs/` | Documentation | Guides, explanations, API docs |
| `tests/` | Quality assurance | Unit tests, integration tests |

---

## 🚀 Installation

### **Prerequisites**
- **Python**: 3.8 or higher
- **pip**: Latest version
- **(Optional)** CUDA-enabled GPU for training (CPU works for inference)

### **Step 1: Clone Repository**
```bash
git clone https://github.com/puneeth-webdev218/AI-FLASHCARD-TUTOR.git
cd AI-FLASHCARD-TUTOR
```

### **Step 2: Install Dependencies**

**For Application Use (Inference Only):**
```bash
pip install -r requirements.txt
```

**For Training & Development:**
```bash
# Install core dependencies
pip install -r requirements.txt

# Install training-specific packages
pip install datasets transformers[torch] nltk rouge-score pyyaml

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### **Step 3: Verify Installation**
```bash
python -c "import streamlit, torch, transformers; print('✅ All dependencies installed')"
```

---

## 💻 Usage

### **Running the Application**

```bash
# Start Streamlit app
streamlit run app.py

# Custom port
streamlit run app.py --server.port 8502

# Headless mode (server deployment)
streamlit run app.py --server.headless true
```

The app will open automatically at `http://localhost:8501`

### **Using the Interface**

#### **1️⃣ Generate Flashcards**
1. Navigate to **"📝 Flashcard Generator"** tab
2. Choose input method:
   - **Paste Text**: Copy-paste study material
   - **Upload PDF**: Click "Browse files" and select PDF
3. Adjust settings in sidebar:
   - Number of flashcards (1-10)
   - Beam search quality (3-8)
4. Click **"✨ Generate Flashcards"**
5. Review generated flashcards:
   - Click card to flip (Question ↔ Answer)
   - Download as JSON (optional)

#### **2️⃣ Take MCQ Quiz**
1. Generate ≥4 flashcards first (required)
2. Navigate to **"🎯 Take Quiz"** tab
3. Select number of questions (4-10)
4. Click **"Start Quiz"**
5. Answer multiple-choice questions
6. Click **"Submit Quiz"** to view:
   - Score percentage
   - Correct/incorrect breakdown
   - Time taken
   - Detailed explanations
7. Click **"Retake Quiz"** to shuffle and retry

#### **3️⃣ View Analytics Dashboard**
1. Navigate to **"📊 Progress Dashboard"** tab
2. Review key metrics:
   - **KPI Cards**: Total flashcards, quizzes taken, average score, learning streak
   - **Score Trend**: 30-day line chart (interactive Plotly)
   - **Topic Performance**: Bar chart by subject
   - **Answer Distribution**: Pie chart (correct vs incorrect)
   - **Activity Log**: Detailed quiz history table
3. Use **"Refresh Dashboard"** button to update
4. **Clear Data** (if needed) from settings

---

## 🎓 Training

### **Training Your Own Model**

```bash
# Basic training (uses config.yaml defaults)
python scripts/train.py

# Custom hyperparameters
python scripts/train.py \
    --model_name t5-base \
    --epochs 5 \
    --batch_size 16 \
    --learning_rate 0.0001 \
    --save_dir models/my_flashcard_model

# Quick test run (limited samples)
python scripts/train.py --epochs 1 --max_samples 1000

# Advanced: Custom dataset
python scripts/train.py \
    --epochs 5 \
    --batch_size 8 \
    --learning_rate 5e-5 \
    --save_dir models/custom_t5 \
    --max_samples 10000
```

### **Training Parameters Explained**

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `--model_name` | `t5-base` | t5-small, base, large | Base T5 model to fine-tune |
| `--epochs` | `3` | 1-10 | Number of training passes |
| `--batch_size` | `16` | 4-32 | Samples per batch (adjust for GPU memory) |
| `--learning_rate` | `1e-4` | 1e-5 to 1e-3 | AdamW learning rate |
| `--max_samples` | `None` | Any int | Limit training samples (for testing) |
| `--save_dir` | `models/flashcard_t5_finetuned` | Any path | Checkpoint save directory |

### **Configuration File (config.yaml)**

Edit `config/config.yaml` to adjust:

```yaml
training:
  batch_size: 16
  learning_rate: 0.0001
  num_epochs: 5
  warmup_steps: 500
  weight_decay: 0.01
  gradient_accumulation_steps: 2
  max_grad_norm: 1.0

model:
  generation:
    num_beams: 6
    temperature: 0.7
    top_p: 0.9
    repetition_penalty: 1.2
```

### **Training Output**

```
Epoch 1/5
Training: 100%|██████████| 5475/5475 [1:23:45<00:00, loss=2.1234, lr=9.8e-05]
Validation Loss: 1.9876
Model saved to models/flashcard_t5_finetuned/checkpoint-epoch-1

Epoch 2/5
Training: 100%|██████████| 5475/5475 [1:22:18<00:00, loss=1.8765, lr=8.2e-05]
...
Training complete! Final model saved to models/flashcard_t5_finetuned
```

---

## 📊 Evaluation

### **Evaluate Model Performance**

```bash
# Basic evaluation
python scripts/evaluate.py --model_path models/flashcard_t5_finetuned

# With sample generation examples
python scripts/evaluate.py \
    --model_path models/flashcard_t5_finetuned \
    --show_examples \
    --num_examples 10

# Limited evaluation (faster)
python scripts/evaluate.py \
    --model_path models/flashcard_t5_finetuned \
    --max_samples 500

# Full evaluation on test set
python scripts/evaluate.py \
    --model_path models/flashcard_t5_finetuned \
    --split validation \
    --max_samples 2000
```

### **Evaluation Metrics Explained**

| Metric | Range | Interpretation | Good Score |
|--------|-------|----------------|------------|
| **BLEU** | 0-1 | Translation/generation quality (word overlap) | >0.3 |
| **ROUGE-1** | 0-1 | Unigram overlap with reference | >0.4 |
| **ROUGE-2** | 0-1 | Bigram overlap (fluency) | >0.2 |
| **ROUGE-L** | 0-1 | Longest common subsequence | >0.35 |
| **Perplexity** | 1-∞ | Model confidence (lower is better) | <50 |

### **Sample Evaluation Output**

```
============================================================
EVALUATION RESULTS
============================================================
Number of samples: 1000

BLEU Score:
  Mean:  0.3245 ± 0.1234
  Range: [0.0823, 0.7654]

ROUGE Scores:
  ROUGE-1: 0.4123 ± 0.0987
  ROUGE-2: 0.2345 ± 0.0654
  ROUGE-L: 0.3876 ± 0.0876
============================================================

Example 1:
Context: Photosynthesis is the process by which plants...
Reference: What is photosynthesis?
Generated: What process do plants use to convert light?
------------------------------------------------------------
```

---

## 🛠 Technology Stack

### **Machine Learning & NLP**
| Technology | Version | Purpose |
|------------|---------|---------|
| **PyTorch** | 2.0+ | Deep learning framework (GPU acceleration) |
| **Transformers** | 4.30+ | HuggingFace model library (T5 implementation) |
| **T5 Model** | Base (220M params) | Text-to-Text Transfer Transformer |
| **SQuAD Dataset** | v1.1 | 87,599 question-answer pairs for training |
| **NLTK** | 3.8+ | Natural language processing utilities |
| **Datasets** | 2.0+ | HuggingFace dataset loading |

### **Web Application**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Streamlit** | 1.22+ | Interactive web UI framework |
| **Plotly** | 5.0+ | Interactive data visualizations |
| **Matplotlib** | 3.7+ | Static plotting |

### **Data Processing**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Pandas** | 2.0+ | Data manipulation & analysis |
| **NumPy** | 1.24+ | Numerical computing |
| **PyPDF2** | 3.0+ | PDF text extraction |
| **SQLite3** | Built-in | Embedded database (no server needed) |

### **Development Tools**
| Technology | Purpose |
|------------|---------|
| **PyYAML** | Configuration file parsing |
| **pathlib** | Cross-platform file path handling |
| **logging** | Application logging |
| **tqdm** | Progress bars for training |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/AmazingFeature`
3. **Commit** changes: `git commit -m 'Add AmazingFeature'`
4. **Push** to branch: `git push origin feature/AmazingFeature`
5. **Open** Pull Request

**Contribution Areas:**
- 🐛 Bug fixes
- ✨ New features (e.g., spaced repetition)
- 📝 Documentation improvements
- 🧪 Unit tests
- 🎨 UI enhancements
- 🚀 Performance optimizations

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Puneeth** - *Initial Development* - [GitHub](https://github.com/puneeth-webdev218)

---

## 🙏 Acknowledgments

- **Google Research**: T5 model architecture and pre-training
- **Stanford NLP Group**: SQuAD dataset creation
- **HuggingFace**: Transformers library and model hub
- **Streamlit Team**: Excellent web framework for ML apps
- **PyTorch Community**: Deep learning framework

---

## 📧 Contact & Support

**For Questions or Issues:**
- 📮 GitHub Issues: [Create Issue](https://github.com/puneeth-webdev218/AI-FLASHCARD-TUTOR/issues)
- 📧 Email: [Your Email]
- 💬 Discussions: [GitHub Discussions](https://github.com/puneeth-webdev218/AI-FLASHCARD-TUTOR/discussions)

**Response Time:** Usually within 24-48 hours

---

## 🔗 Useful Links

### **Research Papers**
- [T5 Paper (2019)](https://arxiv.org/abs/1910.10683) - "Exploring the Limits of Transfer Learning"
- [Attention Is All You Need (2017)](https://arxiv.org/abs/1706.03762) - Original Transformer paper
- [SQuAD Paper (2016)](https://arxiv.org/abs/1606.05250) - Stanford Question Answering Dataset

### **Documentation**
- [HuggingFace Transformers Docs](https://huggingface.co/docs/transformers)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [SQuAD Explorer](https://rajpurkar.github.io/SQuAD-explorer/)

### **Model Hub**
- [T5 on HuggingFace](https://huggingface.co/t5-base)
- [Pre-trained Models](https://huggingface.co/models)

---

## 📈 Roadmap

### **Version 2.0 (Planned)**
- [ ] 🔄 Spaced repetition algorithm (Anki-style)
- [ ] 🌍 Multi-language support (mT5 integration)
- [ ] 🎯 Adaptive difficulty adjustment
- [ ] 📱 Mobile-responsive UI
- [ ] 🔗 Export to Anki format
- [ ] 🤝 Collaborative study sessions
- [ ] 📊 Advanced analytics (confusion matrices)
- [ ] 🎨 Custom themes & branding

### **Version 1.5 (In Progress)**
- [x] ✅ Structured ML project layout
- [x] ✅ Training & evaluation scripts
- [x] ✅ Comprehensive documentation
- [ ] 🧪 Unit test coverage
- [ ] 🐳 Docker containerization
- [ ] 📦 PyPI package release

---

## 🎯 Use Cases

### **Students**
- Convert lecture notes → flashcards
- Generate practice questions from textbooks
- Track learning progress across subjects
- Prepare for exams with MCQ quizzes

### **Educators**
- Create quizzes for students automatically
- Generate study materials from lesson plans
- Assess understanding with analytics
- Save time on quiz creation

### **Professionals**
- Continuous learning & skill development
- Certification exam preparation
- Knowledge retention tracking
- Onboarding material creation

### **Researchers**
- Literature review flashcards
- Methodology Q&A cards
- Conference presentation prep
- Paper concept reinforcement

---

## ⚠️ Limitations & Known Issues

### **Current Limitations**
- **Context Length**: Max 512 tokens input (T5 limitation)
- **Language**: English only (use mT5 for multilingual)
- **GPU Memory**: Training requires ~8GB VRAM for T5-base
- **Generation Time**: 2-5 seconds per flashcard (CPU mode)

### **Known Issues**
- Large PDFs (>50 pages) may cause extraction lag
- Very technical/domain-specific text may generate generic questions
- Database locked error if multiple sessions access simultaneously

### **Workarounds**
- Split large documents into chunks
- Provide more context for better question quality
- Use only one Streamlit session per database

---

## 🔐 Privacy & Security

### **Data Privacy**
✅ **100% Local Processing** - All ML inference runs on your machine  
✅ **No Cloud APIs** - No data sent to external services  
✅ **No Telemetry** - Zero usage tracking or analytics  
✅ **Offline Capable** - Works without internet (after initial setup)  

### **Data Storage**
📁 **SQLite Database** (`data/progress.db`)
- Quiz attempts with timestamps
- Global learning metrics
- No personally identifiable information
- Easily deletable (just remove file)

📄 **Temporary Files**
- PDF uploads stored in memory (not saved)
- Cache cleared on session end

---

## 🚀 Performance Optimization

### **For Faster Inference**
```python
# In config/config.yaml
model:
  generation:
    num_beams: 3  # Reduce from 6 (faster, slightly lower quality)
```

### **For Better Quality**
```python
model:
  generation:
    num_beams: 8  # Increase from 6 (slower, better quality)
    temperature: 0.5  # Lower = more conservative/accurate
```

### **GPU Acceleration**
```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 📝 FAQ

**Q: How long does training take?**  
A: On GPU (RTX 3080): ~2-3 hours for 5 epochs on full SQuAD. On CPU: 24+ hours.

**Q: Can I use a different model?**  
A: Yes! Edit `config.yaml` to use `t5-small` (faster) or `t5-large` (better quality).

**Q: How accurate are generated flashcards?**  
A: Depends on input quality. Structured, detailed text → better results. BLEU scores typically 0.3-0.4.

**Q: Can I export my progress?**  
A: Flashcards export as JSON. Progress data in `data/progress.db` (SQLite).

**Q: Does it work offline?**  
A: Yes! After initial model download, fully offline.

**Q: Can I add my own training data?**  
A: Yes! Modify `scripts/train.py` to load custom datasets.

**Q: What if quiz questions are too hard?**  
A: Provide more detailed context in input. Adjust `num_beams` to 4-5 for balanced difficulty.

---

## 🛠 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: transformers` | Run `pip install transformers torch` |
| "Not enough flashcards for quiz" | Generate ≥4 flashcards before taking quiz |
| Database locked error | Close other Streamlit sessions |
| Out of memory during training | Reduce `batch_size` to 8 or 4 |
| Slow generation | Use GPU or reduce `num_beams` |
| PDF extraction fails | Try converting PDF to TXT first |
| Dashboard shows no data | Take at least one quiz to populate data |

---

**🎓 Ready to transform your learning?**

```bash
streamlit run app.py
```

**Then visit:** [http://localhost:8501](http://localhost:8501)

---

**Made with ❤️ and 🤖 by AI Enthusiasts**

*Powered by Transformers, PyTorch, and Streamlit*
