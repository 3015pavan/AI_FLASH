"""
Training script for T5 model on SQuAD v1.1 dataset for flashcard generation
"""

import os
import json
import logging
from pathlib import Path
import numpy as np
import torch
from datasets import load_dataset, DatasetDict
from transformers import (
    T5Tokenizer, T5ForConditionalGeneration,
    Trainer, TrainingArguments,
    DataCollatorForSeq2Seq
)
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check GPU availability
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Using device: {DEVICE}")


def load_and_prepare_squad():
    """
    Load SQuAD v1.1 dataset and prepare it for training.
    
    Returns:
        Prepared dataset with train/validation split
    """
    logger.info("Loading SQuAD v1.1 dataset...")
    
    # Load dataset
    dataset = load_dataset('squad', split='train')
    
    # Create custom train/validation split
    split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
    
    return split_dataset


def preprocess_function(examples, tokenizer, max_source_length=512, max_target_length=128):
    """
    Preprocess examples for training.
    
    Args:
        examples: Batch of examples from dataset
        tokenizer: T5 tokenizer
        max_source_length: Maximum source length
        max_target_length: Maximum target length
        
    Returns:
        Tokenized inputs and labels
    """
    # Create input text: "flashcard: <context>"
    inputs = [f"flashcard: {context}" for context in examples['context']]
    
    # Create target text: "<question> <sep> <answer>"
    targets = [f"{q} <sep> {a}" for q, a in zip(examples['question'], examples['answers'])]
    
    # Handle multiple answers - take first one
    final_targets = []
    for target_list in targets:
        parts = target_list.split('<sep>')
        if len(parts) == 2:
            question = parts[0].strip()
            answers_part = parts[1].strip()
            # answers_part contains dictionary representation, extract text_key
            final_targets.append(f"{question} <sep> {answers_part}")
        else:
            final_targets.append(target_list)
    
    # Actually process as proper flashcard format
    processed_targets = []
    for q, ans_dict in zip(examples['question'], examples['answers']):
        # Extract first answer text
        if isinstance(ans_dict.get('text'), list) and len(ans_dict['text']) > 0:
            answer = ans_dict['text'][0]
        else:
            answer = ans_dict.get('text', '')
        processed_targets.append(f"{q} <sep> {answer}")
    
    # Tokenize inputs
    model_inputs = tokenizer(
        inputs, 
        max_length=max_source_length, 
        truncation=True,
        padding='max_length'
    )
    
    # Tokenize targets
    labels = tokenizer(
        processed_targets,
        max_length=max_target_length,
        truncation=True,
        padding='max_length'
    )
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def train_model():
    """
    Main training loop for T5 model on SQuAD dataset.
    """
    logger.info("Starting T5 model training...")
    
    # Create output directory
    output_dir = Path('flashcard_t5')
    output_dir.mkdir(exist_ok=True)
    
    # Load model and tokenizer
    logger.info("Loading T5-small model and tokenizer...")
    model_name = 't5-small'
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    
    # Add special token for separation
    special_tokens_dict = {'additional_special_tokens': ['<sep>']}
    tokenizer.add_special_tokens(special_tokens_dict)
    model.resize_token_embeddings(len(tokenizer))
    
    logger.info(f"Model moved to device: {DEVICE}")
    model.to(DEVICE)
    
    # Load and prepare dataset
    logger.info("Preparing SQuAD dataset...")
    dataset = load_and_prepare_squad()
    
    # Preprocess dataset
    logger.info("Preprocessing dataset...")
    processed_dataset = dataset.map(
        lambda x: preprocess_function(x, tokenizer),
        batched=True,
        remove_columns=['id', 'title', 'context', 'question', 'answers'],
        batch_size=32
    )
    
    logger.info(f"Training set size: {len(processed_dataset['train'])}")
    logger.info(f"Validation set size: {len(processed_dataset['test'])}")
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(output_dir / 'checkpoints'),
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=str(output_dir / 'logs'),
        logging_steps=100,
        eval_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='eval_loss',
        greater_is_better=False,
        gradient_accumulation_steps=2,
        learning_rate=5e-5,
        seed=42,
    )
    
    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer,
        model=model,
        label_pad_token_id=tokenizer.pad_token_id
    )
    
    # Initialize trainer
    logger.info("Initializing trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=processed_dataset['train'],
        eval_dataset=processed_dataset['test'],
        data_collator=data_collator,
    )
    
    # Train model
    logger.info("Starting training...")
    trainer.train()
    
    # Save final model and tokenizer
    logger.info(f"Saving model and tokenizer to {output_dir}...")
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    
    # Save training metadata
    metadata = {
        'model_name': model_name,
        'source_dataset': 'SQuAD v1.1',
        'special_tokens': ['<sep>'],
        'training_epochs': 3,
        'device': str(DEVICE)
    }
    
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info("Training completed successfully!")
    logger.info(f"Model saved at: {output_dir}")
    
    return model, tokenizer


if __name__ == '__main__':
    train_model()
