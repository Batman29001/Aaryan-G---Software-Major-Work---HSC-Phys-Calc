from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict
from huggingface_hub import login
login(token="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")
import torch
import re
import json


class LocalAIParser:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
        self.model = AutoModelForCausalLM.from_pretrained(
            "mistralai/Mistral-7B-Instruct-v0.1",
            device_map="auto",
            torch_dtype=torch.float16
        )
        self.prompt_template = """[INST] Analyze this HSC physics problem:
{problem}

Extract as JSON with:
- "topic" (kinematics/dynamics/projectile/circular/electrostatics/etc.)
- "inputs" ({{"variable": value}})
- "target" (variable to find)

Example:
{{
  "topic": "projectile",
  "inputs": {{"u": 20, "θ": 30}},
  "target": "range"
}}[/INST]"""

    def parse(self, problem: str) -> Dict:
        prompt = self.prompt_template.format(problem=problem)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.1
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON from response
        try:
            json_str = re.search(r'\{.*\}', response, re.DOTALL).group()
            return json.loads(json_str)
        except:
            raise ValueError("Failed to parse AI response")