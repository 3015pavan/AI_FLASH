"""
Training Script for T5 Flashcard Generator
==========================================
Fine-tunes T5 model on SQuAD dataset for question generation.

Usage:
    python scripts/train.py --epochs 5 --batch_size 16
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
from torch.utils.data import DataLoader
from transformers import (
    T5Tokenizer,
    T5ForConditionalGeneration,
    AdamW,
    get_linear_schedule_with_warmup
)
from datasets import load_dataset
from tqdm import tqdm
import logging

from config.model_config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class T5Trainer:
    """Trainer class for fine-tuning T5 on SQuAD dataset."""
    
    def __init__(self, model_name: str = "t5-base"):
        """Initialize trainer with model and tokenizer."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
        
        logger.info(f"Loaded model: {model_name}")
        logger.info(f"Model parameters: {self.model.num_parameters():,}")
    
    def prepare_data(self, split: str = "train", max_samples: int = None):
        """
        Load and prepare SQuAD dataset.
        
        Args:
            split: Dataset split ('train', 'validation')
            max_samples: Limit number of samples (for testing)
        """
        logger.info(f"Loading SQuAD dataset - {split} split")
        dataset = load_dataset("squad", split=split)
        
        if max_samples:
            dataset = dataset.select(range(max_samples))
        
        logger.info(f"Loaded {len(dataset)} examples")
        return dataset
    
    def preprocess_function(self, examples):
        """
        Preprocess data into T5 format.
        Input: "generate question: <context>"
        Output: "<question>"
        """
        inputs = []
        targets = []
        
        for context, question in zip(examples['context'], examples['question']):
            # T5 expects text-to-text format
            input_text = f"generate question: {context}"
            target_text = question
            
            inputs.append(input_text)
            targets.append(target_text)
        
        # Tokenize inputs
        model_inputs = self.tokenizer(
            inputs,
            max_length=config.max_input_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Tokenize targets
        labels = self.tokenizer(
            targets,
            max_length=config.max_output_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
    
    def train(
        self,
        train_dataset,
        val_dataset=None,
        epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 1e-4,
        save_dir: str = "models/flashcard_t5_finetuned"
    ):
        """
        Train the model.
        
        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            save_dir: Directory to save model checkpoints
        """
        logger.info("Starting training...")
        
        # Prepare data
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True
        )
        
        # Setup optimizer
        optimizer = AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=config.get_training_config()['weight_decay']
        )
        
        # Setup scheduler
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=config.get_training_config()['warmup_steps'],
            num_training_steps=total_steps
        )
        
        # Training loop
        self.model.train()
        global_step = 0
        
        for epoch in range(epochs):
            logger.info(f"\nEpoch {epoch + 1}/{epochs}")
            epoch_loss = 0
            
            progress_bar = tqdm(train_loader, desc=f"Training Epoch {epoch + 1}")
            
            for batch in progress_bar:
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                epoch_loss += loss.item()
                
                # Backward pass
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    config.get_training_config()['max_grad_norm']
                )
                
                # Update weights
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                
                global_step += 1
                
                # Update progress bar
                progress_bar.set_postfix({
                    'loss': f"{loss.item():.4f}",
                    'lr': f"{scheduler.get_last_lr()[0]:.2e}"
                })
            
            avg_loss = epoch_loss / len(train_loader)
            logger.info(f"Epoch {epoch + 1} - Average Loss: {avg_loss:.4f}")
            
            # Validation
            if val_dataset:
                val_loss = self.evaluate(val_dataset, batch_size)
                logger.info(f"Validation Loss: {val_loss:.4f}")
            
            # Save checkpoint
            checkpoint_dir = Path(save_dir) / f"checkpoint-epoch-{epoch + 1}"
            self.save_model(checkpoint_dir)
        
        logger.info("Training complete!")
        
        # Save final model
        self.save_model(save_dir)
    
    def evaluate(self, dataset, batch_size: int = 16):
        """Evaluate model on validation set."""
        self.model.eval()
        
        val_loader = DataLoader(dataset, batch_size=batch_size)
        total_loss = 0
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Evaluating"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                total_loss += outputs.loss.item()
        
        self.model.train()
        return total_loss / len(val_loader)
    
    def save_model(self, save_dir: str):
        """Save model and tokenizer."""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        
        logger.info(f"Model saved to {save_path}")


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train T5 for flashcard generation")
    parser.add_argument("--model_name", type=str, default="t5-base", help="Base model name")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--learning_rate", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--max_samples", type=int, default=None, help="Limit samples (for testing)")
    parser.add_argument("--save_dir", type=str, default="models/flashcard_t5_finetuned", help="Save directory")
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = T5Trainer(model_name=args.model_name)
    
    # Load data
    train_dataset = trainer.prepare_data("train", max_samples=args.max_samples)
    val_dataset = trainer.prepare_data("validation", max_samples=args.max_samples)
    
    # Preprocess data
    logger.info("Preprocessing data...")
    train_dataset = train_dataset.map(
        trainer.preprocess_function,
        batched=True,
        remove_columns=train_dataset.column_names
    )
    val_dataset = val_dataset.map(
        trainer.preprocess_function,
        batched=True,
        remove_columns=val_dataset.column_names
    )
    
    # Train
    trainer.train(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        save_dir=args.save_dir
    )


if __name__ == "__main__":
    main()
