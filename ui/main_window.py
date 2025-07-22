from PyQt6.QtWidgets import (QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont

from ui.kinematics_tab import KinematicsTab
from ui.dynamics_tab import DynamicsTab
from ui.waves_tab import WavesTab
from ui.electricity_magnetism_tab import ElectricityMagnetismTab
from ui.advanced_mechanics_tab import AdvancedMechanicsTab
from ui.electromagnetism_tab import ElectromagnetismTab
from ui.ai_assistant_tab import AIAssistantTab
from ui.global_chat import GlobalChatTab

import random
import math

class ParticleBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.initParticles(35)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateParticles)
        self.timer.start(40)

    def initParticles(self, count):
        for _ in range(count):
            size = random.uniform(1, 2.5)
            speed = random.uniform(0.3, 1.2)
            self.particles.append({
                'x': random.uniform(0, self.width()),
                'y': random.uniform(0, self.height()),
                'size': size,
                'speed': speed,
                'direction': random.uniform(0, 2 * math.pi),
                'color': QColor(79, 195, 247, random.randint(40, 100))
            })

    def resizeEvent(self, event):
        for p in self.particles:
            p['x'] = random.uniform(0, self.width())
            p['y'] = random.uniform(0, self.height())
        super().resizeEvent(event)

    def updateParticles(self):
        for p in self.particles:
            p['x'] += math.cos(p['direction']) * p['speed']
            p['y'] += math.sin(p['direction']) * p['speed']
            if p['x'] < 0: p['x'] = self.width()
            if p['x'] > self.width(): p['x'] = 0
            if p['y'] < 0: p['y'] = self.height()
            if p['y'] > self.height(): p['y'] = 0
            if random.random() < 0.015:
                p['direction'] += random.uniform(-0.3, 0.3)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        dirty_rect = event.rect()
        painter.setClipRect(dirty_rect)

        for p in self.particles:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(p['color']))
            painter.drawEllipse(QPoint(int(p['x']), int(p['y'])), int(p['size']), int(p['size']))

        pen = QPen(QColor(200, 200, 200, 15))
        pen.setWidth(1)
        painter.setPen(pen)
        grid_size = 50
        for x in range(0, self.width(), grid_size):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), grid_size):
            painter.drawLine(0, y, self.width(), y)
        painter.end()

class MainMenu(QWidget):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.background = ParticleBackground(self)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(60, 40, 60, 20)

        title = QLabel(f"Welcome to Phys Calc, {self.username}!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #4FC3F7; padding: 20px;")
        layout.addWidget(title)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("border: 1px solid #2A2A2A;")
        layout.addWidget(separator)

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
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch(1)

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
        layout.addWidget(self.footer)

        self.fact_timer = QTimer(self)
        self.fact_timer.timeout.connect(self.update_footer_fact)
        self.fact_timer.start(8000)

    def resizeEvent(self, event):
        self.background.resize(self.size())
        super().resizeEvent(event)

    def get_random_physics_fact(self):
        facts = [
            "Light travels at ~299,792 km/s in vacuum.",
            "A neutron star's spoonful weighs 10M tons.",
            "Quantum entanglement defies distance.",
            "Time slows in stronger gravity fields.",
            "Superconductors conduct with no resistance.",
            "The universe expands faster every day."
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

        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.kinematics_tab)
        self.stacked_widget.addWidget(self.dynamics_tab)
        self.stacked_widget.addWidget(self.waves_tab)
        self.stacked_widget.addWidget(self.em_tab)
        self.stacked_widget.addWidget(self.advanced_mechanics_tab)
        self.stacked_widget.addWidget(self.electromagnetism_tab)
        self.stacked_widget.addWidget(self.ai_tab)
        self.stacked_widget.addWidget(self.global_chat_tab)

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
