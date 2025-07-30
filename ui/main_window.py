from PyQt6.QtWidgets import (QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ui.kinematics_tab import KinematicsTab
from ui.dynamics_tab import DynamicsTab
from ui.waves_tab import WavesTab
from ui.electricity_magnetism_tab import ElectricityMagnetismTab
from ui.advanced_mechanics_tab import AdvancedMechanicsTab
from ui.electromagnetism_tab import ElectromagnetismTab
from ui.ai_assistant_tab import AIAssistantTab
from ui.global_chat import GlobalChatTab
from ui.user_settings_tab import UserSettingsTab
from ui.particle_background import ParticleBackground
import random

class MainMenu(QWidget):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username

        # Background layer
        self.background = ParticleBackground(self)
        self.background.lower()

        # Main layout on self (MainMenu widget)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Content layer on top of background
        self.content = QWidget(self)
        self.content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.content.setStyleSheet("background: transparent;")  # Let background show through

        self.layout = QVBoxLayout(self.content)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(60, 40, 60, 20)

        self.main_layout.addWidget(self.content)  # Attach content to MainMenu layout
        self.initUI()


    def resizeEvent(self, event):
        self.background.resize(self.size())
        self.content.resize(self.size())

        if hasattr(self.parent(), 'settings_button'):
            self.parent().settings_button.move(
                self.width() - 60,
                self.height() - 70
            )

        super().resizeEvent(event)


    def initUI(self):
        title = QLabel(f"Welcome to Phys Calc, {self.username}!", self.content)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #4FC3F7; padding: 20px;")
        self.layout.addWidget(title)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("border: 1px solid #2A2A2A;")
        self.layout.addWidget(separator)

        self.buttons = []
        button_labels = [
            "Kinematics Calculator",
            "Dynamics Calculator",
            "Waves Calculator",
            "Electricity and Magnetism",
            "Advanced Mechanics",
            "Electromagnetism",
            "AI Physics Solver",
            "Global Chat"
        ]

        for label in button_labels:
            btn = QPushButton(label)
            btn.setMinimumHeight(45)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E2A38;
                    color: #CFD8DC;
                    border: 1px solid #4FC3F7;
                    border-radius: 6px;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #263646;
                }
            """)
            self.layout.addWidget(btn)
            self.buttons.append(btn)

        self.layout.addStretch(1)

        self.footer = QLabel(self.get_random_physics_fact())
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setStyleSheet("""
            QLabel {
                color: #90A4AE;
                font-style: italic;
                padding: 10px;
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
            }
        """)
        self.layout.addWidget(self.footer)

        self.fact_timer = QTimer(self)
        self.fact_timer.timeout.connect(self.update_footer_fact)
        self.fact_timer.start(8000)

    def get_random_physics_fact(self):
        facts = [
            "Light travels at ~299,792 km/s in vacuum.",
            "A neutron star's spoonful weighs 10M tons.",
            "Quantum entanglement defies distance.",
            "Time slows in stronger gravity fields.",
            "Superconductors conduct with no resistance.",
            "The universe expands faster every day.",
            "Mitochondria is the powerhouse of the cell", 
            "Newton was celibate his whole life he got no play. Kinda like you lmao  ", 
            "nigger"
        ]
        return random.choice(facts)

    def update_footer_fact(self):
        self.footer.setText(self.get_random_physics_fact())



class PhysicsCalculator(QMainWindow):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.setWindowTitle("HSC Physics Calculator")
        self.setGeometry(100, 100, 1000, 700)

        self.stacked_widget = QStackedWidget()
        username = self.auth_manager.current_user[1] if self.auth_manager.current_user else "User"
        self.main_menu = MainMenu(username)
        self.kinematics_tab = KinematicsTab()
        self.dynamics_tab = DynamicsTab()
        self.waves_tab = WavesTab()
        self.em_tab = ElectricityMagnetismTab()
        self.advanced_mechanics_tab = AdvancedMechanicsTab()
        self.electromagnetism_tab = ElectromagnetismTab()
        self.ai_tab = AIAssistantTab()
        self.global_chat_tab = GlobalChatTab(self.auth_manager)
        self.user_settings_tab = UserSettingsTab(self.auth_manager, return_callback=self.return_to_menu)

        self.stacked_widget.addWidget(self.main_menu)
        self.settings_button = QPushButton("⚙")
        self.settings_button.setFixedSize(45, 45)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #1E2A38;
                color: #4FC3F7;
                font-size: 20px;
                border: 1px solid #4FC3F7;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #263646;
            }
        """)
        self.settings_button.setParent(self.main_menu)
        self.settings_button.raise_() 
        self.settings_button.clicked.connect(lambda: self.switch_to_calculator(9))
        self.stacked_widget.addWidget(self.kinematics_tab)
        self.stacked_widget.addWidget(self.dynamics_tab)
        self.stacked_widget.addWidget(self.waves_tab)
        self.stacked_widget.addWidget(self.em_tab)
        self.stacked_widget.addWidget(self.advanced_mechanics_tab)
        self.stacked_widget.addWidget(self.electromagnetism_tab)
        self.stacked_widget.addWidget(self.ai_tab)
        self.stacked_widget.addWidget(self.global_chat_tab)
        self.stacked_widget.addWidget(self.user_settings_tab)

        for i, btn in enumerate(self.main_menu.buttons):
            btn.clicked.connect(self.make_switch_callback(i + 1))

        self.setCentralWidget(self.stacked_widget)
        self.stacked_widget.setCurrentIndex(0)

    def make_switch_callback(self, index):
        return lambda: self.switch_to_calculator(index)

    def switch_to_calculator(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def return_to_menu(self):
        self.switch_to_calculator(0)

    
