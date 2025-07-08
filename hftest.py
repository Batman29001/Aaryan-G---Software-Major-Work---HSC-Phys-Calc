import requests
import sys

API_TOKEN = "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"  # Replace with your actual token

API_URL = "https://api-inference.huggingface.co/models/gpt2"
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

result = generator("Once upon a time in a land far, far away,", max_length=60, num_return_sequences=1)

print(result[0]['generated_text'])



