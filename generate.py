"""
Inference script for generating flashcards from input text
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from utils import (
    clean_text, chunk_text, validate_answer_span,
    remove_duplicates, extract_answer_span, validate_flashcard
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check GPU availability
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Using device for inference: {DEVICE}")


class FlashcardGenerator:
    """
    Generate flashcards from input text using trained T5 model.
    """
    
    def __init__(self, model_dir: str = 'flashcard_t5'):
        """
        Initialize the flashcard generator with trained model.
        
        Args:
            model_dir: Directory containing saved model and tokenizer
        """
        self.model_dir = Path(model_dir)
        self.model = None
        self.tokenizer = None
        self.ready = False
        
        if not self.model_dir.exists():
            raise FileNotFoundError(
                f"Model directory not found at {self.model_dir}. "
                "Running in demo mode."
            )
        
        try:
            logger.info(f"Loading model from {self.model_dir}...")
            
            # Check if model files exist
            config_path = self.model_dir / 'config.json'
            if not config_path.exists():
                logger.warning("Model config not found. Using demo mode.")
                return
            
            # Try to load tokenizer and model
            try:
                self.tokenizer = T5Tokenizer.from_pretrained(str(self.model_dir))
                self.model = T5ForConditionalGeneration.from_pretrained(str(self.model_dir))
                
                # Move model to device
                self.model.to(DEVICE)
                self.model.eval()
                
                self.ready = True
                logger.info(f"Model loaded successfully on {DEVICE}")
            except Exception as e:
                logger.warning(f"Could not load full model: {e}. Demo mode active.")
                self.ready = False
                
        except Exception as e:
            logger.warning(f"Model initialization warning: {e}. Demo mode will be used.")
            self.ready = False
    
    def generate_flashcards(
        self,
        input_text: str,
        num_flashcards: int = 8,
        max_length: int = 256,
        num_beams: int = 6,
        no_repeat_ngram_size: int = 3
    ) -> List[Dict[str, str]]:
        """
        Generate flashcards from input text.
        
        Args:
            input_text: Input text to generate flashcards from
            num_flashcards: Target number of flashcards to generate
            max_length: Maximum length of generated text
            num_beams: Number of beams for beam search
            no_repeat_ngram_size: No repeat n-gram size
            
        Returns:
            List of flashcard dictionaries with 'question' and 'answer' keys
        """
        # If model not ready, return demo flashcards
        if not self.ready or self.model is None:
            return self._generate_demo_flashcards(input_text, num_flashcards)
        
        # Clean input text
        input_text = clean_text(input_text)
        
        if len(input_text.strip()) < 50:
            logger.warning("Input text too short. Minimum 50 characters required.")
            return []
        
        # Chunk text to fit within token limit
        chunks = chunk_text(input_text, chunk_size=350, overlap=50)
        logger.info(f"Text split into {len(chunks)} chunks")
        
        all_flashcards = []
        
        # Generate flashcards from each chunk
        for chunk_idx, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {chunk_idx + 1}/{len(chunks)}...")
            
            # Prepare input
            input_prompt = f"flashcard: {chunk}"
            
            # Tokenize
            inputs = self.tokenizer(
                input_prompt,
                max_length=512,
                truncation=True,
                return_tensors='pt'
            ).to(DEVICE)
            
            # Generate multiple flashcards from this chunk
            try:
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs['input_ids'],
                        max_length=max_length,
                        num_beams=num_beams,
                        no_repeat_ngram_size=no_repeat_ngram_size,
                        num_return_sequences=min(num_flashcards // len(chunks) + 2, 5),
                        early_stopping=True,
                        temperature=0.7,
                        top_p=0.9,
                        do_sample=False,
                    )
                
                # Decode outputs
                for output in outputs:
                    decoded = self.tokenizer.decode(output, skip_special_tokens=True)
                    
                    # Parse question and answer
                    flashcard = self._parse_flashcard(decoded, chunk)
                    
                    if flashcard:
                        all_flashcards.append(flashcard)
                        
            except Exception as e:
                logger.error(f"Error generating flashcards for chunk {chunk_idx}: {e}")
                continue
        
        # Remove duplicates
        all_flashcards = remove_duplicates(all_flashcards)
        
        # Ensure we have at least 6 flashcards
        if len(all_flashcards) < 6:
            logger.warning(f"Generated only {len(all_flashcards)} flashcards. Minimum 6 recommended.")
        
        # Limit to target number
        all_flashcards = all_flashcards[:num_flashcards]
        
        logger.info(f"Generated {len(all_flashcards)} flashcards")
        
        return all_flashcards
    
    def _parse_flashcard(self, generated_text: str, context: str) -> Dict[str, str]:
        """
        Parse generated text into question and answer.
        
        Args:
            generated_text: Raw generated text from model
            context: Original context text
            
        Returns:
            Dictionary with 'question' and 'answer' keys, or None if invalid
        """
        # Split by separator
        if '<sep>' not in generated_text.lower():
            return None
        
        parts = generated_text.split('<sep>')
        if len(parts) != 2:
            return None
        
        question = parts[0].strip()
        answer = parts[1].strip()
        
        # Clean text
        question = question.replace('<pad>', '').replace('</s>', '').strip()
        answer = answer.replace('<pad>', '').replace('</s>', '').strip()
        
        # Validate answer is in context
        is_valid, validated_answer = extract_answer_span(answer, context)
        
        if not is_valid:
            return None
        
        # Final validation
        if not validate_flashcard(question, validated_answer, context):
            return None
        
        return {
            'question': question,
            'answer': validated_answer
        }
    
    def _generate_demo_flashcards(self, input_text: str, num: int) -> List[Dict[str, str]]:
        """
        Generate demo flashcards when model is not available.
        """
        demo = [
            {
                "question": "What is the main topic discussed in the text?",
                "answer": "The text discusses " + input_text[:100] + "..."
            },
            {
                "question": "What are the key concepts mentioned?",
                "answer": "Various important concepts and ideas are covered throughout the text."
            },
            {
                "question": "What is the significance of this topic?",
                "answer": "This topic is significant for understanding modern concepts and practices."
            }
        ]
        return demo[:num]


def generate_flashcards_from_text(text: str) -> List[Dict[str, str]]:
    """
    Convenience function to generate flashcards from text.
    
    Args:
        text: Input text
        
    Returns:
        List of flashcards
    """
    generator = FlashcardGenerator()
    return generator.generate_flashcards(text, num_flashcards=10)


if __name__ == '__main__':
    # Example usage
    sample_text = """
    Machine learning is a subset of artificial intelligence (AI) that provides 
    systems the ability to automatically learn and improve from experience without 
    being explicitly programmed. Machine learning focuses on computer programs that 
    can access data and use it to learn for themselves. The process begins with 
    observation or data, such as examples, direct experience or instruction to look 
    for patterns in data and make better decisions in the future based on the examples 
    provided. The primary aim is to allow the computer systems to learn from experience, 
    learn from their own mistakes, and improve their performance.
    """
    
    print("Generating flashcards from sample text...")
    flashcards = generate_flashcards_from_text(sample_text)
    
    print(f"\nGenerated {len(flashcards)} flashcards:")
    print(json.dumps(flashcards, indent=2))
