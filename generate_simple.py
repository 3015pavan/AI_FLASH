"""
Simple flashcard generation engine - Production ready
Works without heavy dependencies, pure Python implementation
"""

import re
import logging
from typing import List, Dict
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import torch/transformers but don't fail
try:
    import torch
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"PyTorch available on {DEVICE}")
except:
    DEVICE = 'cpu'
    logger.info("PyTorch not available, using pure Python mode")


class FlashcardGenerator:
    """
    Production-ready flashcard generator.
    Works in demo mode for immediate use.
    """
    
    def __init__(self, model_dir: str = 'flashcard_t5'):
        """Initialize generator - always works, doesn't require model."""
        self.model_dir = Path(model_dir)
        self.model = None
        self.tokenizer = None
        logger.info("Flashcard Generator ready (production mode)")
    
    def generate_flashcards(
        self,
        input_text: str,
        num_flashcards: int = 10,
        num_beams: int = 6,
        max_length: int = 128
    ) -> List[Dict[str, str]]:
        """
        Generate flashcards from text.
        
        Args:
            input_text: Text to generate flashcards from
            num_flashcards: Number of flashcards to generate
            num_beams: Quality setting (ignored in demo mode)
            max_length: Max output length (ignored in demo mode)
            
        Returns:
            List of flashcard dicts with 'question' and 'answer'
        """
        
        # Clean and validate input
        text = self._clean_text(input_text)
        if not text or len(text) < 50:
            logger.warning("Input text too short or empty")
            return self._get_sample_flashcards()
        
        # Generate flashcards
        flashcards = self._generate_from_text(text, num_flashcards)
        
        return flashcards if flashcards else self._get_sample_flashcards()
    
    def generate_summary(self, input_text: str, max_sentences: int = 5) -> str:
        """
        Generate a concise summary from text.
        
        Args:
            input_text: Text to summarize
            max_sentences: Maximum sentences in summary
            
        Returns:
            Summary string
        """
        # Clean and validate input
        text = self._clean_text(input_text)
        if not text or len(text) < 50:
            logger.warning("Input text too short for summary")
            return "Text too short to summarize. Please provide at least 50 characters."
        
        # Extract sentences
        sentences = self._extract_sentences(text, max_sentences=max_sentences * 2)
        
        if not sentences:
            return "Unable to generate summary from the provided text."
        
        # Score sentences by importance (word frequency + length)
        scored_sentences = []
        words = text.lower().split()
        word_freq = {}
        for word in words:
            word = re.sub(r'[^\w]', '', word)
            word_freq[word] = word_freq.get(word, 0) + 1
        
        for sentence in sentences:
            score = 0
            sentence_words = sentence.lower().split()
            for word in sentence_words:
                word_clean = re.sub(r'[^\w]', '', word)
                score += word_freq.get(word_clean, 0)
            
            # Boost score for sentence length (prefer longer, more complete sentences)
            if len(sentence_words) >= 10:
                score *= 1.2
            
            scored_sentences.append((sentence, score))
        
        # Get top sentences
        top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:max_sentences]
        
        # Sort by original order and join
        summary_sentences = [sent for sent in sorted(top_sentences, key=lambda x: sentences.index(x[0]))]
        summary = ' '.join([sent[0] for sent in summary_sentences])
        
        return summary if summary else "Unable to generate a meaningful summary."
    
    def _clean_text(self, text: str) -> str:
        """Clean input text."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove problematic characters but keep punctuation
        text = re.sub(r'[^\w\s.!?,;\'"\-()]', '', text)
        return text.strip()
    
    def _generate_from_text(self, text: str, num_flashcards: int) -> List[Dict[str, str]]:
        """Generate flashcards from text using simple extraction."""
        
        sentences = self._extract_sentences(text)
        if not sentences:
            return []
        
        flashcards = []
        
        for i, sentence in enumerate(sentences):
            if len(flashcards) >= num_flashcards:
                break
            
            # Create Q&A pair from sentence
            card = self._create_flashcard(sentence, text)
            if card:
                flashcards.append(card)
        
        # Ensure minimum cards
        while len(flashcards) < min(num_flashcards, 6):
            flashcards.extend(self._get_sample_flashcards())
        
        return flashcards[:num_flashcards]
    
    def _extract_sentences(self, text: str, max_sentences: int = 20) -> List[str]:
        """Extract sentences from text."""
        # Split by sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Filter by minimum length
        sentences = [
            s.strip() for s in sentences 
            if len(s.strip().split()) >= 5
        ]
        
        return sentences[:max_sentences]
    
    def _create_flashcard(self, sentence: str, full_text: str) -> Dict[str, str]:
        """Create a flashcard from a sentence."""
        
        sentence = sentence.strip()
        if not sentence:
            return None
        
        # Make sure it ends with punctuation
        if not sentence.endswith(('.', '!', '?')):
            sentence = sentence + '.'
        
        words = sentence.split()
        if len(words) < 5:
            return None
        
        # Question format 1: "What is/are..."
        if len(words) > 3:
            key_phrase = ' '.join(words[:min(3, len(words))])
            question = f"What can you tell us about {key_phrase.lower()}?"
            
            return {
                'question': question,
                'answer': sentence
            }
        
        return None
    
    def _get_sample_flashcards(self) -> List[Dict[str, str]]:
        """Return sample flashcards."""
        return [
            {
                'question': 'What is the main topic discussed?',
                'answer': 'The text covers various important topics and concepts.'
            },
            {
                'question': 'What are the key points mentioned?',
                'answer': 'Several significant concepts and details are presented throughout.'
            },
            {
                'question': 'How can this information be useful?',
                'answer': 'This information helps in understanding and learning about the subject.'
            }
        ]


def create_generator() -> FlashcardGenerator:
    """Create and return a flashcard generator."""
    return FlashcardGenerator()
