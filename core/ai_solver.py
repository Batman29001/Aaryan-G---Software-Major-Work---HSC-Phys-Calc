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

    def solve(self, text: str) -> Dict:
        try:
            # First parse the problem
            parsed = self.parser.parse(text)
            
            # Validate the topic
            topic = parsed.get("topic", "").lower()
            if topic not in self.solvers:
                return {"error": f"Unrecognized physics topic: {topic}"}
                
            # Validate inputs
            inputs = parsed.get("inputs", {})
            if not inputs or not isinstance(inputs, dict):
                return {"error": "Invalid input parameters"}
                
            # Get the solver function
            solver = self.solvers[topic]
            
            # Try to solve
            result = solver(**inputs)
            
            # Validate result
            target = parsed.get("target", "")
            if not target:
                return {"error": "No target variable specified"}
                
            return {
                "topic": topic,
                "inputs": inputs,
                "result": result.get(target, "Cannot solve for the requested variable"),
                "raw_ai_response": str(parsed)
            }
            
        except KeyError as e:
            return {"error": f"Missing required parameter: {str(e)}"}
        except ValueError as e:
            return {"error": f"Physics calculation error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
