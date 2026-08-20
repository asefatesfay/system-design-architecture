import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.6f} seconds")
        return result
    return wrapper

# BAD: Loads everything into memory at once

@timer
def get_squares_bad(n):
    return [i ** 2 for i in range(n)]

@timer
def get_squares_good(n):
    for i in range(n):
        yield i ** 2

if __name__ == "__main__":
    squares = get_squares_bad(1000000)
    print(squares[:10])  # Print first 10000 squares

    squares_gen = get_squares_good(1000000)
    print([next(squares_gen) for _ in range(10)])  # Print first 10000 squares from generator