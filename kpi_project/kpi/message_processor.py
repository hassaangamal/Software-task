import re
from .interpreter import create_interpreter

from .models import Message

class MessageProcessor:
    def __init__(self, equation):
        self.equation = equation

    def process_message(self, message):
        """
        Process a message by evaluating the equation with the message's attribute value.

        The equation can contain "ATTR" which is replaced with the attribute value
        from the message.

        :param message: The message to process
        :return: The result of the equation as a string
        :raises ValueError: If the message does not contain a 'value' field
                            or the equation is invalid
        """
        attr_value = message.get("value")

        if not attr_value:
            raise ValueError("Message does not contain a 'value' field")

  
        try:
            # Replace "ATTR" in the equation with the attribute value
            expression = self.equation.replace("ATTR", str(attr_value))
            interpreter = create_interpreter(expression)
            result = interpreter.interpret()
            return str(result)
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {e}")
