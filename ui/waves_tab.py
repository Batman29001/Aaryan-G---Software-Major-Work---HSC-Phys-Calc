from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QGroupBox, QFormLayout,
                            QMessageBox, QComboBox, QTabWidget)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from core.waves import (solve_wave_properties, solve_sound_waves, solve_light_properties,
                       InputValidationError, InsufficientDataError, PhysicsConfigurationError)
from PyQt6.QtGui import QFont, QColor
from matplotlib.patches import ArrowStyle
import math

class BaseWaveTab(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.last_result = None
        self.title = title
        self.initUI()
    
    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Left panel for inputs
        input_panel = QGroupBox(self.title)
        input_layout = QFormLayout()
        
        # Create input fields
        self.create_input_fields(input_layout)
        
        # Buttons
        self.calculate_btn = QPushButton("🚀 Calculate")
        self.clear_btn = QPushButton("🔄 Reset")
        self.plot_btn = QPushButton("📊 Plot")
        self.theme_btn = QPushButton("🌙 Toggle Plot Theme")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.calculate_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.plot_btn)
        button_layout.addWidget(self.theme_btn)
        
        # Results display
        self.result_display = QLabel("Results will appear here...")
        self.result_display.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.result_display.setWordWrap(True)
        
        input_layout.addRow(button_layout)
        input_layout.addRow(self.result_display)
        
        # Right panel for plot
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        
        # Add panels to main layout
        input_panel.setLayout(input_layout)
        main_layout.addWidget(input_panel, 1)
        main_layout.addWidget(self.canvas, 1)
        
        self.setLayout(main_layout)
        self.apply_style()
        self.connect_signals()
    
    def create_input_fields(self, layout):
        """To be implemented by subclasses"""
        pass
    
    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #222222;
                color: #EEEEEE;
                font-family: Segoe UI, Arial;
            }
            QGroupBox {
                font: bold 14px;
                border: 2px solid #3A7CA5;
                border-radius: 5px;
                margin-top: 1ex;
                background-color: #333333;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #3A7CA5;
            }
            QPushButton {
                background-color: #3A7CA5;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2F6690;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QLineEdit, QComboBox {
                border: 1px solid #3A7CA5;
                padding: 5px;
                border-radius: 3px;
                background-color: #444444;
                color: white;
                selection-background-color: #3A7CA5;
            }
            QLabel {
                color: #EEEEEE;
                font-size: 13px;
            }
        """)
        self.update_plot_theme()
    
    def update_plot_theme(self):
        if self.dark_mode:
            self.ax.set_facecolor('#2F2F2F')
            self.figure.set_facecolor('#2F2F2F')
            for text in [self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label] + self.ax.texts:
                text.set_color('#EEEEEE')
            self.ax.grid(color='#444444')
        else:
            self.ax.set_facecolor('#F8F9FA')
            self.figure.set_facecolor('#F8F9FA')
            for text in [self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label] + self.ax.texts:
                text.set_color('#333333')
            self.ax.grid(color='#DDDDDD')
        self.canvas.draw()
    
    def connect_signals(self):
        self.calculate_btn.clicked.connect(self.calculate)
        self.clear_btn.clicked.connect(self.clear_fields)
        self.plot_btn.clicked.connect(self.plot)
        self.theme_btn.clicked.connect(self.toggle_theme)
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme_btn.setText("☀️ Light Plot" if self.dark_mode else "🌙 Dark Plot")
        self.update_plot_theme()
    
    def calculate(self):
        """To be implemented by subclasses"""
        pass
    
    def get_input_values(self):
        values = {}
        for var, field in self.inputs.items():
            text = field.text().strip()
            try:
                values[var] = float(text) if text else None
            except ValueError:
                values[var] = None
        return values
    
    def clear_fields(self):
        for field in self.inputs.values():
            field.clear()
        self.result_display.setText("Results will appear here...")
        self.last_result = None
        self.ax.clear()
        self.update_plot_theme()
        self.canvas.draw()
    
    def plot(self):
        """To be implemented by subclasses"""
        pass

    def handle_calculation_error(self, e: Exception) -> str:
        """Convert core physics exceptions to user-friendly messages"""
        if isinstance(e, InputValidationError):
            return f"Invalid input: {str(e)}"
        elif isinstance(e, InsufficientDataError):
            return f"Missing required data: {str(e)}"
        elif isinstance(e, PhysicsConfigurationError):
            return f"Physical impossibility: {str(e)}"
        elif "Division by zero" in str(e):
            return "Calculation error: Division by zero occurred (check your inputs)"
        elif "Maximum iterations reached" in str(e):
            return "Calculation didn't converge - check if inputs are physically possible"
        elif "invalid value" in str(e).lower():
            return "Invalid value encountered in calculations"
        else:
            return f"Calculation error: {str(e)}"


class WavePropertiesTab(BaseWaveTab):
    def __init__(self, parent=None):
        super().__init__("Wave Properties Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'v': ["m/s", "km/s"],
            'f': ["Hz", "kHz", "MHz"],
            'λ': ["m", "cm", "nm"],
            'T': ["s", "ms", "μs"],
            'ω': ["rad/s"],
            'k': ["rad/m"]
        }
        
        symbols = {
            'v': "v (Wave velocity)",
            'f': "f (Frequency)",
            'λ': "λ (Wavelength)",
            'T': "T (Period)",
            'ω': "ω (Angular frequency)",
            'k': "k (Wave number)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['v', 'f', 'λ', 'T', 'ω', 'k']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def calculate(self):
        values = self.get_input_values()
        try:
            result = solve_wave_properties(**values)
            self.last_result = result
            
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3f}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['f', 'λ']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need frequency and wavelength to plot wave.")
            return
        
        f, λ = result['f'], result['λ']
        
        # Create wave data
        x = np.linspace(0, 3*λ, 1000)
        t = 1/f  # One period
        y = np.sin(2 * np.pi * (x/λ - f * 0))  # Wave at t=0
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Plot wave
        self.ax.plot(x, y, color='#2E86AB', linewidth=2, label=f'Wave (f={f:.1f} Hz, λ={λ:.2f} m)')
        
        # Mark wavelength
        if λ > 0:
            self.ax.annotate('', xy=(0, 1.1), xytext=(λ, 1.1),
                           arrowprops=dict(arrowstyle='<->', color='#D62246'))
            self.ax.text(λ/2, 1.15, f'λ = {λ:.2f} m', ha='center', color='#D62246')
        
        # Add labels
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Amplitude')
        self.ax.set_title('Waveform Visualization')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class SoundWavesTab(BaseWaveTab):
    def __init__(self, parent=None):
        super().__init__("Sound Waves Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'f_observed': ["Hz", "kHz"],
            'f_source': ["Hz", "kHz"],
            'v_source': ["m/s", "km/h"],
            'v_observer': ["m/s", "km/h"],
            'v_medium': ["m/s"],
            'θ_source': ["°"],
            'θ_observer': ["°"]
        }
        
        symbols = {
            'f_observed': "f' (Observed frequency)",
            'f_source': "f (Source frequency)",
            'v_source': "vₛ (Source velocity)",
            'v_observer': "vₒ (Observer velocity)",
            'v_medium': "v (Speed of sound)",
            'θ_source': "θₛ (Source angle)",
            'θ_observer': "θₒ (Observer angle)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['f_observed', 'f_source', 'v_source', 'v_observer', 'v_medium', 'θ_source', 'θ_observer']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def calculate(self):
        values = self.get_input_values()
        try:
            result = solve_sound_waves(**values)
            self.last_result = result
            
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3f}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['f_source', 'v_source', 'f_observed']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need source frequency, source velocity, and observed frequency to plot Doppler effect.")
            return
        
        f_source = result['f_source']
        f_observed = result['f_observed']
        v_source = result['v_source']
        
        # Create source positions
        positions = np.linspace(-100, 100, 400)
        times = np.linspace(0, 1, 100)
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Plot source and observer
        self.ax.plot([0], [0], 'bo', markersize=10, label='Observer')
        
        # Plot source positions and waves
        for t in times[::5]:  # Plot every 5th time step
            x_source = v_source * t
            self.ax.plot([x_source], [0], 'ro', markersize=5, alpha=0.3)
            
            # Plot wavefronts
            r = 343 * t  # Wave radius
            circle = plt.Circle((x_source, 0), r, color='r', fill=False, alpha=0.1)
            self.ax.add_artist(circle)
        
        # Add annotations
        self.ax.text(0.02, 0.95, 
                    f"Source: {f_source:.1f} Hz\nObserved: {f_observed:.1f} Hz\nShift: {f_observed-f_source:.1f} Hz",
                    transform=self.ax.transAxes,
                    bbox=dict(facecolor='white' if not self.dark_mode else '#444444',
                             alpha=0.8, edgecolor='none'))
        
        # Set axis limits
        self.ax.set_xlim(-120, 120)
        self.ax.set_ylim(-120, 120)
        self.ax.set_aspect('equal')
        
        # Add labels
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Position (m)')
        self.ax.set_title('Doppler Effect Visualization')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class LightPropertiesTab(BaseWaveTab):
    def __init__(self, parent=None):
        super().__init__("Light Properties Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'n1': ["unitless"],
            'n2': ["unitless"],
            'θ1': ["°"],
            'θ2': ["°"],
            'I1': ["W/m²", "lux"],
            'I2': ["W/m²", "lux"]
        }
        
        symbols = {
            'n1': "n₁ (Refractive index 1)",
            'n2': "n₂ (Refractive index 2)",
            'θ1': "θ₁ (Incident angle)",
            'θ2': "θ₂ (Refracted angle)",
            'I1': "I₁ (Incident intensity)",
            'I2': "I₂ (Transmitted intensity)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['n1', 'n2', 'θ1', 'θ2', 'I1', 'I2']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def calculate(self):
        values = self.get_input_values()
        try:
            result = solve_light_properties(**values)
            self.last_result = result
            
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3f}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['n1', 'n2', 'θ1']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need n₁, n₂, and θ₁ to plot refraction.")
            return
        
        n1, n2, θ1 = result['n1'], result['n2'], result['θ1']
        
        # Calculate θ2 if not provided
        θ2 = result.get('θ2')
        if θ2 is None:
            try:
                θ2 = math.degrees(math.asin((n1 * math.sin(math.radians(θ1))) / n2))
            except:
                θ2 = 90  # Total internal reflection case
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Draw interface
        self.ax.axhline(0, color='k', linestyle='-', linewidth=1)
        self.ax.text(0.5, 0.02, f"n₁ = {n1:.2f}", ha='center', transform=self.ax.transAxes)
        self.ax.text(0.5, -0.08, f"n₂ = {n2:.2f}", ha='center', transform=self.ax.transAxes)
        
        # Draw incident ray (red)
        x_incident = np.linspace(-1, 0, 100)
        y_incident = np.tan(math.radians(θ1)) * x_incident
        self.ax.plot(x_incident, y_incident, 'r-', linewidth=2, label=f'Incident (θ₁={θ1:.1f}°)')
        
        # Draw refracted ray (blue) - FIXED DIRECTION
        if abs((n1 * math.sin(math.radians(θ1))) / n2) <= 1:  # No total internal reflection
            x_refracted = np.linspace(0, 1, 100)
            # Changed from -tan to +tan to maintain direction
            y_refracted = np.tan(math.radians(θ2)) * x_refracted
            self.ax.plot(x_refracted, y_refracted, 'b-', linewidth=2, label=f'Refracted (θ₂={θ2:.1f}°)')
        else:
            # Draw reflected ray (green) for total internal reflection
            x_reflected = np.linspace(0, -1, 100)
            y_reflected = -np.tan(math.radians(θ1)) * x_reflected
            self.ax.plot(x_reflected, y_reflected, 'g-', linewidth=2, label='Reflected (Total Internal)')
            self.ax.text(0.5, 0.5, "Total Internal Reflection", ha='center', 
                        bbox=dict(facecolor='white' if not self.dark_mode else '#444444',
                                alpha=0.8, edgecolor='none'))
        
        # Draw normal
        self.ax.axvline(0, color='k', linestyle='--', linewidth=0.5)
        
        # Add labels
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position')
        self.ax.set_ylabel('Position')
        self.ax.set_title('Light Refraction at Interface')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class WavesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Create return button
        return_btn = QPushButton("← Return to Main Menu")
        return_btn.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 14px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        layout.addWidget(return_btn)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create and add sub-tabs
        self.wave_properties_tab = WavePropertiesTab()
        self.sound_waves_tab = SoundWavesTab()
        self.light_properties_tab = LightPropertiesTab()
        
        self.tabs.addTab(self.wave_properties_tab, "Wave Properties")
        self.tabs.addTab(self.sound_waves_tab, "Sound Waves")
        self.tabs.addTab(self.light_properties_tab, "Light Properties")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        # Connect return button
        return_btn.clicked.connect(self.return_to_menu)
    
    def return_to_menu(self):
        self.parent().parent().return_to_menu()