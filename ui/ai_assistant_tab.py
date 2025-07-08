from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel)
from PyQt6.QtCore import QThread, pyqtSignal
from core.physics_ai.hf_mistral import PhysicsMistral

ENABLE_AI = True 

class AIWorker(QThread):
    finished = pyqtSignal(str)  # Signal to send the AI's response back
    error = pyqtSignal(str)     # Signal for errors

    def __init__(self, mistral, question):
        super().__init__()
        self.mistral = mistral
        self.question = question

    def run(self):
        try:
            response = self.mistral.analyze_question(self.question)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class AIAssistantTab(QWidget):

    def __init__(self):
        super().__init__()
        self.mistral = PhysicsMistral() if ENABLE_AI else None
        self.worker = None  # Track active worker
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

    def validate_ai_response(self, response: str) -> str:
        """Ensure the AI's response contains a 'Final Answer' section."""
        if "**Final Answer:**" not in response:
            return "ERROR: AI failed to follow the required format.\n\nRaw AI Output:\n" + response
        return response

    def solve_question(self):
        if not ENABLE_AI:
            self.response_display.setPlainText("AI feature is disabled")
            return

        if self.worker and self.worker.isRunning():
            return

        question = self.question_input.toPlainText()
        if not question.strip():
            self.response_display.setPlainText("Please enter a question")
            return

        try:
            self.response_display.setPlainText("Processing...")
            self.worker = AIWorker(self.mistral, question)
            self.worker.finished.connect(self.handle_response)
            self.worker.error.connect(self.handle_error)
            self.worker.start()
        except Exception as e:
            self.response_display.setPlainText(f"Initialization error: {str(e)}")


    def handle_response(self, response):
        validated = self.validate_ai_response(response)
        self.response_display.setPlainText(validated)
        self.worker = None  # Reset worker

    def handle_error(self, error_msg):
        self.response_display.setPlainText(f"Error: {error_msg}")
        self.worker = None
        