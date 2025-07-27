from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, QPoint
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
import random, math

class ParticleBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.initParticles(20)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateParticles)
        self.timer.start(60)

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
        for p in self.particles:
            painter.setPen(QPen(p['color'], p['size']))
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
