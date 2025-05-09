# core/electricity_magnetism.py
import math
from typing import Dict, Optional

class EMSolver:
    def __init__(self):
        self.permittivity = 8.854e-12  # ε₀ in F/m
        self.permeability = 4 * math.pi * 1e-7  # μ₀ in N/A²
        self.solutions = {}
        
        # Ordered by dependency
        self.equations = [
            self._solve_electrostatics,
            self._solve_circuits,
            self._solve_magnetism
        ]
    
    def solve(self, category: str, **kwargs) -> Dict[str, float]:
        """Main solver that handles all EM calculations"""
        # Initialize all possible variables with None
        self.solutions = {
            # Electrostatics
            'F': None, 'q': None, 'E': None, 'V': None, 'd': None, 'U': None, 'W': None,
            # Circuits
            'I': None, 'V_circuit': None, 'R': None, 'P': None, 'E_energy': None, 't': None,
            'R_series': None, 'R_parallel': None, 'R1': None, 'R2': None,
            # Magnetism
            'B': None, 'I_wire': None, 'r_wire': None, 'N': None, 'L': None, 'type': None
        }
        
        # Set provided values
        for k, v in kwargs.items():
            if k in self.solutions:
                self.solutions[k] = v
        
        # Keep solving until no more progress can be made
        changed = True
        while changed:
            changed = False
            for equation in self.equations:
                if equation.__name__ == f"_solve_{category}":
                    changed |= equation()
        
        # Return only calculated values (remove None values)
        return {k: v for k, v in self.solutions.items() if v is not None}
    
    def _solve_electrostatics(self) -> bool:
        """Solve electrostatics equations"""
        changed = False
        
        # Force on charge: F = qE
        if self.solutions['F'] is None:
            if self.solutions['q'] is not None and self.solutions['E'] is not None:
                self.solutions['F'] = self.solutions['q'] * self.solutions['E']
                changed = True
        
        # Electric field: E = V/d
        if self.solutions['E'] is None:
            if self.solutions['V'] is not None and self.solutions['d'] is not None:
                self.solutions['E'] = self.solutions['V'] / self.solutions['d']
                changed = True
        
        # Potential difference: V = Ed
        if self.solutions['V'] is None:
            if self.solutions['E'] is not None and self.solutions['d'] is not None:
                self.solutions['V'] = self.solutions['E'] * self.solutions['d']
                changed = True
        
        return changed
    
    def _solve_circuits(self) -> bool:
        """Solve electric circuit equations"""
        changed = False
        
        # Ohm's Law: V = IR
        if self.solutions['V_circuit'] is None:
            if self.solutions['I'] is not None and self.solutions['R'] is not None:
                self.solutions['V_circuit'] = self.solutions['I'] * self.solutions['R']
                changed = True
        
        if self.solutions['I'] is None:
            if self.solutions['V_circuit'] is not None and self.solutions['R'] is not None:
                self.solutions['I'] = self.solutions['V_circuit'] / self.solutions['R']
                changed = True
        
        if self.solutions['R'] is None:
            if self.solutions['V_circuit'] is not None and self.solutions['I'] is not None:
                self.solutions['R'] = self.solutions['V_circuit'] / self.solutions['I']
                changed = True
        
        # Power: P = VI = I²R = V²/R
        if self.solutions['P'] is None:
            if self.solutions['V_circuit'] is not None and self.solutions['I'] is not None:
                self.solutions['P'] = self.solutions['V_circuit'] * self.solutions['I']
                changed = True
            elif self.solutions['I'] is not None and self.solutions['R'] is not None:
                self.solutions['P'] = (self.solutions['I']**2) * self.solutions['R']
                changed = True
            elif self.solutions['V_circuit'] is not None and self.solutions['R'] is not None:
                self.solutions['P'] = (self.solutions['V_circuit']**2) / self.solutions['R']
                changed = True
        
        # Energy: E = Pt = VIt
        if self.solutions['E_energy'] is None:
            if self.solutions['P'] is not None and self.solutions['t'] is not None:
                self.solutions['E_energy'] = self.solutions['P'] * self.solutions['t']
                changed = True
            elif all(k in self.solutions and self.solutions[k] is not None 
                     for k in ['V_circuit', 'I', 't']):
                self.solutions['E_energy'] = (
                    self.solutions['V_circuit'] * self.solutions['I'] * self.solutions['t'])
                changed = True
        
        # Series resistance: R_series = R1 + R2
        if self.solutions['R_series'] is None:
            if all(k in self.solutions and self.solutions[k] is not None 
                     for k in ['R1', 'R2']):
                self.solutions['R_series'] = self.solutions['R1'] + self.solutions['R2']
                changed = True
        
        # Parallel resistance: 1/R_parallel = 1/R1 + 1/R2
        if self.solutions['R_parallel'] is None:
            if all(k in self.solutions and self.solutions[k] is not None 
                     for k in ['R1', 'R2']):
                self.solutions['R_parallel'] = 1 / (1/self.solutions['R1'] + 1/self.solutions['R2'])
                changed = True
        
        return changed
    
    def _solve_magnetism(self) -> bool:
        changed = False
    
        # Straight wire case
        if self.solutions.get('r_wire') is not None and self.solutions.get('I_wire') is not None:
            if self.solutions.get('B') is None:
                self.solutions['B'] = (self.permeability * self.solutions['I_wire']) / \
                                    (2 * math.pi * self.solutions['r_wire'])
                self.solutions['type'] = 'straight_wire'
                changed = True
            elif self.solutions.get('I_wire') is None and self.solutions.get('B') is not None:
                self.solutions['I_wire'] = (self.solutions['B'] * 2 * math.pi * self.solutions['r_wire']) / \
                                        self.permeability
                self.solutions['type'] = 'straight_wire'
                changed = True
        
        # Solenoid case
        elif self.solutions.get('N') is not None and self.solutions.get('L') is not None:
            if self.solutions.get('B') is None and self.solutions.get('I_wire') is not None:
                self.solutions['B'] = (self.permeability * self.solutions['N'] * \
                                    self.solutions['I_wire']) / self.solutions['L']
                self.solutions['type'] = 'solenoid'
                changed = True
            elif self.solutions.get('I_wire') is None and self.solutions.get('B') is not None:
                self.solutions['I_wire'] = (self.solutions['B'] * self.solutions['L']) / \
                                        (self.permeability * self.solutions['N'])
                self.solutions['type'] = 'solenoid'
                changed = True
    
            return changed

def solve_electrostatics(**kwargs) -> Dict[str, float]:
    """Convenience function for electrostatics"""
    solver = EMSolver()
    return solver.solve('electrostatics', **kwargs)

def solve_circuits(**kwargs) -> Dict[str, float]:
    """Convenience function for electric circuits"""
    solver = EMSolver()
    return solver.solve('circuits', **kwargs)

def solve_magnetism(**kwargs) -> Dict[str, float]:
    """Convenience function for magnetism"""
    solver = EMSolver()
    return solver.solve('magnetism', **kwargs)