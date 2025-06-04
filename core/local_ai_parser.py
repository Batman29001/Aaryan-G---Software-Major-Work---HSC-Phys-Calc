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
                gpu_layers=0,
                threads=8,
                local_files_only=False
            )
            
            # Strict prompt template with examples
            self.prompt_template = """[INST]Analyze this physics problem:
{problem}

Return JSON with these EXACT keys:
{"topic":"circular/kinematics/etc.","inputs":{"parameter":value},"target":"parameter"}

Use ONLY these parameter names:
m (kg), v (m/s), r (m), θ (°), t (s), a (m/s²), F (N), f (Hz), T (s), q (C), V (V), I (A), R (Ω)

Example for circular motion:
{"topic":"circular","inputs":{"m":3,"v":4,"r":2},"target":"F"}[/INST]"""
            
        except Exception as e:
            raise RuntimeError(f"Model initialization failed: {str(e)}")

    def parse(self, problem: str) -> Dict:
        try:
            prompt = self.prompt_template.format(problem=problem)
            response = self.model(
                prompt,
                max_new_tokens=150,  # Reduced from 200
                temperature=0.1,
                repetition_penalty=1.2
            )
            
            # Fallback if JSON extraction fails
            clean_response = response.strip()
            json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
            if not json_match:
                # Try manual extraction as fallback
                json_str = clean_response.split('{', 1)[-1].rsplit('}', 1)[0]
                json_str = '{' + json_str + '}'
            else:
                json_str = json_match.group()
            
            parsed = json.loads(json_str.replace("'", '"'))
            return parsed
            
        except Exception as e:
            raise ValueError(f"Try rephrasing. Example: '3kg mass, 4m/s speed, 2m radius - find force'")