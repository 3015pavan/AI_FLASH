"""
AI Flashcard Generator - Main Streamlit App with Navigation
Includes flashcard generation, MCQ quiz, and progress dashboard
"""

import json
import logging
from pathlib import Path
import streamlit as st
import PyPDF2
import io
from datetime import datetime

try:
    from generate_simple import FlashcardGenerator
except:
    try:
        from generate import FlashcardGenerator
    except:
        FlashcardGenerator = None

from quiz import QuizGenerator
from dashboard import create_progress_database
from pages_quiz import show_quiz_page
from pages_dashboard import show_dashboard_page

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .flashcard {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 30px;
        margin: 20px 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 18px;
        font-weight: 500;
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .flashcard:hover {
        transform: scale(1.02);
    }
    
    .flashcard-flipped {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .stats-box {
        background: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #667eea;
    }
    
    .success-box {
        background: #d4edda;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #28a745;
        color: #155724;
    }
    
    .warning-box {
        background: #fff3cd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #ffc107;
        color: #856404;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_generator():
    """
    Load the flashcard generator (cached).
    Always returns a working generator in demo mode.
    """
    try:
        return FlashcardGenerator(model_dir='flashcard_t5')
    except Exception as e:
        st.info("Running in demo mode - sample flashcards available")
        return FlashcardGenerator()


def extract_pdf_text(pdf_file) -> str:
    """
    Extract text from PDF file.
    
    Args:
        pdf_file: Uploaded PDF file object
        
    Returns:
        Extracted text from PDF
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + " "
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""


def display_flashcard(question: str, answer: str, index: int):
    """
    Display a single flashcard with flip animation.
    
    Args:
        question: Question text
        answer: Answer text
        index: Flashcard index
    """
    
    # Initialize session state for flip state
    flip_key = f'flipped_{index}'
    if flip_key not in st.session_state:
        st.session_state[flip_key] = False
    
    # Create columns for button and card
    col1, col2 = st.columns([1, 10])
    
    # Flip button in left column
    with col1:
        if st.button(
            "🔄",
            key=f'flip_btn_{index}',
            help="Click to flip the card"
        ):
            st.session_state[flip_key] = not st.session_state[flip_key]
    
    # Flashcard display in right column
    with col2:
        is_flipped = st.session_state[flip_key]
        
        if is_flipped:
            # Show answer (red/pink side)
            st.markdown(
                f'''
                <div style="
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    border-radius: 10px;
                    padding: 30px;
                    margin: 20px 0;
                    color: white;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    min-height: 200px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    font-weight: 500;
                    text-align: center;
                ">
                    <div>
                        <strong style="color: white; font-size: 16px;">ANSWER:</strong>
                        <br><br>
                        {answer}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
        else:
            # Show question (purple side)
            st.markdown(
                f'''
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px;
                    padding: 30px;
                    margin: 20px 0;
                    color: white;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    min-height: 200px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    font-weight: 500;
                    text-align: center;
                ">
                    <div>
                        <strong style="color: #ffd700; font-size: 16px;">Q{index + 1}:</strong>
                        <br><br>
                        {question}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )


def download_flashcards_json(flashcards: list):
    """
    Create a download button for flashcards as JSON.
    
    Args:
        flashcards: List of flashcard dictionaries
    """
    json_data = json.dumps(flashcards, indent=2)
    
    st.download_button(
        label="📥 Download as JSON",
        data=json_data,
        file_name="flashcards.json",
        mime="application/json",
        key='download_json'
    )


def show_flashcard_generator():
    """Display the flashcard generator page."""
    
    # Header
    st.markdown("# 📚 AI Flashcard Generator")
    st.markdown(
        "Transform your notes and text into interactive flashcards using AI! "
        "Our trained model generates questions and answers automatically."
    )
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        num_flashcards = st.slider(
            "Number of Flashcards",
            min_value=6,
            max_value=15,
            value=10,
            step=1,
            help="Target number of flashcards to generate"
        )
        
        num_beams = st.select_slider(
            "Beam Search (Quality)",
            options=[3, 4, 5, 6, 8],
            value=6,
            help="Higher value = better quality but slower generation"
        )
        
        st.markdown("---")
        st.markdown("### 📖 About")
        st.info(
            "This tool uses a fine-tuned T5 model trained on SQuAD v1.1 "
            "to generate high-quality flashcards from your text. "
            "All processing happens offline with no external APIs."
        )
    
    # Main content
    st.markdown("## 📝 Input Text")
    
    # Text input options
    input_method = st.radio(
        "Choose input method:",
        ["Paste Text", "Upload PDF", "Example Text"],
        horizontal=True
    )
    
    input_text = ""
    
    if input_method == "Paste Text":
        input_text = st.text_area(
            "Enter your notes, paragraph, or topic:",
            height=200,
            placeholder="Paste your text here...",
            label_visibility="collapsed"
        )
    elif input_method == "Upload PDF":
        pdf_file = st.file_uploader(
            "Upload a PDF file:",
            type="pdf",
            label_visibility="collapsed"
        )
        if pdf_file is not None:
            with st.spinner("Reading PDF..."):
                input_text = extract_pdf_text(pdf_file)
                st.success(f"✅ Extracted {len(input_text)} characters from PDF")
            st.text_area(
                "Extracted text from PDF:",
                value=input_text,
                height=150,
                label_visibility="collapsed",
                disabled=True
            )
    else:
        # Example text
        example_text = """
Machine learning is a subset of artificial intelligence that provides systems 
the ability to automatically learn and improve from experience without being 
explicitly programmed. It focuses on computer programs that can access data and 
use it to learn for themselves. The process begins with observation or data, such 
as examples, direct experience or instruction to look for patterns in data and 
make better decisions in the future. Machine learning algorithms build models 
based on training data to make predictions or decisions without being explicitly 
programmed for every possible scenario. Common types include supervised learning, 
unsupervised learning, and reinforcement learning.
        """
        input_text = st.text_area(
            "Example text (feel free to modify):",
            value=example_text,
            height=200,
            label_visibility="collapsed"
        )
    
    # Generate buttons
    col1, col2, col3, col4 = st.columns([2, 1.2, 1.2, 0.8])
    
    with col1:
        generate_button = st.button(
            "✨ Generate Flashcards",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        summary_button = st.button(
            "📄 Generate Summary",
            use_container_width=True
        )
    
    with col3:
        clear_button = st.button(
            "🗑️ Clear",
            use_container_width=True
        )
    
    if clear_button:
        st.session_state.generated_flashcards = None
        st.session_state.generated_summary = None
        st.rerun()
    
    # Handle summary generation
    if summary_button:
        if not input_text or len(input_text.strip()) < 50:
            st.error("❌ Please enter at least 50 characters of text.")
        else:
            st.markdown("---")
            generator = load_generator()
            
            with st.spinner("Generating summary..."):
                try:
                    summary = generator.generate_summary(input_text, max_sentences=5)
                    st.session_state.generated_summary = summary
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
                    logger.error(f"Summary generation error: {e}")
    
    # Generation logic
    if generate_button:
        if not input_text or len(input_text.strip()) < 50:
            st.error("❌ Please enter at least 50 characters of text.")
            return
        
        st.markdown("---")
        
        # Load generator
        generator = load_generator()
        
        with st.spinner(f"Generating {num_flashcards} flashcards..."):
            try:
                flashcards = generator.generate_flashcards(
                    input_text,
                    num_flashcards=num_flashcards,
                    num_beams=num_beams
                )
            except Exception as e:
                st.error(f"Error generating flashcards: {str(e)}")
                logger.error(f"Generation error: {e}")
                return
        
        # Save to session state
        st.session_state.generated_flashcards = flashcards
        st.session_state.current_topic = "General Topic"
        
        # Update database
        db = create_progress_database()
        db.update_flashcard_count(len(flashcards))
    
    # Display summary if generated
    if 'generated_summary' in st.session_state and st.session_state.generated_summary:
        st.markdown("---")
        st.markdown("## 📋 Generated Summary")
        st.markdown(
            f'<div style="'
            f'background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); '
            f'border-radius: 10px; '
            f'padding: 20px; '
            f'color: #1a1a1a; '
            f'box-shadow: 0 4px 6px rgba(0,0,0,0.1); '
            f'"'
            f'>'
            f'{st.session_state.generated_summary}'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Display flashcards from session state
    if 'generated_flashcards' in st.session_state and st.session_state.generated_flashcards:
        flashcards = st.session_state.generated_flashcards
        
        st.markdown("---")
        
        # Display results
        if not flashcards:
            st.markdown(
                '<div class="warning-box">⚠️ <strong>Not enough context</strong><br>'
                'The model could not generate valid flashcards from the provided text. '
                'Please try with more detailed or longer text.</div>',
                unsafe_allow_html=True
            )
            return
        
        if len(flashcards) < 6:
            st.markdown(
                f'<div class="warning-box">⚠️ <strong>Limited flashcards</strong><br>'
                f'Only {len(flashcards)} flashcards generated (minimum 6 recommended). '
                f'More detailed input text may help.</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="success-box">✅ <strong>Generated {len(flashcards)} flashcards!</strong></div>',
                unsafe_allow_html=True
            )
        
        # Statistics
        st.markdown("## 📊 Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Flashcards", len(flashcards))
        
        with col2:
            avg_q_len = sum(len(f['question'].split()) for f in flashcards) / len(flashcards)
            st.metric("Avg Question Length", f"{avg_q_len:.1f} words")
        
        with col3:
            avg_a_len = sum(len(f['answer'].split()) for f in flashcards) / len(flashcards)
            st.metric("Avg Answer Length", f"{avg_a_len:.1f} words")
        
        # Display flashcards
        st.markdown("## 🎴 Your Flashcards")
        st.markdown("Click the 🔄 button or the card to flip between question and answer.")
        
        for idx, flashcard in enumerate(flashcards):
            display_flashcard(
                flashcard['question'],
                flashcard['answer'],
                idx
            )
        
        # Download button
        st.markdown("---")
        st.markdown("## 💾 Export Flashcards")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("Download your flashcards as a JSON file for use in other apps.")
        
        with col2:
            download_flashcards_json(flashcards)
        
        # Show JSON preview
        with st.expander("📋 View JSON Preview"):
            st.json(flashcards)


def main():
    """
    Main application with navigation.
    """
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Flashcard Generator"
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("# 🧭 Navigation")
        
        page = st.radio(
            "Select Page:",
            ["Flashcard Generator", "Take Quiz", "Progress Dashboard"],
            index=["Flashcard Generator", "Take Quiz", "Progress Dashboard"].index(st.session_state.current_page),
            key="page_nav"
        )
        
        st.session_state.current_page = page
        
        st.markdown("---")
        st.markdown("### ℹ️ App Info")
        st.info(
            "**AI Flashcard Generator**\n\n"
            "📚 Generate flashcards from text\n"
            "🎯 Take MCQ quizzes\n"
            "📊 Track your progress\n\n"
            "All data is stored locally."
        )
    
    # Route to appropriate page
    if st.session_state.current_page == "Flashcard Generator":
        show_flashcard_generator()
    elif st.session_state.current_page == "Take Quiz":
        show_quiz_page()
    elif st.session_state.current_page == "Progress Dashboard":
        show_dashboard_page()


if __name__ == '__main__':
    main()
