from typing import Dict
from core import (kinematics, dynamics, waves, 
                 electricity_magnetism, advanced_mechanics)

class SolverOrchestrator:
    MODULE_SOLVERS = {
        'kinematics': kinematics.solve_kinematics,
        'dynamics': dynamics.solve_dynamics,
        'waves': waves.solve_wave_properties,
        'electricity': electricity_magnetism.solve_circuits,
        'advanced': advanced_mechanics.solve_projectile_motion
    }

    def solve(self, module: str, variables: Dict) -> Dict:
        """Route the problem to the appropriate solver"""
        solver = self.MODULE_SOLVERS.get(module)
        if not solver:
            raise ValueError(f"No solver for module: {module}")
        
        # Convert variables to kwargs format expected by solvers
        kwargs = {k: v[0] for k, v in variables.items()}
        return solver(**kwargs)