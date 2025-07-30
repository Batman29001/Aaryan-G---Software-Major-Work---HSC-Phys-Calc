from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
)
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from core.physics_ai.hf_mistral import PhysicsMistral
from ui.particle_background import ParticleBackground

ENABLE_AI = True

class ModelLoaderWorker(QThread):
    finished = pyqtSignal(object)  # Emits the loaded model
    error = pyqtSignal(str)  # Emits error message

    def __init__(self):
        super().__init__()
        self.model = None

    def run(self):
        try:
            self.model = PhysicsMistral()
            self.finished.emit(self.model)
        except Exception as e:
            self.error.emit(str(e))


class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

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
        self.mistral = None  # Don't load model immediately
        self.worker = None
        self.model_loader = None

        self.background = ParticleBackground(self)
        self.background.lower()

        self.init_ui()

    def resizeEvent(self, event):
        self.background.resize(self.size())
        super().resizeEvent(event)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Welcome to your personal Physics AI assistant!")
        title.setStyleSheet("""
            QLabel {
                color: #4FC3F7;
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Question input
        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText("Enter your physics question...")
        self.question_input.setMaximumHeight(100)
        self.question_input.setStyleSheet("""
            QTextEdit {
                background-color: #1E2A38;
                color: #CFD8DC;
                border: 1px solid #4FC3F7;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.question_input)

        # Solve button
        submit_btn = QPushButton("Solve")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #263646;
                color: #CFD8DC;
                border: 1px solid #4FC3F7;
                border-radius: 6px;
                padding: 8px 18px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2F4254;
            }
        """)
        submit_btn.clicked.connect(self.solve_question)
        layout.addWidget(submit_btn)

        # Response display
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        self.response_display.setStyleSheet("""
            QTextEdit {
                background-color: #1E2A38;
                color: #90A4AE;
                border: 1px solid #4FC3F7;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.response_display)

        # Back button
        back_btn = QPushButton("← Back to Menu")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setFixedWidth(140)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #263646;
                color: #CFD8DC;
                border: 1px solid #4FC3F7;
                border-radius: 6px;
                font-size: 13px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2F4254;
            }
        """)
        back_btn.clicked.connect(self.return_to_menu)
        layout.addWidget(back_btn)

    def return_to_menu(self):
        from ui.main_window import PhysicsCalculator
        if hasattr(self.parent(), 'parent') and hasattr(self.parent().parent(), 'return_to_menu'):
            self.parent().parent().return_to_menu()

    def validate_ai_response(self, response: str) -> str:
        if "**Final Answer:**" not in response:
            return "ERROR: AI failed to follow the required format.\n\nRaw AI Output:\n" + response
        return response

    def solve_question(self):
        if not ENABLE_AI:
            self.response_display.setPlainText("AI feature is disabled")
            return

        question = self.question_input.toPlainText()
        if not question.strip():
            self.response_display.setPlainText("Please enter a question")
            return

        # If model is not loaded, load it in background thread
        if self.mistral is None:
            self.response_display.setPlainText("Loading AI model... This may take a moment on first use.")
            
            # Stop any existing model loader
            if self.model_loader and self.model_loader.isRunning():
                self.model_loader.quit()
                self.model_loader.wait()
            
            # Start model loading in background
            self.model_loader = ModelLoaderWorker()
            self.model_loader.finished.connect(self.on_model_loaded)
            self.model_loader.error.connect(self.on_model_error)
            self.model_loader.start()
            return

        # Model is loaded, proceed with question
        self.process_question(question)

    def on_model_loaded(self, model):
        """Called when AI model finishes loading"""
        self.mistral = model
        self.response_display.setPlainText("AI model loaded! Processing your question...")
        
        # Now process the question that was waiting
        question = self.question_input.toPlainText()
        if question.strip():
            self.process_question(question)

    def on_model_error(self, error_msg):
        """Called when AI model loading fails"""
        self.response_display.setPlainText(f"Error loading AI model: {error_msg}")

    def process_question(self, question):
        """Process the question with the loaded model"""
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()

        try:
            if self.worker and self.worker.isRunning():
                self.worker.quit()
                self.worker.wait()
            self.response_display.setPlainText("Processing...")
            self.worker = AIWorker(self.mistral, question)
            self.worker.finished.connect(self.handle_response)
            self.worker.error.connect(self.handle_error)
            self.worker.start()
        except Exception as e:
            self.response_display.setPlainText(f"Error: {str(e)}")

    def handle_response(self, response):
        validated = self.validate_ai_response(response)
        self.response_display.setPlainText(validated)
        self.worker = None

    def handle_error(self, error_msg):
        self.response_display.setPlainText(f"Error: {error_msg}")
        self.worker = None

    def closeEvent(self, event):
        try:
            if self.worker and self.worker.isRunning():
                self.worker.quit()
                self.worker.wait()
                self.worker = None

            if self.model_loader and self.model_loader.isRunning():
                self.model_loader.quit()
                self.model_loader.wait()
        except Exception as e:
            print(f"Error during closeEvent: {e}")
        event.accept()


