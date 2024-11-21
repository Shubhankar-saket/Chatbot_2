#!/bin/bash
# Install SpaCy model before running the app
python -m spacy download en_core_web_sm
# Run the app with Gunicorn
gunicorn app:app

