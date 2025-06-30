import re
from typing import Dict, Optional

class PhysicsInterpreter:
    MODULE_MAP = {
        'kinematics': ['velocity', 'acceleration', 'displacement', 'time'],
        'dynamics': ['force', 'mass', 'momentum', 'impulse'],
        'waves': ['wavelength', 'frequency', 'period', 'wave speed'],
        'electricity': ['current', 'voltage', 'resistance', 'power'],
        'advanced': ['projectile', 'circular motion', 'gravitation']
    }

    def extract_variables(self, text: str) -> Dict[str, float]:
        """Extract variables from the AI's analysis"""
        pattern = r"([a-zA-Z]+)\s*=\s*([0-9.]+)\s*([a-zA-Z]*)"
        matches = re.findall(pattern, text)
        return {var: (float(val), unit) for var, val, unit in matches}

    def determine_module(self, text: str) -> Optional[str]:
        """Determine which physics module to use"""
        text_lower = text.lower()
        for module, keywords in self.MODULE_MAP.items():
            if any(keyword in text_lower for keyword in keywords):
                return module
        return None