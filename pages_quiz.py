"""
Quiz page for Streamlit multi-page app
"""

import streamlit as st
import time
from quiz import QuizGenerator
from dashboard import create_progress_database

def show_quiz_page():
    """Display the quiz interface."""
    
    st.markdown("# 🎯 MCQ Quiz")
    st.markdown(
        "Test your understanding with concept-based multiple-choice questions "
        "generated from your flashcards."
    )
    
    st.markdown("---")
    
    # Check if flashcards exist in session
    if 'generated_flashcards' not in st.session_state or not st.session_state.generated_flashcards:
        st.warning(
            "⚠️ No flashcards found. Please generate flashcards first from the main page."
        )
        return
    
    flashcards = st.session_state.generated_flashcards
    
    # Check minimum flashcards requirement
    if len(flashcards) < 4:
        st.error(
            f"❌ Not enough flashcards to generate quiz. "
            f"You have {len(flashcards)} flashcards, but at least 4 are required."
        )
        return
    
    # Initialize quiz session state
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.quiz_questions = None
        st.session_state.quiz_answers = []
        st.session_state.current_question = 0
        st.session_state.quiz_completed = False
        st.session_state.quiz_start_time = None
    
    # Quiz control buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("▶️ Start Quiz", use_container_width=True, type="primary"):
            # Generate quiz questions
            quiz_gen = QuizGenerator()
            quiz_questions = quiz_gen.generate_quiz_questions(flashcards)
            
            if quiz_questions:
                st.session_state.quiz_questions = quiz_questions
                st.session_state.quiz_started = True
                st.session_state.quiz_answers = [None] * len(quiz_questions)
                st.session_state.current_question = 0
                st.session_state.quiz_completed = False
                st.session_state.quiz_start_time = time.time()
                st.rerun()
            else:
                st.error("Failed to generate quiz questions")
    
    with col2:
        if st.button("🔄 Reset Quiz", use_container_width=True):
            st.session_state.quiz_started = False
            st.session_state.quiz_questions = None
            st.session_state.quiz_answers = []
            st.session_state.current_question = 0
            st.session_state.quiz_completed = False
            st.rerun()
    
    with col3:
        st.write("")  # Placeholder
    
    st.markdown("---")
    
    # If quiz not started, show info
    if not st.session_state.quiz_started:
        st.info(
            f"📋 Ready to start a quiz with {len(flashcards)} flashcards? "
            "Click the 'Start Quiz' button above!"
        )
        return
    
    # Display current question
    if st.session_state.quiz_completed:
        _display_quiz_results(st.session_state.quiz_questions, st.session_state.quiz_answers)
    else:
        _display_quiz_question()


def _display_quiz_question():
    """Display current quiz question and options."""
    
    quiz_questions = st.session_state.quiz_questions
    current_idx = st.session_state.current_question
    total_questions = len(quiz_questions)
    
    # Progress bar
    progress = current_idx / total_questions
    st.progress(progress)
    st.markdown(f"**Question {current_idx + 1} of {total_questions}**")
    
    st.markdown("---")
    
    # Get current question
    question = quiz_questions[current_idx]
    
    # Display question
    st.markdown(f"### {question['question']}")
    
    st.markdown("**Choose the best answer:**")
    
    # Display options as radio buttons
    selected_option = st.radio(
        label="Options",
        options=question['options'],
        label_visibility="collapsed",
        key=f"question_{current_idx}"
    )
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_idx > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_question -= 1
                st.rerun()
    
    with col2:
        # Save current answer
        selected_index = question['options'].index(selected_option)
        st.session_state.quiz_answers[current_idx] = selected_index
        
        if current_idx < len(quiz_questions) - 1:
            if st.button("➡️ Next", use_container_width=True, type="primary"):
                st.session_state.current_question += 1
                st.rerun()
        else:
            if st.button("✅ Submit Quiz", use_container_width=True, type="primary"):
                st.session_state.quiz_completed = True
                st.rerun()
    
    with col3:
        st.write("")  # Placeholder


def _display_quiz_results(quiz_questions, answers):
    """Display quiz results and detailed feedback."""
    
    quiz_gen = QuizGenerator()
    score_data = quiz_gen.calculate_score(quiz_questions, answers)
    
    # Calculate time taken
    time_taken = time.time() - st.session_state.quiz_start_time
    time_taken_seconds = int(time_taken)
    
    # Save quiz attempt to database
    db = create_progress_database()
    topic = st.session_state.get('current_topic', 'General Quiz')
    db.save_quiz_attempt(
        topic=topic,
        score_percentage=score_data['score_percentage'],
        total_questions=score_data['total_questions'],
        correct_answers=score_data['correct_count'],
        incorrect_answers=score_data['incorrect_count'],
        time_taken_seconds=time_taken_seconds,
        flashcards_used=len(quiz_questions)
    )
    
    st.markdown("---")
    st.markdown("# 🎉 Quiz Completed!")
    
    # Display score
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Score", f"{score_data['score_percentage']:.1f}%")
    
    with col2:
        st.metric("Correct", f"{score_data['correct_count']}/{score_data['total_questions']}")
    
    with col3:
        st.metric("Incorrect", score_data['incorrect_count'])
    
    with col4:
        minutes = time_taken_seconds // 60
        seconds = time_taken_seconds % 60
        st.metric("Time", f"{minutes}m {seconds}s")
    
    st.markdown("---")
    
    # Display detailed results
    st.markdown("## 📋 Detailed Results")
    
    for detail in score_data['details']:
        question_num = detail['question_index'] + 1
        
        with st.expander(
            f"Q{question_num}: {'✅ Correct' if detail['is_correct'] else '❌ Incorrect'}",
            expanded=False
        ):
            st.markdown(f"**Question:** {detail['question']}")
            
            if detail['is_correct']:
                st.success(f"✅ Your answer: {detail['selected_option']}")
            else:
                st.error(f"❌ Your answer: {detail['selected_option']}")
                st.success(f"✅ Correct answer: {detail['correct_option']}")
            
            st.markdown(f"**Explanation (from flashcard):**")
            st.info(detail['explanation'])
    
    st.markdown("---")
    
    # Retake quiz option
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.quiz_started = False
            st.session_state.quiz_questions = None
            st.session_state.quiz_answers = []
            st.session_state.current_question = 0
            st.session_state.quiz_completed = False
            st.rerun()
    
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.current_page = "Flashcard Generator"
            st.rerun()


if __name__ == "__main__":
    show_quiz_page()
