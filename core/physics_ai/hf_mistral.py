# core/physics_ai/hf_mistral.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class PhysicsMistral:
    def __init__(self):
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.1"
        self.tokenizer = None #lazy load
        self.model = None #lazy load
        self.system_prompt = """You are a physics expert solving problems. Follow these rules:
        1. **Identify Variables**: List all given values with units (e.g., "mass = 5 kg").
        2. **Use SI Units**: Convert everything to meters, kg, seconds, etc.
        3. **Show Formulas**: Explicitly state the physics formula used.
        4. **Final Answer**: Format as:  
        **Final Answer:** [value] [unit]  

        Example:
        **Given:**  
        - mass = 5 kg  
        - acceleration = 2 m/s²  
        **Formula:** F = ma  
        **Calculation:** 5 kg * 2 m/s² = 10 N  
        **Final Answer:** 10 N  

        Now solve this:"""

    def analyze_question(self, question):
        if self.model is None:  # Loads only when first used
            self._load_model()

        prompt = f"<s>[INST] {self.system_prompt}\nQuestion: {question} [/INST]"
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)  
        outputs = self.model.generate(**inputs, max_new_tokens=500)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def _load_model(self):
        """Load model on first use to avoid startup delay."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",       # Uses GPU if available
            torch_dtype=torch.float16,  # Faster on GPU
            low_cpu_mem_usage=True,
        )