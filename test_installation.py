"""
Test script to verify AI Flashcard Generator installation and functionality
Run this after training to test the complete pipeline
"""

import json
import sys
from pathlib import Path

def test_imports():
    """Test all required imports."""
    print("\n" + "="*60)
    print("TESTING IMPORTS")
    print("="*60)
    
    try:
        import torch
        print(f"✓ torch {torch.__version__}")
    except ImportError as e:
        print(f"✗ torch: {e}")
        return False
    
    try:
        import transformers
        print(f"✓ transformers {transformers.__version__}")
    except ImportError as e:
        print(f"✗ transformers: {e}")
        return False
    
    try:
        import datasets
        print(f"✓ datasets {datasets.__version__}")
    except ImportError as e:
        print(f"✗ datasets: {e}")
        return False
    
    try:
        import streamlit
        print(f"✓ streamlit {streamlit.__version__}")
    except ImportError as e:
        print(f"✗ streamlit: {e}")
        return False
    
    print("\n✓ All imports successful!")
    return True


def test_model_exists():
    """Test if trained model exists."""
    print("\n" + "="*60)
    print("TESTING MODEL FILES")
    print("="*60)
    
    model_dir = Path('flashcard_t5')
    
    if not model_dir.exists():
        print(f"✗ Model directory not found: {model_dir}")
        print("  Please run: python train.py")
        return False
    
    required_files = [
        'config.json',
        'pytorch_model.bin',
        'spiece.model',
        'tokenizer_config.json'
    ]
    
    for file in required_files:
        file_path = model_dir / file
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"✓ {file} ({size_mb:.1f} MB)")
        else:
            print(f"✗ {file} missing")
            return False
    
    print("\n✓ All model files found!")
    return True


def test_generator():
    """Test flashcard generator."""
    print("\n" + "="*60)
    print("TESTING FLASHCARD GENERATOR")
    print("="*60)
    
    try:
        from generate import FlashcardGenerator
        print("✓ FlashcardGenerator imported")
    except ImportError as e:
        print(f"✗ Failed to import FlashcardGenerator: {e}")
        return False
    
    try:
        print("  Loading model...")
        gen = FlashcardGenerator()
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return False
    
    # Test with sample text
    sample_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, 
    in contrast to the natural intelligence displayed by humans and animals. 
    AI has applications in various fields including healthcare, finance, 
    transportation, and entertainment. Machine learning is a subset of AI 
    that enables systems to learn and improve from experience without being 
    explicitly programmed. Deep learning uses artificial neural networks 
    with multiple layers to process data and recognize patterns.
    """
    
    try:
        print("  Generating flashcards from sample text...")
        flashcards = gen.generate_flashcards(
            sample_text,
            num_flashcards=6,
            num_beams=4  # Lower for testing
        )
        print(f"✓ Generated {len(flashcards)} flashcards")
        
        if flashcards:
            print("\n  Sample flashcard:")
            print(f"  Q: {flashcards[0]['question'][:50]}...")
            print(f"  A: {flashcards[0]['answer'][:50]}...")
        
        return True
    except Exception as e:
        print(f"✗ Generation failed: {e}")
        return False


def test_utils():
    """Test utility functions."""
    print("\n" + "="*60)
    print("TESTING UTILITY FUNCTIONS")
    print("="*60)
    
    try:
        from utils import (
            clean_text, chunk_text, validate_answer_span,
            remove_duplicates, validate_flashcard
        )
        print("✓ All utils imported")
        
        # Test clean_text
        text = "This   is   messy  text!"
        cleaned = clean_text(text)
        print(f"✓ clean_text: '{text}' → '{cleaned}'")
        
        # Test chunk_text
        long_text = " ".join(["word"] * 500)
        chunks = chunk_text(long_text, chunk_size=100)
        print(f"✓ chunk_text: 500 words → {len(chunks)} chunks")
        
        # Test validate_answer_span
        answer = "artificial intelligence"
        context = "Artificial intelligence is a field of computer science"
        is_valid = validate_answer_span(answer, context)
        print(f"✓ validate_answer_span: {is_valid}")
        
        # Test remove_duplicates
        flashcards = [
            {"question": "What is AI?", "answer": "Artificial intelligence"},
            {"question": "What is AI?", "answer": "AI"},
            {"question": "What is ML?", "answer": "Machine learning"}
        ]
        unique = remove_duplicates(flashcards)
        print(f"✓ remove_duplicates: {len(flashcards)} → {len(unique)} unique")
        
        return True
    except Exception as e:
        print(f"✗ Utils test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  AI FLASHCARD GENERATOR - INSTALLATION TEST".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Model Files", test_model_exists()))
    results.append(("Utils", test_utils()))
    results.append(("Generator", test_generator()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {test_name}")
    
    print("-"*60)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "🎉 "*10)
        print("ALL TESTS PASSED! Ready to use.")
        print("Run: streamlit run app.py")
        print("🎉 "*10)
        return 0
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        if not test_model_exists.__doc__:
            print("Hint: Did you run 'python train.py' first?")
        return 1


if __name__ == '__main__':
    sys.exit(main())
