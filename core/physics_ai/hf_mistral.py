from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class PhysicsMistral:
    def __init__(self):
        # Switch to a smaller model
        self.model_name = "microsoft/phi-2"
        self.tokenizer = None
        self.model = None
        self.system_prompt = """You are a physics expert solving problems. Follow these rules:
        1. **Final Answer**: Format as:  
        **Final Answer:** [value] [unit]  
        2. **Identify Variables**: List all given values with units.
        3. **Use SI Units**: Convert everything to meters, kg, seconds, etc.
        4. **Show Formulas**: Explicitly state the physics formula used, just mention them with as little words as possible.


        Example:
        **Final Answer:** 10 N  
        **Given:**  
        - mass = 5 kg  
        - acceleration = 2 m/s²  
        **Formula:** F = ma  
        **Calculation:** 5 kg * 2 m/s² = 10 N  

        Now solve this:"""

    def analyze_question(self, question):
            if self.model is None:
                self._load_model()

            prompt = f"Instruct: {self.system_prompt}\nQuestion: {question}\nOutput:"
            
            # Tokenize with padding and attention mask
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                return_attention_mask=True
            )
            
            # Move inputs to the correct device (GPU/CPU)
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate response
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=300,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id  # Use EOS token as pad token
            )
            
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def _load_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Set padding token if missing (CRITICAL FIX)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True
            )
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback to CPU if GPU fails
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="cpu",
                torch_dtype=torch.float32,
                trust_remote_code=True
            )
        self.model.eval()