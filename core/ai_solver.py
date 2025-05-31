#might be removing
import openai
import json
from typing import Dict
from core.advanced_mechanics import *
from core.dynamics import solve_dynamics
from core.electricity_magnetism import *
from core.kinematics import solve_kinematics
from core.waves import *

class AISolver:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        if not openai.api_key.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format")
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
        """Main solver that handles all physics problems"""
        # Step 1: Call AI to extract variables and identify topic
        prompt = f"""
        Given this physics problem: "{text}"
        
        Return JSON with:
        1. "topic" (match exactly one of: {list(self.solvers.keys())})
        2. "inputs" (dict of variables like {{"m": 2, "v": 5}})
        3. "target" (the variable to solve for, e.g., "F")
        
        Example:
        {{
            "topic": "circular",
            "inputs": {{"m": 2, "v": 5, "r": 3}},
            "target": "F_c"
        }}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)

        # Step 2: Solve using the appropriate module
        solver = self.solvers[data["topic"]]
        result = solver(**data["inputs"])

        # Step 3: Return the target variable if found
        output = {
            "topic": data["topic"],
            "inputs": data["inputs"],
            "result": result.get(data["target"], "Cannot solve for this variable")
        }
        return output