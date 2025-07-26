from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import QTimer, Qt, QSize, QPoint
from PyQt6.QtGui import QTextCursor, QColor, QPainter, QPen, QBrush

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

class GlobalChatTab(QWidget):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager

        self.background = ParticleBackground(self)
        self.background.lower()

        self.setup_ui()
        self.load_messages()

        # Don't start timer immediately - only when tab is visible
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_messages)
        self.timer_running = False

    def resizeEvent(self, event):
        self.background.resize(self.size())
        super().resizeEvent(event)

    def showEvent(self, event):
        """Start timer when tab becomes visible"""
        super().showEvent(event)
        if not self.timer_running:
            self.timer.start(2000)
            self.timer_running = True

    def hideEvent(self, event):
        """Stop timer when tab is hidden"""
        super().hideEvent(event)
        if self.timer_running:
            self.timer.stop()
            self.timer_running = False

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 20)
        layout.setSpacing(15)

        title = QLabel("Welcome to the Global Chat Server!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #4FC3F7;
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1E2A38;
                color: #E0F7FA;
                border: 1px solid #4FC3F7;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        self.chat_display.setMinimumHeight(400)
        layout.addWidget(self.chat_display)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #263646;
                color: #CFD8DC;
                border: 1px solid #4FC3F7;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #81D4FA;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.message_input)

        self.send_btn = QPushButton("Send")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setStyleSheet("""
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
        self.send_btn.clicked.connect(self.send_message)
        layout.addWidget(self.send_btn)

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
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def return_to_menu(self):
        self.parent().parent().return_to_menu()

    def append_system_message(self, text):
        self.chat_display.append(
            f'<div style="color: #90A4AE; font-style: italic; margin: 2px 0;">{text}</div>'
        )

    def load_messages(self):
        try:
            messages = self.auth_manager.get_global_messages()
            current_scroll = self.chat_display.verticalScrollBar().value()
            at_bottom = self.chat_display.verticalScrollBar().value() == self.chat_display.verticalScrollBar().maximum()

            self.chat_display.clear()
            for msg in messages:
                self.chat_display.append(
                    f'<div style="margin: 4px 0;">'
                    f'<span style="font-weight: bold; color: #4FC3F7;">{msg["username"]}</span>'
                    f'<span style="color: #90A4AE; font-size: 12px; margin-left: 6px;">{msg["timestamp"]}</span>'
                    f'<div style="color: #E0F7FA; margin-top: 2px;">{msg["message"]}</div>'
                    f'</div>'
                )

            if at_bottom:
                self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
            else:
                self.chat_display.verticalScrollBar().setValue(current_scroll)

        except Exception as e:
            self.append_system_message(f"Error loading messages: {str(e)}")

    def send_message(self):
        if not hasattr(self.auth_manager, 'current_user') or not self.auth_manager.current_user:
            self.append_system_message("Please login to send messages")
            return

        message = self.message_input.text().strip()
        if message:
            try:
                user = self.auth_manager.current_user
                self.auth_manager.save_global_message(user[0], user[1], message)
                self.message_input.clear()
                self.load_messages()
            except Exception as e:
                self.append_system_message(f"Error sending message: {str(e)}")
