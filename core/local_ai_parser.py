from ctransformers import AutoModelForCausalLM
import re
import json
from typing import Dict

class LocalAIParser:
    def __init__(self):
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
                model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
                model_type="mistral",
                gpu_layers=0,  # Force CPU-only
                threads=8,     # Use all CPU cores
                local_files_only=False
            )
            
            self.prompt_template = """[INST]Analyze this physics problem:
{problem}

Return JSON with:
- "topic" (kinematics/dynamics/projectile/etc.)
- "inputs" ({{"variable": value}})
- "target" (variable to find)

Example: {{"topic":"projectile","inputs":{{"velocity":20,"angle":30}},"target":"range"}}[/INST]"""
            
        except Exception as e:
            raise RuntimeError(f"Model initialization failed: {str(e)}")

    def parse(self, problem: str) -> Dict:
        try:
            response = self.model(
                self.prompt_template.format(problem=problem),
                max_new_tokens=150,
                temperature=0.3,
                repetition_penalty=1.1
            )
            json_str = re.search(r'\{[^{}]*\}', response).group()
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Parsing failed: {str(e)}")