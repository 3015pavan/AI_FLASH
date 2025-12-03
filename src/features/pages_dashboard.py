"""
Progress Dashboard page for Streamlit multi-page app
Shows analytics, charts, and learning progress
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from src.features.dashboard import create_progress_database

def show_dashboard_page():
    """Display the progress dashboard."""
    
    st.markdown("# 📊 Learning Progress Dashboard")
    st.markdown(
        "Track your learning journey with detailed analytics and insights."
    )
    
    st.markdown("---")
    
    # Initialize database
    db = create_progress_database()
    
    # Get all data
    global_metrics = db.get_global_metrics()
    quiz_attempts = db.get_all_quiz_attempts()
    avg_score = db.get_average_score()
    learning_streak = db.get_learning_streak()
    topic_stats = db.get_topic_statistics()
    score_trend = db.get_score_trend_data(days=30)
    
    # Check if any data exists
    if not quiz_attempts:
        st.info(
            "📈 No quiz data yet. Complete some quizzes to see your progress here!"
        )
        return
    
    # ============================================
    # 1. KPI Summary Cards
    # ============================================
    st.markdown("## 📈 Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Flashcards",
            global_metrics.get('total_flashcards_generated', 0)
        )
    
    with col2:
        st.metric(
            "Quizzes Taken",
            global_metrics.get('total_quizzes_taken', 0)
        )
    
    with col3:
        st.metric(
            "Average Score",
            f"{avg_score:.1f}%"
        )
    
    with col4:
        st.metric(
            "Learning Streak",
            f"{learning_streak} days"
        )
    
    st.markdown("---")
    
    # ============================================
    # 2. Score Trend Chart
    # ============================================
    if score_trend:
        st.markdown("## 📈 Score Trend (Last 30 Days)")
        
        df_trend = pd.DataFrame(score_trend, columns=['Date', 'Average Score'])
        
        fig_trend = px.line(
            df_trend,
            x='Date',
            y='Average Score',
            title='Daily Average Score Trend',
            markers=True,
            labels={'Average Score': 'Score (%)', 'Date': 'Date'}
        )
        
        fig_trend.update_layout(
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        fig_trend.update_yaxes(range=[0, 100])
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        st.markdown("---")
    
    # ============================================
    # 3. Score Distribution Pie Chart
    # ============================================
    if quiz_attempts:
        st.markdown("## 📊 Overall Performance")
        
        total_correct = sum(int(q['correct_answers']) for q in quiz_attempts)
        total_incorrect = sum(int(q['incorrect_answers']) for q in quiz_attempts)
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Correct', 'Incorrect'],
            values=[total_correct, total_incorrect],
            marker=dict(colors=['#28a745', '#dc3545']),
            textinfo='label+percent+value'
        )])
        
        fig_pie.update_layout(
            title='Correct vs Incorrect Answers',
            height=400
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("---")
    
    # ============================================
    # 4. Topic Performance Bar Chart
    # ============================================
    if topic_stats:
        st.markdown("## 📚 Performance by Topic")
        
        topics = list(topic_stats.keys())
        avg_scores = [topic_stats[t]['avg_score'] for t in topics]
        attempts = [topic_stats[t]['attempts'] for t in topics]
        
        df_topics = pd.DataFrame({
            'Topic': topics,
            'Average Score': avg_scores,
            'Attempts': attempts
        })
        
        fig_topics = px.bar(
            df_topics,
            x='Topic',
            y='Average Score',
            title='Average Score by Topic',
            color='Average Score',
            color_continuous_scale='RdYlGn',
            hover_data=['Attempts']
        )
        
        fig_topics.update_layout(
            height=400,
            template='plotly_white'
        )
        
        fig_topics.update_yaxes(range=[0, 100])
        
        st.plotly_chart(fig_topics, use_container_width=True)
        
        st.markdown("---")
    
    # ============================================
    # 5. Detailed Activity Table
    # ============================================
    st.markdown("## 📋 Recent Quiz Attempts")
    
    if quiz_attempts:
        # Prepare dataframe
        df_attempts = pd.DataFrame(quiz_attempts)
        
        # Format date
        df_attempts['date'] = pd.to_datetime(df_attempts['date']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Rename and reorder columns for display
        df_display = df_attempts[[
            'date', 'topic', 'score_percentage', 'correct_answers', 
            'total_questions', 'time_taken_seconds'
        ]].copy()
        
        df_display.columns = [
            'Date', 'Topic', 'Score (%)', 'Correct', 'Total Q.', 'Time (s)'
        ]
        
        # Format score with color indication
        def get_score_badge(score):
            if score >= 80:
                return f"🟢 {score}%"
            elif score >= 60:
                return f"🟡 {score}%"
            else:
                return f"🔴 {score}%"
        
        df_display['Score (%)'] = df_display['Score (%)'].apply(get_score_badge)
        
        # Display table
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # ============================================
    # 6. Detailed Topic Statistics
    # ============================================
    if topic_stats:
        st.markdown("## 📊 Detailed Topic Statistics")
        
        with st.expander("View topic breakdown"):
            for topic in sorted(topic_stats.keys()):
                stats = topic_stats[topic]
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric(f"📚 {topic}", stats['attempts'], label_visibility="collapsed")
                
                with col2:
                    st.metric("Avg", f"{stats['avg_score']:.1f}%", label_visibility="collapsed")
                
                with col3:
                    st.metric("Best", f"{stats['best_score']:.1f}%", label_visibility="collapsed")
                
                with col4:
                    st.metric("Worst", f"{stats['worst_score']:.1f}%", label_visibility="collapsed")
                
                with col5:
                    improvement = stats['best_score'] - stats['worst_score']
                    st.metric("Improve.", f"+{improvement:.1f}%", label_visibility="collapsed")
    
    st.markdown("---")
    
    # ============================================
    # 7. Reset Data Option (in expander)
    # ============================================
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Dashboard", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
                if st.session_state.get('confirm_clear', False):
                    db.clear_all_data()
                    st.success("✅ All data cleared!")
                    st.session_state.confirm_clear = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("⚠️ Click again to confirm clearing all data")


if __name__ == "__main__":
    show_dashboard_page()
