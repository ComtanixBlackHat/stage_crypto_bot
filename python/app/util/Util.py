import random
import string

class UTIL:
    @staticmethod
    def generate_random_string(length: int = 20) -> str:
        """Generates a random string of the specified length."""
        # Define the characters to choose from (letters and digits)
        characters = string.ascii_letters + string.digits
        # Generate a random string by randomly choosing from the characters
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

# # Example usage
# print(UTIL.generate_random_string(20))
