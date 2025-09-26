"""
PQ-Torus Widget Implementation
Defines the torus T = C / L where L = Zp + Zqi with p and q prime.
"""

import re
from typing import Dict, Any


def is_prime(n: int) -> bool:
    """Check if a number is prime"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


class PQTorusWidget:
    """
    PQ-Torus widget implementation defining torus T = C / L where L = Zp + Zqi.
    
    Input: pair of integers (p, q) that should be prime
    Output: same pair with validation, torus description, and markdown display
    """
    
    def __init__(self, widget_schema: Dict[str, Any]):
        self.schema = widget_schema
        self.id = widget_schema['id']
        self.name = widget_schema['name']
        self.input_schema = widget_schema.get('input_schema', {})
        self.output_schema = widget_schema.get('output_schema', {})
    
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data against schema and apply defaults"""
        validated = {}
        
        # Get p and q values with defaults
        p = input_data.get('p', 11)
        q = input_data.get('q', 5)
        
        # Ensure they are integers
        try:
            validated['p'] = int(p)
            validated['q'] = int(q)
        except (ValueError, TypeError):
            raise ValueError(f"p and q must be integers, got p={p}, q={q}")
        
        # Validate range
        if not (2 <= validated['p'] <= 100):
            raise ValueError(f"p must be between 2 and 100, got {validated['p']}")
        if not (2 <= validated['q'] <= 100):
            raise ValueError(f"q must be between 2 and 100, got {validated['q']}")
        
        return validated
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute widget with validated input"""
        try:
            validated_input = self.validate_input(input_data)
            return self._execute_impl(validated_input)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'p': input_data.get('p', 11),
                'q': input_data.get('q', 5),
                'torus_description': f'Error defining torus: {str(e)}',
                'lattice_description': f'Invalid lattice parameters',
                'markdown_content': f'# PQ-Torus Error\n\n**Error**: {str(e)}',
                'prime_validation': {
                    'p_is_prime': False,
                    'q_is_prime': False,
                    'validation_message': f'Validation failed: {str(e)}'
                }
            }
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the PQ-Torus widget"""
        p = validated_input['p']
        q = validated_input['q']
        
        # Check if p and q are prime
        p_is_prime = is_prime(p)
        q_is_prime = is_prime(q)
        
        # Generate descriptions
        torus_description = f"T = ℂ / L where L = ℤ{p} + ℤ{q}i"
        lattice_description = f"L = ℤ{p} + ℤ{q}i (rectangular prime lattice)"
        
        # Validation message
        if p_is_prime and q_is_prime:
            validation_msg = f"Both {p} and {q} are prime numbers ✓"
        elif p_is_prime and not q_is_prime:
            validation_msg = f"{p} is prime, but {q} is not prime ⚠️"
        elif not p_is_prime and q_is_prime:
            validation_msg = f"{q} is prime, but {p} is not prime ⚠️"
        else:
            validation_msg = f"Neither {p} nor {q} are prime numbers ⚠️"
        
        # Generate markdown content
        markdown_content = self.generate_markdown(p, q, p_is_prime, q_is_prime)
        
        return {
            'success': True,
            'p': p,
            'q': q,
            'torus_description': torus_description,
            'lattice_description': lattice_description,
            'prime_validation': {
                'p_is_prime': p_is_prime,
                'q_is_prime': q_is_prime,
                'validation_message': validation_msg
            },
            'markdown_content': markdown_content,
            'metadata': {
                'lattice_type': 'rectangular_prime_lattice',
                'torus_equation': f'T = ℂ / (ℤ{p} + ℤ{q}i)',
                'fundamental_domain': {
                    'width': p,
                    'height': q,
                    'area': p * q
                },
                'execution_time': 0.001,  # Very fast computation
                'widget_id': 'pq-torus'
            }
        }
    
    def generate_markdown(self, p: int, q: int, p_is_prime: bool, q_is_prime: bool) -> str:
        """Generate markdown content displaying the torus information"""
        
        # Prime status indicators
        p_status = "✓ prime" if p_is_prime else "⚠️ not prime"
        q_status = "✓ prime" if q_is_prime else "⚠️ not prime"
        
        # Generate factorizations if not prime
        p_factors = self.get_prime_factorization(p) if not p_is_prime else ""
        q_factors = self.get_prime_factorization(q) if not q_is_prime else ""
        
        markdown = f"""# PQ-Torus: T = ℂ / L

## Lattice Definition
**L = ℤ{p} + ℤ{q}i** (rectangular lattice)

## Prime Parameters
- **p = {p}** ({p_status}){f" = {p_factors}" if p_factors else ""}
- **q = {q}** ({q_status}){f" = {q_factors}" if q_factors else ""}

## Torus Structure
The torus is defined as:
```
T = ℂ / L = ℂ / (ℤ{p} + ℤ{q}i)
```

### Fundamental Domain
- **Width**: {p} units
- **Height**: {q} units  
- **Area**: {p * q} square units

### Mathematical Properties
- **Lattice type**: Rectangular prime lattice
- **Basis vectors**: (p, 0) and (0, qi)
- **Periodicity**: Points z and z + np + mqi are equivalent for integers n,m

## Weierstrass Function Compatibility
This torus can be used with Weierstrass ℘-function widgets as it defines a rectangular lattice suitable for elliptic function analysis.

### Connection to ℘-function
The Weierstrass ℘-function for this lattice:
```
℘(z; p, qi) = 1/z² + Σ'[(1/(z-w)² - 1/w²)]
```
where the sum is over all non-zero lattice points w ∈ L.
"""
        
        return markdown
    
    def get_prime_factorization(self, n: int) -> str:
        """Get prime factorization of a number"""
        if n < 2:
            return str(n)
        
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        
        # Group identical factors
        from collections import Counter
        factor_counts = Counter(factors)
        
        factorization_parts = []
        for factor in sorted(factor_counts.keys()):
            count = factor_counts[factor]
            if count == 1:
                factorization_parts.append(str(factor))
            else:
                factorization_parts.append(f"{factor}^{count}")
        
        return " × ".join(factorization_parts)


# Widget schema definition for the pq-torus
PQ_TORUS_SCHEMA = {
    "id": "pq-torus",
    "name": "PQ-Torus",
    "description": "Defines torus T = C / L where L = Zp + Zqi with prime lattice parameters",
    "category": "computation",
    "icon": "🔴",
    "input_schemas": [
        "https://litlfred.github.io/notebooks/schemas/pq-torus.json#/definitions/prime_pair_input"
    ],
    "output_schemas": [
        "https://litlfred.github.io/notebooks/schemas/pq-torus.json#/definitions/prime_pair_output"  
    ],
    "python_script": "widgets/pq_torus.py"
}


def create_pq_torus_widget():
    """Factory function to create pq-torus widget instance"""
    return PQTorusWidget(PQ_TORUS_SCHEMA)


if __name__ == "__main__":
    # Test the pq-torus widget
    widget = create_pq_torus_widget()
    
    # Test with default prime values
    result = widget.execute({})
    print("Default execution (p=11, q=5):")
    print(f"Success: {result.get('success')}")
    print(f"Torus: {result.get('torus_description')}")
    print(f"Validation: {result.get('prime_validation', {}).get('validation_message')}")
    print()
    
    # Test with custom prime values
    result = widget.execute({"p": 7, "q": 13})
    print("Custom primes (p=7, q=13):")
    print(f"Success: {result.get('success')}")
    print(f"Validation: {result.get('prime_validation', {}).get('validation_message')}")
    print()
    
    # Test with non-prime values
    result = widget.execute({"p": 6, "q": 8})
    print("Non-prime values (p=6, q=8):")
    print(f"Success: {result.get('success')}")
    print(f"Validation: {result.get('prime_validation', {}).get('validation_message')}")
    print()
    
    # Test markdown output
    result = widget.execute({"p": 3, "q": 7})
    print("Markdown output sample:")
    print(result.get('markdown_content', '')[:200] + "...")