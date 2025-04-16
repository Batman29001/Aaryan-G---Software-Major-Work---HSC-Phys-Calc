import math
from typing import Dict, Optional

class PhysicsSolver:
    def __init__(self):
        self.g = 9.81  # m/s²
        self.solutions = {}
        # Ordered by dependency - basic kinematics first, then dynamics, then energy
        self.equations = [
            self._solve_kinematics,
            self._solve_fma,
            self._solve_pmv,
            self._solve_impulse,
            self._solve_work_energy,
            self._solve_friction,
            self._solve_inclined_plane
        ]
    
    def solve(self, **kwargs) -> Dict[str, float]:
        """Main solver that handles all physics calculations"""
        # Initialize all possible variables with None
        self.solutions = {
            # Basic quantities
            'm': None, 't': None, 
            # Kinematics
            'a': None, 'v': None, 'v0': None, 'vf': None, 's': None,
            # Dynamics
            'F': None, 'p': None, 'impulse': None,
            # Energy
            'W': None, 'KE': None, 'PE': None, 'theta': None,
            # Friction
            'mu': None, 'FN': None, 'Ffriction': None,
            # Inclined plane
            'Fnormal': None, 'Fparallel': None
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
                changed |= equation()
        
        # Return only calculated values (remove None values)
        return {k: v for k, v in self.solutions.items() if v is not None}
    
    def _solve_kinematics(self) -> bool:
        """Solve kinematic equations (priority 1)"""
        changed = False
        
        # Enhanced velocity-acceleration-time relationships
        if self.solutions['t'] is not None:
            # Case 1: Calculate acceleration from velocity and time (a = v/t)
            if self.solutions['v'] is not None and self.solutions['a'] is None:
                self.solutions['a'] = self.solutions['v'] / self.solutions['t']
                changed = True
                # Assume initial velocity was 0 unless specified
                if self.solutions['v0'] is None:
                    self.solutions['v0'] = 0
                self.solutions['vf'] = self.solutions['v']
            
            # Case 2: Calculate velocity from acceleration and time (v = a*t)
            elif self.solutions['a'] is not None and self.solutions['v'] is None:
                self.solutions['v'] = self.solutions['a'] * self.solutions['t']
                changed = True
                if self.solutions['v0'] is None:
                    self.solutions['v0'] = 0
                self.solutions['vf'] = self.solutions['v']
            
            # Case 3: No velocities specified - assume starting from rest (v0=0)
            elif self.solutions['v0'] is None and self.solutions['vf'] is None:
                self.solutions['v0'] = 0  # Assume starting from rest
                self.solutions['vf'] = self.solutions['a'] * self.solutions['t']
                self.solutions['v'] = self.solutions['vf']  # Set general velocity
                changed = True
        
        # Special case: if given a and t but no velocities, calculate v directly
        if self.solutions['v'] is None and self.solutions['a'] is not None and self.solutions['t'] is not None:
            self.solutions['v'] = self.solutions['a'] * self.solutions['t']
            changed = True
        
        # s = v0*t + 0.5*a*t²
        if self.solutions['s'] is None:
            if self.solutions['v0'] is not None and self.solutions['t'] is not None:
                if self.solutions['a'] is not None:
                    self.solutions['s'] = self.solutions['v0'] * self.solutions['t'] + 0.5 * self.solutions['a'] * self.solutions['t']**2
                    changed = True
                elif self.solutions['vf'] is not None:
                    # If we have v0, vf, and t, we can find displacement using average velocity
                    self.solutions['s'] = 0.5 * (self.solutions['v0'] + self.solutions['vf']) * self.solutions['t']
                    changed = True
        
        return changed
    
    def _solve_fma(self) -> bool:
        """Solve F=ma and related (priority 2)"""
        changed = False
        
        # F = ma
        if self.solutions['F'] is None:
            if self.solutions['m'] is not None and self.solutions['a'] is not None:
                self.solutions['F'] = self.solutions['m'] * self.solutions['a']
                changed = True
        
        # a = F/m
        if self.solutions['a'] is None:
            if self.solutions['F'] is not None and self.solutions['m'] is not None:
                self.solutions['a'] = self.solutions['F'] / self.solutions['m']
                changed = True
        
        # m = F/a
        if self.solutions['m'] is None:
            if self.solutions['F'] is not None and self.solutions['a'] is not None:
                self.solutions['m'] = self.solutions['F'] / self.solutions['a']
                changed = True
        
        return changed
    
    def _solve_pmv(self) -> bool:
        """Solve momentum equations (priority 3)"""
        changed = False
        
        # p = mv
        if self.solutions['p'] is None:
            if self.solutions['m'] is not None and self.solutions['v'] is not None:
                self.solutions['p'] = self.solutions['m'] * self.solutions['v']
                changed = True
        
        # m = p/v
        if self.solutions['m'] is None:
            if self.solutions['p'] is not None and self.solutions['v'] is not None:
                self.solutions['m'] = self.solutions['p'] / self.solutions['v']
                changed = True
        
        # v = p/m
        if self.solutions['v'] is None:
            if self.solutions['p'] is not None and self.solutions['m'] is not None:
                self.solutions['v'] = self.solutions['p'] / self.solutions['m']
                changed = True
        
        return changed
    
    def _solve_impulse(self) -> bool:
        """Solve impulse-momentum theorem (priority 4)"""
        changed = False
        
        # impulse = F*t = Δp
        if self.solutions['impulse'] is None:
            if self.solutions['F'] is not None and self.solutions['t'] is not None:
                self.solutions['impulse'] = self.solutions['F'] * self.solutions['t']
                changed = True
            elif self.solutions['p'] is not None and self.solutions['v0'] is not None and self.solutions['m'] is not None:
                # Δp = mΔv
                self.solutions['impulse'] = self.solutions['m'] * (self.solutions['v'] - self.solutions['v0']) if 'v' in self.solutions else None
                if self.solutions['impulse'] is not None:
                    changed = True
        
        # F = impulse/t
        if self.solutions['F'] is None:
            if self.solutions['impulse'] is not None and self.solutions['t'] is not None:
                self.solutions['F'] = self.solutions['impulse'] / self.solutions['t']
                changed = True
        
        return changed
    
    def _solve_work_energy(self) -> bool:
        """Solve work and energy equations (priority 5)"""
        changed = False
        
        # W = F*s*cosθ (θ defaults to 0 if not provided)
        if self.solutions['W'] is None:
            if self.solutions['F'] is not None and self.solutions['s'] is not None:
                theta_rad = math.radians(self.solutions['theta']) if self.solutions['theta'] is not None else 0
                self.solutions['W'] = self.solutions['F'] * self.solutions['s'] * math.cos(theta_rad)
                changed = True
        
        # KE = 0.5*m*v²
        if self.solutions['KE'] is None:
            if self.solutions['m'] is not None and self.solutions['v'] is not None:
                self.solutions['KE'] = 0.5 * self.solutions['m'] * self.solutions['v']**2
                changed = True
        
        # PE = mgh (approximating h as s*sinθ for inclined plane)
        if self.solutions['PE'] is None:
            if self.solutions['m'] is not None and self.solutions['s'] is not None and self.solutions['theta'] is not None:
                self.solutions['PE'] = self.solutions['m'] * self.g * self.solutions['s'] * math.sin(math.radians(self.solutions['theta']))
                changed = True
        
        return changed
    
    def _solve_friction(self) -> bool:
        """Solve friction equations (priority 6)"""
        changed = False
        
        # Ffriction = μ*FN
        if self.solutions['Ffriction'] is None:
            if self.solutions['mu'] is not None and self.solutions['FN'] is not None:
                self.solutions['Ffriction'] = self.solutions['mu'] * self.solutions['FN']
                changed = True
        
        # FN = m*g if on flat surface
        if self.solutions['FN'] is None:
            if self.solutions['m'] is not None and self.solutions['theta'] is None:  # Not on inclined plane
                self.solutions['FN'] = self.solutions['m'] * self.g
                changed = True
        
        return changed
    
    def _solve_inclined_plane(self) -> bool:
        """Solve inclined plane components (priority 7)"""
        changed = False
        
        if self.solutions['m'] is not None and self.solutions['theta'] is not None:
            theta_rad = math.radians(self.solutions['theta'])
            
            if self.solutions['Fnormal'] is None:
                self.solutions['Fnormal'] = self.solutions['m'] * self.g * math.cos(theta_rad)
                changed = True
            
            if self.solutions['Fparallel'] is None:
                self.solutions['Fparallel'] = self.solutions['m'] * self.g * math.sin(theta_rad)
                changed = True
        
        return changed

def solve_dynamics(**kwargs) -> Dict[str, float]:
    """Convenience function that creates a solver instance"""
    solver = PhysicsSolver()
    return solver.solve(**kwargs)