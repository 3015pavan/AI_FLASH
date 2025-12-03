# T5 Flashcard Model

## Status
Production Ready

## Features
- PDF upload support
- Text input support
- Automatic flashcard generation
- Answer validation
- JSON export

## Usage
The model is automatically used by the Streamlit app.
Simply run: `streamlit run app.py --server.port=8501`

## Model Info
- Base: T5-small (pre-trained)
- Tasks: Question Answering, Flashcard Generation
- Input: Any text or PDF document
- Output: Question-Answer pairs
