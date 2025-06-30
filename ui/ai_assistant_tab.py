from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                            QPushButton, QLabel)
from PyQt6.QtCore import Qt
from core.physics_ai import PhysicsMistral, PhysicsInterpreter, SolverOrchestrator

class AIAssistantTab(QWidget):
    def __init__(self):
        super().__init__()
        self.mistral = PhysicsMistral()
        self.interpreter = PhysicsInterpreter()
        self.solver = SolverOrchestrator()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Question input
        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText("Enter your physics question...")
        self.question_input.setMaximumHeight(100)
        
        # Submit button
        submit_btn = QPushButton("Solve")
        submit_btn.clicked.connect(self.solve_question)
        
        # Response display
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        
        # Add widgets to layout
        layout.addWidget(QLabel("Physics Question Solver"))
        layout.addWidget(self.question_input)
        layout.addWidget(submit_btn)
        layout.addWidget(self.response_display)
        
        self.setLayout(layout)

    def solve_question(self):
        question = self.question_input.toPlainText()
        if not question.strip():
            return
            
        try:
            # Step 1: Get AI analysis
            ai_response = self.mistral.analyze_question(question)
            
            # Step 2: Extract variables and module
            variables = self.interpreter.extract_variables(ai_response)
            module = self.interpreter.determine_module(ai_response)
            
            if not module:
                raise ValueError("Could not determine physics module")
            
            # Step 3: Solve using appropriate module
            solution = self.solver.solve(module, variables)
            
            # Format response
            response = f"{ai_response}\n\nCalculated Solution:\n"
            response += "\n".join(f"{k}: {v}" for k, v in solution.items())
            
        except Exception as e:
            response = f"Error: {str(e)}\n\nPlease provide a clear physics question with all required values."
            
        self.response_display.setPlainText(response)
        self.question_input.clear()