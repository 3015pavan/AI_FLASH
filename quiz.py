"""
Quiz generation and management module for AI Flashcard Generator
"""

import random
import logging
from typing import List, Dict, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuizGenerator:
    """
    Generate concept-based MCQ questions from flashcards.
    Each MCQ tests deeper understanding, not just repeating flashcard questions.
    """
    
    def __init__(self):
        self.quiz_data = None
        self.current_question_index = 0
        
    def generate_quiz_questions(
        self, 
        flashcards: List[Dict[str, str]]
    ) -> List[Dict]:
        """
        Generate MCQ questions from flashcards.
        
        Args:
            flashcards: List of flashcard dicts with 'question' and 'answer'
            
        Returns:
            List of MCQ question dicts with question, options, correct_index
        """
        
        if not flashcards or len(flashcards) < 4:
            logger.warning("Not enough flashcards for quiz generation")
            return None
        
        quiz_questions = []
        
        for idx, flashcard in enumerate(flashcards):
            question = flashcard.get('question', '')
            answer = flashcard.get('answer', '')
            
            # Generate conceptual MCQ question (not verbatim flashcard question)
            mcq_question = self._generate_conceptual_question(question, answer)
            
            # Get correct answer (from flashcard answer)
            correct_answer = self._extract_key_concept(answer)
            
            # Generate distractors from other flashcards
            distractors = self._generate_distractors(
                flashcards, 
                idx, 
                correct_answer
            )
            
            # Combine and shuffle options
            options = [correct_answer] + distractors
            correct_index = 0
            
            # Shuffle options
            shuffled_indices = list(range(len(options)))
            random.shuffle(shuffled_indices)
            
            options = [options[i] for i in shuffled_indices]
            correct_index = shuffled_indices.index(0)
            
            quiz_questions.append({
                'question': mcq_question,
                'original_flashcard_q': question,
                'original_flashcard_a': answer,
                'options': options,
                'correct_index': correct_index,
                'correct_answer': correct_answer
            })
        
        return quiz_questions
    
    def _generate_conceptual_question(self, original_q: str, answer: str) -> str:
        """
        Generate a conceptual MCQ question that tests understanding,
        not just repeating the flashcard question.
        """
        
        # Extract key concept from answer
        concept = self._extract_key_concept(answer)
        
        # Generate different question styles based on key concepts
        question_templates = [
            f"Which of the following best describes {concept}?",
            f"What is the primary characteristic of {concept}?",
            f"How can {concept} be identified in the context of the subject?",
            f"Which statement accurately explains {concept}?",
            f"What is the main role or function of {concept}?",
            f"Which of the following is true about {concept}?",
            f"What distinguishes {concept} from similar concepts?",
            f"In what scenario would {concept} be most relevant?",
        ]
        
        return random.choice(question_templates)
    
    def _extract_key_concept(self, answer: str) -> str:
        """
        Extract the key concept/phrase from the answer.
        Returns a meaningful substring from the answer.
        """
        
        # Clean the answer
        answer = answer.strip()
        
        # If answer is short, return as is
        if len(answer) < 30:
            return answer
        
        # Otherwise, extract first meaningful phrase
        # Look for first sentence or first key phrase
        sentences = answer.split('.')
        first_sentence = sentences[0].strip()
        
        # If first sentence is too long, try to extract key phrase
        if len(first_sentence) > 60:
            # Extract words 1-5 as key phrase
            words = first_sentence.split()[:6]
            return ' '.join(words)
        
        return first_sentence
    
    def _generate_distractors(
        self, 
        flashcards: List[Dict[str, str]], 
        current_idx: int,
        correct_answer: str
    ) -> List[str]:
        """
        Generate plausible wrong answer options from other flashcards.
        """
        
        distractors = []
        
        # Get indices of other flashcards
        other_indices = [i for i in range(len(flashcards)) if i != current_idx]
        
        # Select up to 3 random flashcards for distractors
        selected_indices = random.sample(
            other_indices, 
            min(3, len(other_indices))
        )
        
        for idx in selected_indices:
            distractor = self._extract_key_concept(
                flashcards[idx].get('answer', '')
            )
            
            # Ensure distractor is different from correct answer
            if distractor != correct_answer and distractor not in distractors:
                distractors.append(distractor)
        
        # If we don't have enough distractors, create generic ones
        while len(distractors) < 3:
            generic_distractor = self._create_generic_distractor()
            if generic_distractor not in distractors:
                distractors.append(generic_distractor)
        
        return distractors[:3]
    
    def _create_generic_distractor(self) -> str:
        """Create plausible but incorrect answer options."""
        
        generic_distractors = [
            "A hypothetical concept not related to the subject matter",
            "An outdated or historical approach no longer in use",
            "A common misconception about the topic",
            "A related but fundamentally different concept",
            "An advanced variation only applicable in specific scenarios",
            "A simplified interpretation missing key details",
            "An alternative definition from a different field",
            "A partial truth that misses the main point"
        ]
        
        return random.choice(generic_distractors)
    
    def get_quiz_question(self, quiz_questions: List[Dict], index: int) -> Dict:
        """Get a specific quiz question."""
        
        if index >= len(quiz_questions):
            return None
        
        return quiz_questions[index]
    
    def check_answer(self, quiz_questions: List[Dict], question_index: int, selected_index: int) -> bool:
        """
        Check if the selected answer is correct.
        
        Returns:
            True if correct, False otherwise
        """
        
        question = quiz_questions[question_index]
        return selected_index == question['correct_index']
    
    def calculate_score(self, quiz_questions: List[Dict], answers: List[int]) -> Dict:
        """
        Calculate quiz score and statistics.
        
        Args:
            quiz_questions: List of MCQ questions
            answers: List of selected answer indices
            
        Returns:
            Dict with score_percentage, correct_count, incorrect_count, details
        """
        
        correct_count = 0
        incorrect_count = 0
        details = []
        
        for idx, selected_index in enumerate(answers):
            question = quiz_questions[idx]
            is_correct = selected_index == question['correct_index']
            
            if is_correct:
                correct_count += 1
            else:
                incorrect_count += 1
            
            details.append({
                'question_index': idx,
                'question': question['question'],
                'selected_option': question['options'][selected_index],
                'correct_option': question['options'][question['correct_index']],
                'is_correct': is_correct,
                'explanation': question['original_flashcard_a']
            })
        
        total = len(quiz_questions)
        score_percentage = (correct_count / total * 100) if total > 0 else 0
        
        return {
            'score_percentage': round(score_percentage, 2),
            'correct_count': correct_count,
            'incorrect_count': incorrect_count,
            'total_questions': total,
            'details': details
        }


def create_quiz_generator() -> QuizGenerator:
    """Factory function to create quiz generator."""
    return QuizGenerator()
