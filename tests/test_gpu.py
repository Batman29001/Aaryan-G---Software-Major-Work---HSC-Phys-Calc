import torch
from ctransformers import AutoModelForCausalLM

print("CUDA available:", torch.cuda.is_available())
model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
    model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    gpu_layers=50 if torch.cuda.is_available() else 0
)
print("Model loaded successfully!")