# Bad example 

# class Bird:
#     def fly(self):
#         print("Flying ...")

# class Sparrow(Bird):
#     def fly(self):
#         print("Sparrow flying ...")

# class Penguin(Bird):
#     def fly(self):
#         raise Exception("Penguins can't fly")

# def make_bird_fly(bird):
#     bird.fly()

# Good example
from abc import ABC, abstractmethod

class Bird(ABC):
    @abstractmethod
    def move(self):
        pass

class FlyingBird(Bird):
    def move(self):
        self.fly()
    def fly(self):
        print("Flying ...")
class Sparrow(FlyingBird):
    def fly(self):
        print("Sparrow flying ...")
class FlightlessBird(Bird):
    def move(self):
        self.walk()
    def walk(self):
        print("Walking ...")
class Penguin(FlightlessBird):
    def walk(self):
        print("Penguin walking ...")
    def swim(self):
        print("Penguin swimming ...")

def make_bird_move(bird):
    bird.move()
    

if __name__ == "__main__":
    make_bird_move(Sparrow())  # Works fine
    make_bird_move(Penguin())  # Works fine