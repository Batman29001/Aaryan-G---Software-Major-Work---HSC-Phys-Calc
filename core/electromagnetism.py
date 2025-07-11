# electromagnetism.py
import math
from typing import Dict, Optional

class ElectromagnetismSolver:
    def __init__(self):
        self.mu_0 = 4 * math.pi * 1e-7  # Permeability of free space (N/A²)
        self.epsilon_0 = 8.8541878128e-12  # Permittivity of free space (F/m)
        self.e_charge = 1.602176634e-19  # Elementary charge (C)

    def solve_lorentz_force(self, **kwargs) -> Dict[str, float]:
        """
        Solves Lorentz force problems (F = qE + qvBsinθ)
        Possible variables: F, q, E, v, B, theta
        """
        s = {k: kwargs.get(k, None) for k in ['F', 'q', 'E', 'v', 'B', 'theta']}
        changed = True
        
        # Convert theta to radians if provided
        theta_rad = math.radians(s['theta']) if s['theta'] is not None else None
        
        while changed:
            changed = False
            
            # Electric component (F = qE)
            if s['F'] is None and s['q'] is not None and s['E'] is not None:
                s['F'] = s['q'] * s['E']
                changed = True
                
            # Magnetic component (F = qvBsinθ)
            if s['F'] is None and all(s.get(k) is not None for k in ['q', 'v', 'B', 'theta']):
                s['F'] = s['q'] * s['v'] * s['B'] * math.sin(theta_rad)
                changed = True
                
            # Solve for other variables
            if s['q'] is None and s['F'] is not None and s['E'] is not None:
                s['q'] = s['F'] / s['E']
                changed = True
                
            if s['E'] is None and s['F'] is not None and s['q'] is not None:
                s['E'] = s['F'] / s['q']
                changed = True
                
            if s['v'] is None and all(s.get(k) is not None for k in ['F', 'q', 'B', 'theta']):
                try:
                    s['v'] = s['F'] / (s['q'] * s['B'] * math.sin(theta_rad))
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate velocity when B or sinθ is zero")
                    
            if s['B'] is None and all(s.get(k) is not None for k in ['F', 'q', 'v', 'theta']):
                try:
                    s['B'] = s['F'] / (s['q'] * s['v'] * math.sin(theta_rad))
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate B when velocity or sinθ is zero")
                    
            if s['theta'] is None and all(s.get(k) is not None for k in ['F', 'q', 'v', 'B']):
                try:
                    theta_rad = math.asin(s['F'] / (s['q'] * s['v'] * s['B']))
                    s['theta'] = math.degrees(theta_rad)
                    changed = True
                except ValueError:
                    raise ValueError("Invalid combination of values - cannot calculate angle")

        # Validate results
        if s.get('theta') is not None and not (0 <= s['theta'] <= 180):
            raise ValueError("Angle must be between 0° and 180°")
            
        return {k: v for k, v in s.items() if v is not None}

    def solve_force_on_wire(self, **kwargs) -> Dict[str, float]:
        """
        Solves force on current-carrying wire problems (F = ILBsinθ)
        Possible variables: F, I, L, B, theta
        """
        s = {k: kwargs.get(k, None) for k in ['F', 'I', 'L', 'B', 'theta']}
        changed = True
        
        # Convert theta to radians if provided
        theta_rad = math.radians(s['theta']) if s['theta'] is not None else None
        
        while changed:
            changed = False
            
            # Main equation (F = ILBsinθ)
            if s['F'] is None and all(s.get(k) is not None for k in ['I', 'L', 'B', 'theta']):
                s['F'] = s['I'] * s['L'] * s['B'] * math.sin(theta_rad)
                changed = True
                
            # Solve for other variables
            if s['I'] is None and all(s.get(k) is not None for k in ['F', 'L', 'B', 'theta']):
                try:
                    s['I'] = s['F'] / (s['L'] * s['B'] * math.sin(theta_rad))
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate current when L, B or sinθ is zero")
                    
            if s['L'] is None and all(s.get(k) is not None for k in ['F', 'I', 'B', 'theta']):
                try:
                    s['L'] = s['F'] / (s['I'] * s['B'] * math.sin(theta_rad))
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate length when I, B or sinθ is zero")
                    
            if s['B'] is None and all(s.get(k) is not None for k in ['F', 'I', 'L', 'theta']):
                try:
                    s['B'] = s['F'] / (s['I'] * s['L'] * math.sin(theta_rad))
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate B when I, L or sinθ is zero")
                    
            if s['theta'] is None and all(s.get(k) is not None for k in ['F', 'I', 'L', 'B']):
                try:
                    theta_rad = math.asin(s['F'] / (s['I'] * s['L'] * s['B']))
                    s['theta'] = math.degrees(theta_rad)
                    changed = True
                except ValueError:
                    raise ValueError("Invalid combination of values - cannot calculate angle")

        # Validate results
        if s.get('theta') is not None and not (0 <= s['theta'] <= 180):
            raise ValueError("Angle must be between 0° and 180°")
            
        return {k: v for k, v in s.items() if v is not None}

    def solve_parallel_wires(self, **kwargs) -> Dict[str, float]:
        """
        Solves force between parallel wires problems (F/l = μ₀I₁I₂/2πr)
        Possible variables: F_per_length, I1, I2, r
        """
        s = {k: kwargs.get(k, None) for k in ['F_per_length', 'I1', 'I2', 'r']}
        changed = True
        
        while changed:
            changed = False
            
            # Main equation (F/l = μ₀I₁I₂/2πr)
            if s['F_per_length'] is None and all(s.get(k) is not None for k in ['I1', 'I2', 'r']):
                if s['r'] <= 0:
                    raise ValueError("Separation distance must be positive")
                s['F_per_length'] = (self.mu_0 * s['I1'] * s['I2']) / (2 * math.pi * s['r'])
                changed = True
                
            # Solve for other variables
            if s['I1'] is None and all(s.get(k) is not None for k in ['F_per_length', 'I2', 'r']):
                if s['I2'] == 0 or s['r'] <= 0:
                    raise ValueError("Current 2 and separation must be non-zero")
                s['I1'] = (2 * math.pi * s['r'] * s['F_per_length']) / (self.mu_0 * s['I2'])
                changed = True
                
            if s['I2'] is None and all(s.get(k) is not None for k in ['F_per_length', 'I1', 'r']):
                if s['I1'] == 0 or s['r'] <= 0:
                    raise ValueError("Current 1 and separation must be non-zero")
                s['I2'] = (2 * math.pi * s['r'] * s['F_per_length']) / (self.mu_0 * s['I1'])
                changed = True
                
            if s['r'] is None and all(s.get(k) is not None for k in ['F_per_length', 'I1', 'I2']):
                if s['I1'] == 0 or s['I2'] == 0:
                    raise ValueError("Currents must be non-zero")
                if s['F_per_length'] == 0:
                    raise ValueError("Force per length cannot be zero when calculating distance")
                s['r'] = (self.mu_0 * s['I1'] * s['I2']) / (2 * math.pi * s['F_per_length'])
                changed = True

        return {k: v for k, v in s.items() if v is not None}

    def solve_emf_induction(self, **kwargs) -> Dict[str, float]:
        """
        Solves EMF induction problems (ε = -NΔΦ/Δt, Φ = BAcosθ)
        Possible variables: emf, N, delta_phi, delta_t, B, A, theta, phi
        """
        s = {k: kwargs.get(k, None) for k in ['emf', 'N', 'delta_phi', 'delta_t', 'B', 'A', 'theta', 'phi']}
        changed = True
        
        # Convert theta to radians if provided
        theta_rad = math.radians(s['theta']) if s['theta'] is not None else None
        
        while changed:
            changed = False
            
            # Flux equation (Φ = BAcosθ)
            if s['phi'] is None and s['B'] is not None and s['A'] is not None:
                theta = theta_rad if s['theta'] is not None else 0
                s['phi'] = s['B'] * s['A'] * math.cos(theta)
                changed = True
                
            # EMF equation (ε = -NΔΦ/Δt)
            if s['emf'] is None and all(s.get(k) is not None for k in ['N', 'delta_phi', 'delta_t']):
                if s['delta_t'] <= 0:
                    raise ValueError("Time change must be positive")
                s['emf'] = -s['N'] * s['delta_phi'] / s['delta_t']
                changed = True
                
            # Solve for other variables
            if s['N'] is None and all(s.get(k) is not None for k in ['emf', 'delta_phi', 'delta_t']):
                if s['delta_phi'] == 0 or s['delta_t'] <= 0:
                    raise ValueError("Flux change and time must be non-zero")
                s['N'] = -s['emf'] * s['delta_t'] / s['delta_phi']
                changed = True
                
            if s['delta_phi'] is None and all(s.get(k) is not None for k in ['emf', 'N', 'delta_t']):
                if s['delta_t'] <= 0:
                    raise ValueError("Time change must be positive")
                s['delta_phi'] = -s['emf'] * s['delta_t'] / s['N']
                changed = True
                
            if s['delta_t'] is None and all(s.get(k) is not None for k in ['emf', 'N', 'delta_phi']):
                if s['delta_phi'] == 0:
                    raise ValueError("Flux change cannot be zero when calculating time")
                s['delta_t'] = -s['N'] * s['delta_phi'] / s['emf']
                changed = True
                
            if s['B'] is None and s['phi'] is not None and s['A'] is not None:
                if s['A'] <= 0:
                    raise ValueError("Area must be positive")
                theta = theta_rad if s['theta'] is not None else 0
                try:
                    s['B'] = s['phi'] / (s['A'] * math.cos(theta))
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate B when area is zero or cosθ is zero")
                    
            if s['A'] is None and s['phi'] is not None and s['B'] is not None:
                if s['B'] == 0:
                    raise ValueError("Magnetic field must be non-zero")
                theta = theta_rad if s['theta'] is not None else 0
                try:
                    s['A'] = s['phi'] / (s['B'] * math.cos(theta))
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate area when B is zero or cosθ is zero")
                    
            if s['theta'] is None and all(s.get(k) is not None for k in ['phi', 'B', 'A']):
                try:
                    cos_theta = s['phi'] / (s['B'] * s['A'])
                    if abs(cos_theta) > 1:
                        raise ValueError("Invalid combination of values - |cosθ| cannot exceed 1")
                    theta_rad = math.acos(cos_theta)
                    s['theta'] = math.degrees(theta_rad)
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate angle when B or A is zero")

        # Validate results
        if s.get('theta') is not None and not (0 <= s['theta'] <= 180):
            raise ValueError("Angle must be between 0° and 180°")
            
        return {k: v for k, v in s.items() if v is not None}

    def solve_transformer(self, **kwargs) -> Dict[str, float]:
        """
        Solves ideal transformer problems (Vp/Vs = Np/Ns, Ip/Is = Ns/Np)
        Possible variables: V_p, V_s, N_p, N_s, I_p, I_s
        """
        s = {k: kwargs.get(k, None) for k in ['V_p', 'V_s', 'N_p', 'N_s', 'I_p', 'I_s']}
        changed = True
        
        while changed:
            changed = False
            
            # Voltage ratio (Vp/Vs = Np/Ns)
            if s['V_s'] is None and all(s.get(k) is not None for k in ['V_p', 'N_p', 'N_s']):
                if s['N_s'] <= 0:
                    raise ValueError("Secondary turns must be positive")
                s['V_s'] = s['V_p'] * s['N_s'] / s['N_p']
                changed = True
                
            if s['V_p'] is None and all(s.get(k) is not None for k in ['V_s', 'N_p', 'N_s']):
                if s['N_p'] <= 0:
                    raise ValueError("Primary turns must be positive")
                s['V_p'] = s['V_s'] * s['N_p'] / s['N_s']
                changed = True
                
            if s['N_s'] is None and all(s.get(k) is not None for k in ['V_p', 'V_s', 'N_p']):
                if s['V_s'] == 0:
                    raise ValueError("Secondary voltage cannot be zero")
                if s['N_p'] <= 0:
                    raise ValueError("Primary turns must be positive")
                s['N_s'] = s['N_p'] * s['V_s'] / s['V_p']
                changed = True
                
            if s['N_p'] is None and all(s.get(k) is not None for k in ['V_p', 'V_s', 'N_s']):
                if s['V_p'] == 0:
                    raise ValueError("Primary voltage cannot be zero")
                if s['N_s'] <= 0:
                    raise ValueError("Secondary turns must be positive")
                s['N_p'] = s['N_s'] * s['V_p'] / s['V_s']
                changed = True
                
            # Current ratio (Ip/Is = Ns/Np)
            if s['I_s'] is None and all(s.get(k) is not None for k in ['I_p', 'N_p', 'N_s']):
                if s['N_p'] <= 0:
                    raise ValueError("Primary turns must be positive")
                s['I_s'] = s['I_p'] * s['N_p'] / s['N_s']
                changed = True
                
            if s['I_p'] is None and all(s.get(k) is not None for k in ['I_s', 'N_p', 'N_s']):
                if s['N_s'] <= 0:
                    raise ValueError("Secondary turns must be positive")
                s['I_p'] = s['I_s'] * s['N_s'] / s['N_p']
                changed = True

        return {k: v for k, v in s.items() if v is not None}

    def solve_motor_torque(self, **kwargs) -> Dict[str, float]:
        """
        Solves motor torque problems (τ = nIABsinθ)
        Possible variables: torque, n, I, A, B, theta
        """
        s = {k: kwargs.get(k, None) for k in ['torque', 'n', 'I', 'A', 'B', 'theta']}
        changed = True
        
        # Convert theta to radians if provided
        theta_rad = math.radians(s['theta']) if s['theta'] is not None else None
        
        while changed:
            changed = False
            
            # Main equation (τ = nIABsinθ)
            if s['torque'] is None and all(s.get(k) is not None for k in ['n', 'I', 'A', 'B', 'theta']):
                s['torque'] = s['n'] * s['I'] * s['A'] * s['B'] * math.sin(theta_rad)
                changed = True
                
            # Solve for other variables
            if s['n'] is None and all(s.get(k) is not None for k in ['torque', 'I', 'A', 'B', 'theta']):
                try:
                    s['n'] = s['torque'] / (s['I'] * s['A'] * s['B'] * math.sin(theta_rad))
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate turns when I, A, B or sinθ is zero")
                    
            if s['I'] is None and all(s.get(k) is not None for k in ['torque', 'n', 'A', 'B', 'theta']):
                try:
                    s['I'] = s['torque'] / (s['n'] * s['A'] * s['B'] * math.sin(theta_rad))
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate current when n, A, B or sinθ is zero")
                    
            if s['A'] is None and all(s.get(k) is not None for k in ['torque', 'n', 'I', 'B', 'theta']):
                try:
                    s['A'] = s['torque'] / (s['n'] * s['I'] * s['B'] * math.sin(theta_rad))
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate area when n, I, B or sinθ is zero")
                    
            if s['B'] is None and all(s.get(k) is not None for k in ['torque', 'n', 'I', 'A', 'theta']):
                try:
                    s['B'] = s['torque'] / (s['n'] * s['I'] * s['A'] * math.sin(theta_rad))
                    changed = True
                except ZeroDivisionError:
                    raise ValueError("Cannot calculate B when n, I, A or sinθ is zero")
                    
            if s['theta'] is None and all(s.get(k) is not None for k in ['torque', 'n', 'I', 'A', 'B']):
                try:
                    theta_rad = math.asin(s['torque'] / (s['n'] * s['I'] * s['A'] * s['B']))
                    s['theta'] = math.degrees(theta_rad)
                    changed = True
                except ValueError:
                    raise ValueError("Invalid combination of values - cannot calculate angle")

        # Validate results
        if s.get('theta') is not None and not (0 <= s['theta'] <= 180):
            raise ValueError("Angle must be between 0° and 180°")
            
        return {k: v for k, v in s.items() if v is not None}


# Convenience functions
def solve_lorentz_force(**kwargs) -> Dict[str, float]:
    return ElectromagnetismSolver().solve_lorentz_force(**kwargs)

def solve_force_on_wire(**kwargs) -> Dict[str, float]:
    return ElectromagnetismSolver().solve_force_on_wire(**kwargs)

def solve_parallel_wires(**kwargs) -> Dict[str, float]:
    return ElectromagnetismSolver().solve_parallel_wires(**kwargs)

def solve_emf_induction(**kwargs) -> Dict[str, float]:
    return ElectromagnetismSolver().solve_emf_induction(**kwargs)

def solve_transformer(**kwargs) -> Dict[str, float]:
    return ElectromagnetismSolver().solve_transformer(**kwargs)

def solve_motor_torque(**kwargs) -> Dict[str, float]:
    return ElectromagnetismSolver().solve_motor_torque(**kwargs)