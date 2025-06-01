from ctransformers import AutoModelForCausalLM  # Replace transformers
import re
import json
from typing import Dict

class LocalAIParser:
    def __init__(self):
        # Use quantized Mistral (4-bit GGUF)
        self.model = AutoModelForCausalLM.from_pretrained(
            "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
            model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            model_type="mistral",
            gpu_layers=0,
            local_files_only=True
        )
        
        self.prompt_template = """[INST]Analyze this HSC physics problem:
{problem}

Return JSON with:
- "topic" (kinematics/dynamics/projectile/etc.)
- "inputs" ({{"variable": value}})
- "target" (variable to find)

Example: {{"topic":"projectile","inputs":{{"u":20,"θ":30}},"target":"range"}}[/INST]"""

    def parse(self, problem: str) -> Dict:
        prompt = self.prompt_template.format(problem=problem)
        response = self.model(prompt, max_new_tokens=200)
        
        try:
            json_str = re.search(r'\{.*\}', response, re.DOTALL).group()
            return json.loads(json_str)
        except:
            raise ValueError("Could not parse physics problem")