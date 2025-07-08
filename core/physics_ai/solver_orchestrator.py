from typing import Dict, Optional
from enum import Enum
from core.physics_ai.physics_interpreter import ProblemType
from core import (
    kinematics, dynamics, waves,
    electricity_magnetism, electromagnetism,
    advanced_mechanics
)

class SolverOrchestrator:
    def __init__(self):
        # Map problem types to solver functions
        self.SOLVERS = {
            ProblemType.KINEMATICS: {
                'function': kinematics.solve_kinematics,
                'var_mapping': {
                    'velocity': 'v',
                    'acceleration': 'a',
                    'time': 't',
                    'displacement': 's',
                }
            },
            ProblemType.DYNAMICS: {
                'function': dynamics.solve_dynamics,
                'var_mapping': {
                    'mass': 'm',
                    'force': 'F',
                    'velocity': 'v',
                    'acceleration': 'a',
                }
            },
            ProblemType.WAVES: {
                'function': waves.solve_wave_properties,
                'var_mapping': {
                    'frequency': 'f',
                    'wavelength': 'λ',
                    'period': 'T',
                }
            },
            ProblemType.ELECTRICITY: {
                'function': electricity_magnetism.solve_circuits,
                'var_mapping': {
                    'voltage': 'V_circuit',
                    'current': 'I',
                    'resistance': 'R',
                    'power': 'P',
                }
            },
            ProblemType.ELECTROMAGNETISM: {
                'function': electromagnetism.solve_charged_particles,
                'var_mapping': {
                    'charge': 'q',
                    'magnetic_field': 'B',
                    'emf': 'emf',
                    'flux': 'phi',
                }
            },
            ProblemType.ADVANCED_MECHANICS: {
                'function': advanced_mechanics.solve_projectile_motion,
                'var_mapping': {
                    'velocity': 'u',
                    'angle': 'θ',
                    'time': 't_flight',
                }
            }
        }

    def solve(self, problem_type: ProblemType, variables: Dict[str, float]) -> Dict[str, float]:
        """Route the problem to the appropriate solver."""
        solver_config = self.SOLVERS.get(problem_type)
        if not solver_config:
            raise ValueError(f"No solver available for problem type: {problem_type}")

        # Map generic variable names to solver-specific names
        solver_vars = {}
        for generic_name, value in variables.items():
            solver_name = solver_config['var_mapping'].get(generic_name, generic_name)
            solver_vars[solver_name] = value

        try:
            return solver_config['function'](**solver_vars)
        except Exception as e:
            raise RuntimeError(f"Solver failed: {str(e)}")