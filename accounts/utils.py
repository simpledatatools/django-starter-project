import string
import random

# Creates in initial username with random characters
def create_username(name):
        name = name.replace(" ", "")
        choices = string.ascii_letters + string.hexdigits
        choice = "".join(random.choice(choices) for _ in range(10))
        username = f'{name}{choice}'
        return username