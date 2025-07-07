import math
from typing import Dict, Optional

class ElectromagnetismSolver:
    def __init__(self):
        self.mu_0 = 4 * math.pi * 1e-7  # Permeability of free space (N/A²)
        self.epsilon_0 = 8.8541878128e-12  # Permittivity of free space (F/m)
        self.e_charge = 1.602176634e-19  # Elementary charge (C)
    
    def solve_charged_particles(self, **kwargs) -> Dict[str, float]:
        """Solve problems related to charged particles in fields"""
        solutions = {
            'E': None, 'V': None, 'd': None,  # Electric field basics
            'q': None, 'F': None,  # Force on charge
            'B': None, 'v': None, 'theta': None,  # Magnetic field
            'r': None, 'm': None,  # Circular motion
            'work': None, 'K': None, 'U': None  # Energy
        }
        
        # Set provided values
        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v
        
        changed = True
        while changed:
            changed = False
            
            # Electric field relationships
            if solutions['E'] is None and solutions['V'] is not None and solutions['d'] is not None:
                solutions['E'] = solutions['V'] / solutions['d']
                changed = True
                
            if solutions['F'] is None and solutions['q'] is not None and solutions['E'] is not None:
                solutions['F'] = solutions['q'] * solutions['E']
                changed = True
                
            # Magnetic force on moving charge
            if solutions['F'] is None and solutions['q'] is not None and solutions['v'] is not None and solutions['B'] is not None:
                theta = math.radians(solutions['theta']) if solutions['theta'] is not None else 0
                solutions['F'] = solutions['q'] * solutions['v'] * solutions['B'] * math.sin(theta)
                changed = True
                
            # Circular motion in magnetic field
            if solutions['r'] is None and solutions['m'] is not None and solutions['v'] is not None and solutions['q'] is not None and solutions['B'] is not None:
                solutions['r'] = (solutions['m'] * solutions['v']) / (solutions['q'] * solutions['B'])
                changed = True
                
            # Energy relationships
            if solutions['work'] is None and solutions['q'] is not None and solutions['V'] is not None:
                solutions['work'] = solutions['q'] * solutions['V']
                changed = True
                
            if solutions['K'] is None and solutions['m'] is not None and solutions['v'] is not None:
                solutions['K'] = 0.5 * solutions['m'] * solutions['v']**2
                changed = True
        
        return {k: v for k, v in solutions.items() if v is not None}
    
    def solve_motor_effect(self, **kwargs) -> Dict[str, float]:
        """Solve problems related to the motor effect"""
        solutions = {
            'F': None, 'I': None, 'l': None, 'B': None, 'theta': None,
            'F_per_length': None, 'I1': None, 'I2': None, 'r': None
        }
        
        # Set provided values
        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v
        
        changed = True
        while changed:
            changed = False
            
            # Force on current-carrying conductor
            if solutions['F'] is None and solutions['I'] is not None and solutions['l'] is not None and solutions['B'] is not None:
                theta = math.radians(solutions['theta']) if solutions['theta'] is not None else 0
                solutions['F'] = solutions['I'] * solutions['l'] * solutions['B'] * math.sin(theta)
                changed = True
                
            # Force between parallel wires
            if solutions['F_per_length'] is None and solutions['I1'] is not None and solutions['I2'] is not None and solutions['r'] is not None:
                solutions['F_per_length'] = (self.mu_0 * solutions['I1'] * solutions['I2']) / (2 * math.pi * solutions['r'])
                changed = True
        
        return {k: v for k, v in solutions.items() if v is not None}
    
    def solve_induction(self, **kwargs) -> Dict[str, float]:
        """Solve electromagnetic induction problems"""
        solutions = {
            'emf': None, 'N': None, 'delta_phi': None, 'delta_t': None,
            'B': None, 'A': None, 'theta': None, 'phi': None,
            'V_p': None, 'V_s': None, 'N_p': None, 'N_s': None,
            'I_p': None, 'I_s': None
        }
        
        # Set provided values
        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v
        
        changed = True
        while changed:
            changed = False
            
            # Magnetic flux
            if solutions['phi'] is None and solutions['B'] is not None and solutions['A'] is not None:
                theta = math.radians(solutions['theta']) if solutions['theta'] is not None else 0
                solutions['phi'] = solutions['B'] * solutions['A'] * math.cos(theta)
                changed = True
                
            # Faraday's Law
            if solutions['emf'] is None and solutions['N'] is not None and solutions['delta_phi'] is not None and solutions['delta_t'] is not None:
                solutions['emf'] = -solutions['N'] * (solutions['delta_phi'] / solutions['delta_t'])
                changed = True
                
            # Transformer equations
            if solutions['V_s'] is None and solutions['V_p'] is not None and solutions['N_s'] is not None and solutions['N_p'] is not None:
                solutions['V_s'] = solutions['V_p'] * (solutions['N_s'] / solutions['N_p'])
                changed = True
                
            if solutions['I_s'] is None and solutions['I_p'] is not None and solutions['N_p'] is not None and solutions['N_s'] is not None:
                solutions['I_s'] = solutions['I_p'] * (solutions['N_p'] / solutions['N_s'])
                changed = True
        
        return {k: v for k, v in solutions.items() if v is not None}
    
    def solve_motor_applications(self, **kwargs) -> Dict[str, float]:
        """Solve problems related to motor applications"""
        solutions = {
            'torque': None, 'n': None, 'I': None, 'A': None, 'B': None, 'theta': None,
            'back_emf': None, 'omega': None, 'N': None, 'phi': None
        }
        
        # Set provided values
        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v
        
        changed = True
        while changed:
            changed = False
            
            # Torque in motor
            if solutions['torque'] is None and solutions['n'] is not None and solutions['I'] is not None and solutions['A'] is not None and solutions['B'] is not None:
                theta = math.radians(solutions['theta']) if solutions['theta'] is not None else 0
                solutions['torque'] = solutions['n'] * solutions['I'] * solutions['A'] * solutions['B'] * math.sin(theta)
                changed = True
                
            # Back EMF
            if solutions['back_emf'] is None and solutions['omega'] is not None and solutions['N'] is not None and solutions['phi'] is not None:
                solutions['back_emf'] = solutions['N'] * solutions['phi'] * solutions['omega']
                changed = True
        
        return {k: v for k, v in solutions.items() if v is not None}

# Convenience functions
def solve_charged_particles(**kwargs) -> Dict[str, float]:
    solver = ElectromagnetismSolver()
    return solver.solve_charged_particles(**kwargs)

def solve_motor_effect(**kwargs) -> Dict[str, float]:
    solver = ElectromagnetismSolver()
    return solver.solve_motor_effect(**kwargs)

def solve_induction(**kwargs) -> Dict[str, float]:
    solver = ElectromagnetismSolver()
    return solver.solve_induction(**kwargs)

def solve_motor_applications(**kwargs) -> Dict[str, float]:
    solver = ElectromagnetismSolver()
    return solver.solve_motor_applications(**kwargs)