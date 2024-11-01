import re

def is_valid_equation(equation):
    try:
        # Check for arithmetic expressions with "ATTR"
        if "ATTR" in equation and not equation.startswith("Regex"):
            # Try to replace ATTR with a number and use eval to validate
            test_expression = equation.replace("ATTR", "1")
            eval(test_expression)  # Using eval to check arithmetic validity
            return True

        # Check for Regex pattern: Regex("ATTR", "pattern")
        # Simplified regex to match the entire pattern
        regex_match = re.match(r'^Regex\("ATTR",\s*".*"\)$', equation)
        if regex_match:
            return True

    except Exception:
        return False

    return False
