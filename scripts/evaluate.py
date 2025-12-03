"""
Evaluation Script for T5 Flashcard Generator
============================================
Evaluates fine-tuned model on test set using various metrics.

Usage:
    python scripts/evaluate.py --model_path models/flashcard_t5_finetuned
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
from torch.utils.data import DataLoader
from transformers import T5Tokenizer, T5ForConditionalGeneration
from datasets import load_dataset
from tqdm import tqdm
import numpy as np
import logging

# Metrics
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

from config.model_config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class T5Evaluator:
    """Evaluator class for T5 model performance assessment."""
    
    def __init__(self, model_path: str):
        """
        Initialize evaluator with trained model.
        
        Args:
            model_path: Path to saved model directory
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(model_path)
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        logger.info(f"Loaded model from: {model_path}")
        
        # Initialize metrics
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
        self.smoothing = SmoothingFunction()
    
    def generate_question(self, context: str) -> str:
        """
        Generate question from context.
        
        Args:
            context: Input context text
            
        Returns:
            Generated question
        """
        input_text = f"generate question: {context}"
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            max_length=config.max_input_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_length=config.max_output_length,
                num_beams=config.num_beams,
                early_stopping=True
            )
        
        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text
    
    def calculate_bleu(self, reference: str, hypothesis: str) -> float:
        """
        Calculate BLEU score.
        
        Args:
            reference: Ground truth text
            hypothesis: Generated text
            
        Returns:
            BLEU score (0-1)
        """
        reference_tokens = [reference.split()]
        hypothesis_tokens = hypothesis.split()
        
        try:
            score = sentence_bleu(
                reference_tokens,
                hypothesis_tokens,
                smoothing_function=self.smoothing.method1
            )
        except:
            score = 0.0
        
        return score
    
    def calculate_rouge(self, reference: str, hypothesis: str) -> dict:
        """
        Calculate ROUGE scores.
        
        Args:
            reference: Ground truth text
            hypothesis: Generated text
            
        Returns:
            Dictionary with ROUGE-1, ROUGE-2, ROUGE-L scores
        """
        scores = self.rouge_scorer.score(reference, hypothesis)
        
        return {
            'rouge1': scores['rouge1'].fmeasure,
            'rouge2': scores['rouge2'].fmeasure,
            'rougeL': scores['rougeL'].fmeasure
        }
    
    def evaluate_dataset(
        self,
        dataset_name: str = "squad",
        split: str = "validation",
        max_samples: int = None
    ) -> dict:
        """
        Evaluate model on dataset.
        
        Args:
            dataset_name: Dataset to use
            split: Dataset split
            max_samples: Limit number of samples
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info(f"Evaluating on {dataset_name} - {split} split")
        
        # Load dataset
        dataset = load_dataset(dataset_name, split=split)
        if max_samples:
            dataset = dataset.select(range(max_samples))
        
        logger.info(f"Evaluating on {len(dataset)} examples")
        
        # Metrics storage
        bleu_scores = []
        rouge1_scores = []
        rouge2_scores = []
        rougeL_scores = []
        
        # Evaluate samples
        for example in tqdm(dataset, desc="Evaluating"):
            context = example['context']
            reference_question = example['question']
            
            # Generate question
            generated_question = self.generate_question(context)
            
            # Calculate metrics
            bleu = self.calculate_bleu(reference_question, generated_question)
            rouge = self.calculate_rouge(reference_question, generated_question)
            
            bleu_scores.append(bleu)
            rouge1_scores.append(rouge['rouge1'])
            rouge2_scores.append(rouge['rouge2'])
            rougeL_scores.append(rouge['rougeL'])
        
        # Aggregate results
        results = {
            'bleu': {
                'mean': np.mean(bleu_scores),
                'std': np.std(bleu_scores),
                'min': np.min(bleu_scores),
                'max': np.max(bleu_scores)
            },
            'rouge1': {
                'mean': np.mean(rouge1_scores),
                'std': np.std(rouge1_scores)
            },
            'rouge2': {
                'mean': np.mean(rouge2_scores),
                'std': np.std(rouge2_scores)
            },
            'rougeL': {
                'mean': np.mean(rougeL_scores),
                'std': np.std(rougeL_scores)
            },
            'num_samples': len(dataset)
        }
        
        return results
    
    def print_results(self, results: dict):
        """Print evaluation results in formatted manner."""
        logger.info("\n" + "="*60)
        logger.info("EVALUATION RESULTS")
        logger.info("="*60)
        logger.info(f"Number of samples: {results['num_samples']}")
        logger.info("")
        logger.info(f"BLEU Score:")
        logger.info(f"  Mean:  {results['bleu']['mean']:.4f} ± {results['bleu']['std']:.4f}")
        logger.info(f"  Range: [{results['bleu']['min']:.4f}, {results['bleu']['max']:.4f}]")
        logger.info("")
        logger.info(f"ROUGE Scores:")
        logger.info(f"  ROUGE-1: {results['rouge1']['mean']:.4f} ± {results['rouge1']['std']:.4f}")
        logger.info(f"  ROUGE-2: {results['rouge2']['mean']:.4f} ± {results['rouge2']['std']:.4f}")
        logger.info(f"  ROUGE-L: {results['rougeL']['mean']:.4f} ± {results['rougeL']['std']:.4f}")
        logger.info("="*60 + "\n")
    
    def test_examples(self, num_examples: int = 5):
        """Test model on sample examples."""
        logger.info(f"\nTesting {num_examples} sample generations:")
        logger.info("="*60)
        
        dataset = load_dataset("squad", split="validation")
        dataset = dataset.select(range(num_examples))
        
        for i, example in enumerate(dataset, 1):
            context = example['context']
            reference = example['question']
            generated = self.generate_question(context)
            
            logger.info(f"\nExample {i}:")
            logger.info(f"Context: {context[:200]}...")
            logger.info(f"Reference: {reference}")
            logger.info(f"Generated: {generated}")
            logger.info("-"*60)


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate T5 flashcard generator")
    parser.add_argument(
        "--model_path",
        type=str,
        default="models/flashcard_t5_finetuned",
        help="Path to trained model"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="squad",
        help="Dataset to evaluate on"
    )
    parser.add_argument(
        "--split",
        type=str,
        default="validation",
        help="Dataset split"
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=None,
        help="Maximum samples to evaluate"
    )
    parser.add_argument(
        "--show_examples",
        action="store_true",
        help="Show sample generations"
    )
    parser.add_argument(
        "--num_examples",
        type=int,
        default=5,
        help="Number of examples to show"
    )
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = T5Evaluator(model_path=args.model_path)
    
    # Show examples if requested
    if args.show_examples:
        evaluator.test_examples(num_examples=args.num_examples)
    
    # Run evaluation
    results = evaluator.evaluate_dataset(
        dataset_name=args.dataset,
        split=args.split,
        max_samples=args.max_samples
    )
    
    # Print results
    evaluator.print_results(results)
    
    # Save results
    import json
    results_path = Path(args.model_path) / "evaluation_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to: {results_path}")


if __name__ == "__main__":
    main()
