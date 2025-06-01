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
            parsed = self.parser.parse(text)
            solver = self.solvers[parsed["topic"]]
            result = solver(**parsed["inputs"])
            
            return {
                "topic": parsed["topic"],
                "inputs": parsed["inputs"],
                "result": result.get(parsed["target"], "Cannot solve"),
                "raw_ai_response": str(parsed)  # Changed from undefined 'response' to str(parsed)
            }
        except KeyError:
            return {"error": "Unrecognized physics topic"}
        except ValueError as e:
            return {"error": f"Physics parsing error: {str(e)}"}
        except Exception:
            return {"error": traceback.format_exc()}
