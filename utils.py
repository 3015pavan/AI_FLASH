"""
Utility functions for text processing and validation
"""

import re
from typing import List, Dict, Tuple


def clean_text(text: str) -> str:
    """
    Clean input text by removing extra whitespace and normalizing.
    
    Args:
        text: Raw input text
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep alphanumeric, punctuation, and spaces
    text = re.sub(r'[^\w\s.!?,;:\'\"-]', '', text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 350, overlap: int = 50) -> List[str]:
    """
    Split text into chunks with overlap to preserve context.
    
    Args:
        text: Input text to chunk
        chunk_size: Approximate number of words per chunk
        overlap: Number of words to overlap between chunks
        
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    if len(words) <= chunk_size:
        return [text]
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks


def validate_answer_span(answer: str, context: str) -> bool:
    """
    Validate that answer is a substring (or close match) of context.
    
    Args:
        answer: Generated answer
        context: Original context text
        
    Returns:
        True if answer is found in context, False otherwise
    """
    # Normalize both strings
    answer_lower = answer.lower().strip()
    context_lower = context.lower()
    
    # Check if answer is directly in context
    if answer_lower in context_lower:
        return True
    
    # Check if first few words of answer appear in context
    words = answer_lower.split()
    if len(words) > 0:
        first_words = ' '.join(words[:min(3, len(words))])
        if first_words in context_lower:
            return True
    
    return False


def remove_duplicates(flashcards: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Remove duplicate flashcards based on question similarity.
    
    Args:
        flashcards: List of flashcard dictionaries
        
    Returns:
        List of unique flashcards
    """
    unique_flashcards = []
    seen_questions = set()
    
    for flashcard in flashcards:
        question = flashcard.get('question', '').lower().strip()
        
        # Normalize for comparison
        question_normalized = re.sub(r'\s+', ' ', question)
        
        # Check if similar question already exists
        is_duplicate = False
        for seen_q in seen_questions:
            # Simple similarity check - exact match after normalization
            if question_normalized == seen_q:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_flashcards.append(flashcard)
            seen_questions.add(question_normalized)
    
    return unique_flashcards


def extract_answer_span(generated_text: str, context: str) -> Tuple[bool, str]:
    """
    Extract the longest valid answer span from generated text that exists in context.
    
    Args:
        generated_text: Generated answer text
        context: Original context
        
    Returns:
        Tuple of (is_valid, extracted_answer)
    """
    # Split by common separators
    parts = generated_text.split('<sep>')
    if len(parts) == 2:
        answer = parts[1].strip()
    else:
        answer = generated_text.strip()
    
    # Clean the answer
    answer = answer.replace('[SEP]', '').replace('[EOS]', '').strip()
    
    # Remove trailing incomplete sentences
    if answer.endswith(' and'):
        answer = answer[:-4].strip()
    
    # Validate answer is in context
    if validate_answer_span(answer, context):
        return True, answer
    
    # Try to find largest substring that exists in context
    words = answer.split()
    for length in range(len(words), 0, -1):
        candidate = ' '.join(words[:length])
        if validate_answer_span(candidate, context):
            return True, candidate
    
    return False, ""


def validate_flashcard(question: str, answer: str, context: str, min_answer_len: int = 3) -> bool:
    """
    Validate a complete flashcard for quality.
    
    Args:
        question: Question text
        answer: Answer text
        context: Original context
        min_answer_len: Minimum answer length in words
        
    Returns:
        True if flashcard passes validation
    """
    # Check lengths
    if len(question.strip()) < 10 or len(answer.strip()) < min_answer_len:
        return False
    
    # Check answer is in context
    if not validate_answer_span(answer, context):
        return False
    
    # Check for placeholder text
    if any(placeholder in question.lower() for placeholder in ['[', ']', '__', '???', '...']):
        return False
    
    # Check answer sentences don't exceed 3
    sentences = answer.split('.')
    if len([s for s in sentences if s.strip()]) > 3:
        return False
    
    return True
