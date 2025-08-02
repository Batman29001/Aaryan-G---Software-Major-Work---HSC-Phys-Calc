# Error Handling and Input Validation Guide - I got ts from somewhere so u basically just use this in ur things

## Overview

This guide outlines the comprehensive error handling and input validation strategy for the Physics Calculator application.

## 1. Exception Hierarchy

### Core Exception Classes
```python
class PhysicsError(Exception):
    """Base class for physics-related errors"""
    pass

class InputValidationError(PhysicsError):
    """Exception raised for invalid input values"""
    pass

class InsufficientDataError(PhysicsError):
    """Exception raised when not enough data is provided"""
    pass

class PhysicsConfigurationError(PhysicsError):
    """Exception raised for physically impossible scenarios"""
    pass
```

## 2. Input Validation Strategy

### 2.1 Real-Time Validation
- **Field-level validation**: Validate each field as user types
- **Visual feedback**: Red borders and tooltips for invalid inputs
- **Progressive disclosure**: Show validation errors only when relevant

### 2.2 Pre-Calculation Validation
- **Comprehensive check**: Validate all inputs before calculation
- **Dependency validation**: Ensure required field combinations are met
- **Physical constraints**: Check for physically impossible values

### 2.3 Calculation-Time Validation
- **Runtime checks**: Validate intermediate calculation steps
- **Convergence monitoring**: Check for calculation convergence
- **Result validation**: Verify final results are physically reasonable

## 3. Validation Rules by Physics Domain

### 3.1 Electromagnetism
```python
# Force on Wire (F = BILsinθ)
validation_rules = {
    'I': {'min': 0, 'max': 1e6, 'zero_allowed': False},  # Current
    'L': {'min': 0, 'max': 1e6, 'zero_allowed': False},  # Length
    'B': {'min': 0, 'max': 100, 'zero_allowed': False},  # Magnetic field
    'theta': {'min': -360, 'max': 360, 'zero_allowed': True},  # Angle
    'F': {'min': 0, 'max': 1e12, 'zero_allowed': True}   # Force
}
```

### 3.2 Kinematics
```python
# Basic kinematic equations
validation_rules = {
    'u': {'min': -3e8, 'max': 3e8, 'zero_allowed': True},  # Initial velocity
    'v': {'min': -3e8, 'max': 3e8, 'zero_allowed': True},  # Final velocity
    'a': {'min': -1e6, 'max': 1e6, 'zero_allowed': True},  # Acceleration
    's': {'min': 0, 'max': 1e12, 'zero_allowed': True},    # Displacement
    't': {'min': 0, 'max': 1e12, 'zero_allowed': False}    # Time
}
```

### 3.3 Advanced Mechanics
```python
# Projectile motion
validation_rules = {
    'u': {'min': 0, 'max': 3e8, 'zero_allowed': False},   # Initial velocity
    'theta': {'min': -360, 'max': 360, 'zero_allowed': False},  # Launch angle
    'g': {'min': 0, 'max': 100, 'zero_allowed': False},   # Gravity
    't_flight': {'min': 0, 'max': 1e6, 'zero_allowed': False}   # Flight time
}
```

## 4. Input Rule Enforcement

### 4.1 Mutual Exclusions
```python
def enforce_mutual_exclusions(self):
    """Enforce mutually exclusive input fields"""
    # Example: For magnetism calculations
    has_r = bool(self.inputs['r_wire'].text().strip())
    has_N = bool(self.inputs['N'].text().strip())
    
    if has_r:
        self.inputs['N'].setEnabled(False)
        self.inputs['L'].setEnabled(False)
    elif has_N:
        self.inputs['r_wire'].setEnabled(False)
    else:
        self.inputs['r_wire'].setEnabled(True)
        self.inputs['N'].setEnabled(True)
        self.inputs['L'].setEnabled(True)
```

### 4.2 Dependency Rules
```python
def enforce_dependencies(self):
    """Enforce field dependencies"""
    # Example: At least 3 of 4 variables needed for force calculation
    required_vars = ['I', 'L', 'B', 'theta']
    provided_vars = sum(1 for var in required_vars 
                       if self.inputs[var].text().strip())
    
    if provided_vars < 3:
        self.calculate_btn.setEnabled(False)
        self.calculate_btn.setToolTip("Need at least 3 variables")
    else:
        self.calculate_btn.setEnabled(True)
        self.calculate_btn.setToolTip("Ready to calculate")
```

## 5. Error Message Guidelines

### 5.1 User-Friendly Messages
- **Clear and specific**: "Current cannot be zero" vs "Invalid input"
- **Actionable**: "Please provide a positive value for length"
- **Contextual**: "Angle must be between 0° and 180° for this calculation"

### 5.2 Error Categories
```python
error_categories = {
    'input_validation': "Please check your input values",
    'insufficient_data': "Please provide more information",
    'physical_impossibility': "These values are physically impossible",
    'calculation_error': "Calculation failed - check your inputs",
    'convergence_error': "Calculation didn't converge"
}
```

## 6. Implementation Best Practices

### 6.1 Base Class Pattern
```python
class BaseCalculationTab(QWidget):
    def validate_field(self, field_name: str, text: str) -> bool:
        """Real-time validation for individual fields"""
        # Implementation here
    
    def apply_field_validation_rules(self, field_name: str, value: float) -> tuple[bool, str]:
        """Apply specific validation rules - override in subclasses"""
        return True, ""
    
    def handle_calculation_error(self, e: Exception) -> str:
        """Convert exceptions to user-friendly messages"""
        # Implementation here
```

### 6.2 Unit Conversion Validation
```python
def convert_units_with_validation(self, values: dict) -> dict:
    """Convert units with validation"""
    converted = values.copy()
    
    for field_name, value in values.items():
        if value is not None:
            try:
                unit = self.unit_combos[field_name].currentText()
                converted[field_name] = self.convert_unit(value, unit)
            except ValueError as e:
                raise InputValidationError(f"Invalid unit conversion for {field_name}: {e}")
    
    return converted
```

### 6.3 Calculation Error Handling
```python
def perform_calculation_with_validation(self, values: dict) -> dict:
    """Perform calculation with comprehensive error handling"""
    try:
        # Pre-calculation validation
        self.validate_all_inputs(values)
        
        # Unit conversion
        converted_values = self.convert_units_with_validation(values)
        
        # Perform calculation
        result = self.calculation_function(**converted_values)
        
        # Post-calculation validation
        self.validate_results(result)
        
        return result
        
    except ZeroDivisionError as e:
        raise PhysicsError("Division by zero occurred - check your inputs") from e
    except ValueError as e:
        raise InputValidationError(f"Invalid value in calculation: {e}") from e
    except Exception as e:
        raise PhysicsError(f"Calculation failed: {e}") from e
```

## 7. Testing Error Handling

### 7.1 Unit Tests
```python
def test_input_validation():
    """Test input validation rules"""
    # Test valid inputs
    assert validate_field('I', '5.0') == True
    
    # Test invalid inputs
    assert validate_field('I', '-5.0') == False
    assert validate_field('I', '0') == False
    assert validate_field('I', 'abc') == False

def test_error_messages():
    """Test error message generation"""
    try:
        raise InputValidationError("Current cannot be negative")
    except InputValidationError as e:
        message = handle_calculation_error(e)
        assert "Current cannot be negative" in message
```

### 7.2 Integration Tests
```python
def test_calculation_error_flow():
    """Test complete error handling flow"""
    # Setup invalid inputs
    tab = ForceOnWireTab()
    tab.inputs['I'].setText('0')  # Invalid current
    
    # Trigger calculation
    tab.calculate()
    
    # Verify error handling
    assert "Current cannot be zero" in tab.result_display.text()
```

## 8. Performance Considerations

### 8.1 Debounced Validation
```python
from PyQt6.QtCore import QTimer

class DebouncedValidator:
    def __init__(self, delay_ms=300):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.perform_validation)
    
    def validate_field(self, field_name: str, text: str):
        self.timer.stop()
        self.timer.start(300)  # 300ms delay
```

### 8.2 Caching Validation Results
```python
class ValidationCache:
    def __init__(self):
        self.cache = {}
    
    def get_cached_validation(self, field_name: str, value: str) -> tuple[bool, str]:
        cache_key = f"{field_name}:{value}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Perform validation
        result = self.perform_validation(field_name, value)
        self.cache[cache_key] = result
        return result
```

## 9. Future Enhancements

### 9.1 Machine Learning Validation
- **Pattern recognition**: Learn from user input patterns
- **Anomaly detection**: Identify unusual input combinations
- **Smart suggestions**: Suggest corrections for common errors

### 9.2 Advanced Visualization
- **Error highlighting**: Visual indicators for problematic inputs
- **Confidence indicators**: Show calculation confidence levels
- **Alternative suggestions**: Propose similar valid inputs

### 9.3 Accessibility Improvements
- **Screen reader support**: Proper ARIA labels for error messages
- **Keyboard navigation**: Full keyboard access to error states
- **High contrast mode**: Clear error indicators in all themes 