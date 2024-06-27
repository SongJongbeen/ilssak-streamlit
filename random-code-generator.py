import random

def random_code_generator():
    # generate a random code of digits and letters of length 12
    code = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=12))
    return code

# generate a random code
code = random_code_generator()
print(code)
