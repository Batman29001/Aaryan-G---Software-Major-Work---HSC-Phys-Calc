# core/physics_ai/hf_mistral.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class PhysicsMistral:
    def __init__(self):
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.1"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="cpu",
            torch_dtype=torch.float32,
        )
        self.system_prompt = """You are a physics expert solving HSC-level problems. 
        Analyze questions to identify:
        1. All given variables with values
        2. The unknown variable(s) to find
        3. Which physics module to use (kinematics, dynamics, waves, etc.)
        4. The appropriate formulas in correct order
        
        Always structure your response with:
        - Thought Process: [your analysis]
        - Variables Identified: [list]
        - Module Selected: [module name]
        - Solution Steps: [ordered steps]
        - Final Answer: [value with units]"""

    def analyze_question(self, question):
        prompt = f"<s>[INST] {self.system_prompt}\nQuestion: {question} [/INST]"
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cpu")  # Changed to CPU
        outputs = self.model.generate(**inputs, max_new_tokens=500)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)