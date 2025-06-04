import json
from typing import Dict
from core.local_ai_parser import LocalAIParser 
from core.advanced_mechanics import *
from core.dynamics import solve_dynamics
from core.electricity_magnetism import *
from core.kinematics import solve_kinematics
from core.waves import *
import traceback

class AISolver:
    def __init__(self):
        try:
            self.parser = LocalAIParser()  
        except Exception as e:
            raise RuntimeError(f"Failed to initialize AI solver: {str(e)}")
            
        self.solvers = {
            "kinematics": solve_kinematics,
            "dynamics": solve_dynamics,
            "projectile": solve_projectile_motion,
            "circular": solve_circular_motion,
            "banked": solve_banked_tracks,
            "gravitation": solve_gravitation,
            "electrostatics": solve_electrostatics,
            "circuits": solve_circuits,
            "magnetism": solve_magnetism,
            "wave": solve_wave_properties,
            "sound": solve_sound_waves,
            "light": solve_light_properties
        }

    def solve(self, text: str, retries=2) -> Dict:
        for attempt in range(retries + 1):
            try:
                if attempt > 0:  # Simplify input on retry
                    text = self._simplify_problem_text(text)
                parsed = self.parser.parse(text)
                # ... rest of solver logic ...
                
            except Exception as e:
                if attempt == retries:
                    return {
                        "error": f"Physics solver failed. Try simpler phrasing like '3kg at 4m/s in 2m circle - find force'",
                        "raw_input": text
                    }

    def _simplify_problem_text(self, text: str) -> str:
        """Extract key numbers and units for retry"""
        simplified = []
        for part in text.split():
            if any(c.isdigit() for c in part):
                simplified.append(part)
        return ' '.join(simplified[:10])  # Limit to first 10 number-containing words