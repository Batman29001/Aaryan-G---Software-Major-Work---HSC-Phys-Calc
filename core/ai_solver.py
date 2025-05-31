import json
from typing import Dict
from core.local_ai_parser import LocalAIParser 
from core.advanced_mechanics import *
from core.dynamics import solve_dynamics
from core.electricity_magnetism import *
from core.kinematics import solve_kinematics
from core.waves import *

class AISolver:
    def __init__(self):
        self.parser = LocalAIParser()  
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

    def solve(self, text: str) -> Dict:
        try:
            # Step 1: Parse with local AI
            parsed = self.parser.parse(text)
            
            # Step 2: Solve using appropriate module
            solver = self.solvers[parsed["topic"]]
            result = solver(**parsed["inputs"])
            
            return {
                "topic": parsed["topic"],
                "inputs": parsed["inputs"],
                "result": result.get(parsed["target"], "Cannot solve for this variable")
            }
        except Exception as e:
            return {"error": str(e)}
