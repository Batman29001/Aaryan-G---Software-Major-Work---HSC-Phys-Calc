import io
import qrcode
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class QRCodeDialog(QDialog):
    def __init__(self, uri):
        super().__init__()
        self.setWindowTitle("Scan 2FA QR Code")
        self.setFixedSize(300, 360)
        self.setStyleSheet("background-color: #1E2A38;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Generate QR code
        qr = qrcode.make(uri)
        buf = io.BytesIO()
        qr.save(buf, format='PNG')

        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())

        qr_label = QLabel()
        scaled_pixmap = pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        qr_label.setPixmap(scaled_pixmap)
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        tip_label = QLabel("Scan with Google Authenticator or Authy.")
        tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tip_label.setStyleSheet("color: #B0BEC5; font-size: 12px;")

        close_btn = QPushButton("Done")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4FC3F7;
                color: #1E2A38;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #81D4FA;
            }
        """)
        close_btn.clicked.connect(self.accept)

        layout.addWidget(qr_label)
        layout.addWidget(tip_label)
        layout.addSpacing(10)
        layout.addWidget(close_btn)

        self.setLayout(layout)
