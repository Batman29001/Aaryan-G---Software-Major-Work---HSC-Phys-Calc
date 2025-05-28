import math
from typing import Dict, Optional

class AdvancedMechanicsSolver:
    def __init__(self):
        self.g = 9.81  # m/s² (standard gravity)
        self.G = 6.67430e-11  # universal gravitational constant (m³ kg⁻¹ s⁻²)
    
    def solve_projectile_motion(self, **kwargs) -> Dict[str, float]:
        """Solve projectile motion problems"""
        solutions = {
            'u': None, 'θ': None, 'ux': None, 'uy': None,
            't_flight': None, 'max_height': None, 'range': None
        }
        
        # Set provided values
        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v
        
        # Convert angle to radians if provided
        if solutions['θ'] is not None:
            solutions['θ'] = math.radians(solutions['θ'])
        
        # Calculate missing values
        changed = True
        while changed:
            changed = False
            
            # Calculate initial velocity components
            if solutions['u'] is not None and solutions['θ'] is not None:
                if solutions['ux'] is None:
                    solutions['ux'] = solutions['u'] * math.cos(solutions['θ'])
                    changed = True
                if solutions['uy'] is None:
                    solutions['uy'] = solutions['u'] * math.sin(solutions['θ'])
                    changed = True
            
            # Calculate time of flight
            if solutions['t_flight'] is None and solutions['uy'] is not None:
                solutions['t_flight'] = 2 * solutions['uy'] / self.g
                changed = True
            
            # Calculate maximum height
            if solutions['max_height'] is None and solutions['uy'] is not None:
                solutions['max_height'] = (solutions['uy'] ** 2) / (2 * self.g)
                changed = True
            
            # Calculate range
            if solutions['range'] is None and solutions['ux'] is not None and solutions['t_flight'] is not None:
                solutions['range'] = solutions['ux'] * solutions['t_flight']
                changed = True
        
        # Convert angle back to degrees for display
        if solutions['θ'] is not None:
            solutions['θ'] = math.degrees(solutions['θ'])
        
        return {k: v for k, v in solutions.items() if v is not None}
    
    def solve_circular_motion(self, **kwargs) -> Dict[str, float]:
        """Solve uniform circular motion problems"""
        solutions = {
            'v': None, 'r': None, 'T': None, 'f': None, 
            'ω': None, 'a_c': None, 'F_c': None, 'm': None
        }
        
        # Set provided values
        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v
        
        changed = True
        while changed:
            changed = False
            
            # Angular velocity relationships
            if solutions['ω'] is None:
                if solutions['T'] is not None:
                    solutions['ω'] = 2 * math.pi / solutions['T']
                    changed = True
                elif solutions['f'] is not None:
                    solutions['ω'] = 2 * math.pi * solutions['f']
                    changed = True
            
            # Velocity relationships
            if solutions['v'] is None and solutions['ω'] is not None and solutions['r'] is not None:
                solutions['v'] = solutions['ω'] * solutions['r']
                changed = True
            
            # Centripetal acceleration
            if solutions['a_c'] is None and solutions['v'] is not None and solutions['r'] is not None:
                solutions['a_c'] = (solutions['v'] ** 2) / solutions['r']
                changed = True
            
            # Centripetal force
            if solutions['F_c'] is None and solutions['m'] is not None and solutions['a_c'] is not None:
                solutions['F_c'] = solutions['m'] * solutions['a_c']
                changed = True
        
        return {k: v for k, v in solutions.items() if v is not None}
    
    def solve_banked_tracks(self, **kwargs) -> Dict[str, float]:
        """Solve banked track problems"""
        solutions = {
            'θ': None, 'v': None, 'r': None, 'μ': None,
            'v_min': None, 'v_max': None
        }
        
        # Set provided values
        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v
        
        # Convert angle to radians if provided
        if solutions['θ'] is not None:
            solutions['θ'] = math.radians(solutions['θ'])
        
        changed = True
        while changed:
            changed = False
            
            # Ideal banked curve (no friction needed)
            if solutions['v'] is not None and solutions['r'] is not None and solutions['θ'] is None:
                solutions['θ'] = math.atan((solutions['v'] ** 2) / (self.g * solutions['r']))
                changed = True
            
            # With friction
            if solutions['μ'] is not None and solutions['θ'] is not None:
                tan_θ = math.tan(solutions['θ'])
                if solutions['v_min'] is None and solutions['r'] is not None:
                    solutions['v_min'] = math.sqrt(self.g * solutions['r'] * (tan_θ - solutions['μ']) / (1 + solutions['μ'] * tan_θ))
                    changed = True
                if solutions['v_max'] is None and solutions['r'] is not None:
                    solutions['v_max'] = math.sqrt(self.g * solutions['r'] * (tan_θ + solutions['μ']) / (1 - solutions['μ'] * tan_θ))
                    changed = True
        
        # Convert angle back to degrees for display
        if solutions['θ'] is not None:
            solutions['θ'] = math.degrees(solutions['θ'])
        
        return {k: v for k, v in solutions.items() if v is not None}
    
    def solve_gravitation(self, **kwargs) -> Dict[str, float]:
        """Solve gravitation problems"""
        solutions = {
            'M': None, 'm': None, 'r': None, 'F_g': None,
            'g': None, 'v_orbital': None, 'T': None, 'altitude': None
        }
        
        # Set provided values
        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v
        
        changed = True
        while changed:
            changed = False
            
            # Gravitational force
            if solutions['F_g'] is None and solutions['M'] is not None and solutions['m'] is not None and solutions['r'] is not None:
                solutions['F_g'] = self.G * solutions['M'] * solutions['m'] / (solutions['r'] ** 2)
                changed = True
            
            # Gravitational field strength
            if solutions['g'] is None and solutions['M'] is not None and solutions['r'] is not None:
                solutions['g'] = self.G * solutions['M'] / (solutions['r'] ** 2)
                changed = True
            
            # Orbital velocity
            if solutions['v_orbital'] is None and solutions['M'] is not None and solutions['r'] is not None:
                solutions['v_orbital'] = math.sqrt(self.G * solutions['M'] / solutions['r'])
                changed = True
            
            # Orbital period
            if solutions['T'] is None and solutions['v_orbital'] is not None and solutions['r'] is not None:
                solutions['T'] = 2 * math.pi * solutions['r'] / solutions['v_orbital']
                changed = True
            
            # Altitude (if Earth's radius is considered)
            if solutions['altitude'] is None and solutions['r'] is not None:
                earth_radius = 6.371e6  # meters
                solutions['altitude'] = solutions['r'] - earth_radius
                changed = True
        
        return {k: v for k, v in solutions.items() if v is not None}

def solve_projectile_motion(**kwargs) -> Dict[str, float]:
    solver = AdvancedMechanicsSolver()
    return solver.solve_projectile_motion(**kwargs)

def solve_circular_motion(**kwargs) -> Dict[str, float]:
    solver = AdvancedMechanicsSolver()
    return solver.solve_circular_motion(**kwargs)

def solve_banked_tracks(**kwargs) -> Dict[str, float]:
    solver = AdvancedMechanicsSolver()
    return solver.solve_banked_tracks(**kwargs)

def solve_gravitation(**kwargs) -> Dict[str, float]:
    solver = AdvancedMechanicsSolver()
    return solver.solve_gravitation(**kwargs)