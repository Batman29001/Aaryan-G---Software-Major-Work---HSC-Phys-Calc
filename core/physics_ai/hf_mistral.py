from gradio_client import Client

class PhysicsMistral:
    def __init__(self):
        # Use your Space's name here
        self.client = Client("BatmanStrikes29001/phi2-api")
        self.system_prompt = """You are a physics expert. When given a question, return the solution with these sections:

**Final Answer:** [value] [unit]  
**Given:**  
- list of known variables  
**Formula:** the main formula used  
**Calculation:** show brief working

Now solve this:"""

    def analyze_question(self, question: str) -> str:
        try:
            prompt = f"{self.system_prompt}\n\nQuestion: {question}"
            # Call the /predict API with the prompt as 'question' input
            response = self.client.predict(prompt, api_name="/predict")
            return response
        except Exception as e:
            return f"Request failed: {e}"
