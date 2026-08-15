# Machine Coding Interviews

> **🌍 Language Choice:** Machine coding requires working code in your chosen language.
> - **Python** 🐍 - Fast to write, most flexible (recommended for speed)
> - **Go** 🔷 - Clean and fast, good for systems problems
> - **Java** ☕ - Verbose but explicit, common at enterprise companies
> - **JavaScript** 💛 - Good for web-focused roles
>
> Resources:
> - [Choose Your Language](../lld-coding/multi-language/LANGUAGE-COMPARISON.md) - Pros/cons comparison
> - [Complete Working Examples](../COMPLETE-INTERVIEW-WALKTHROUGHS-MULTILANG.md) - All languages
> - [Practice Problems](../07-practice-problems/) - Full implementations

## Overview

Machine coding rounds are especially common at **Indian tech companies and startups** (Flipkart, Swiggy, Zepto, Razorpay, CRED, etc.). Unlike OOD interviews where pseudocode is acceptable, here you must build a **complete, working solution**.

## Format

- **Duration**: 90-120 minutes (sometimes 150 minutes)
- **Expectation**: Fully functional code that compiles and runs
- **Environment**: Your local IDE with your preferred language
- **Testing**: Your code must handle all test cases correctly

## What Makes It Different

| Aspect | OOD Interview | Machine Coding |
|--------|---------------|----------------|
| **Code Completeness** | Skeleton/pseudocode OK | Must be fully working |
| **Compilation** | Not required | Must compile |
| **Testing** | Discuss test cases | Must write and pass tests |
| **Time** | 45-60 minutes | 90-120 minutes |
| **Focus** | Design thinking | Design + implementation |

## What Interviewers Evaluate

### 1. Code Quality (40%)
- Is code clean and readable?
- Are variable/function names meaningful?
- Is code properly organized?
- Are there unnecessary comments or code?

### 2. Design (30%)
- Are classes well-structured?
- Is separation of concerns maintained?
- Are design patterns used appropriately?
- Is the code extensible?

### 3. Functionality (20%)
- Does it work correctly?
- Are all requirements met?
- Are edge cases handled?

### 4. Testing (10%)
- Are unit tests written?
- Do tests cover edge cases?
- Is test code also clean?

## Step-by-Step Approach

### Step 1: Read Requirements Carefully (5 min)

```
Problem: Design a Snake and Ladders Game

Requirements:
1. Support N players
2. Board size M x M
3. Snakes and ladders at specific positions
4. Players roll dice (1-6)
5. First player to reach end wins
6. Display game state after each move
```

### Step 2: Clarify & Note Assumptions (5 min)

Write down assumptions in comments:

```python
"""
ASSUMPTIONS:
1. Board starts at position 1, ends at M*M
2. If dice roll takes player beyond end, they don't move
3. Multiple players can be on same position
4. Snakes always go down, ladders always go up
5. No validation needed for snake/ladder positions
6. Players take turns in order
"""
```

### Step 3: Design Class Structure (10 min)

Quickly sketch classes on paper/comments:

```python
"""
CLASS STRUCTURE:
- Board: Manages board, snakes, ladders
- Player: Stores player info and position
- Dice: Generates random numbers
- Game: Orchestrates the game flow
- Snake: Represents a snake (start, end)
- Ladder: Represents a ladder (start, end)
"""
```

### Step 4: Implement Core Classes (60 min)

Build incrementally, test as you go:

```python
from dataclasses import dataclass
from typing import Dict, List
import random

# Step 4a: Create simple data classes first
@dataclass
class Snake:
    start: int
    end: int

    def __post_init__(self):
        if self.start <= self.end:
            raise ValueError("Snake start must be greater than end")

@dataclass
class Ladder:
    start: int
    end: int

    def __post_init__(self):
        if self.start >= self.end:
            raise ValueError("Ladder start must be less than end")

# Step 4b: Create Player class
class Player:
    def __init__(self, name: str, player_id: int):
        self.name = name
        self.player_id = player_id
        self.position = 0  # Start before the board

    def move(self, steps: int):
        self.position += steps

    def set_position(self, position: int):
        self.position = position

    def __str__(self):
        return f"{self.name} (Position: {self.position})"

# Step 4c: Create Dice class
class Dice:
    def __init__(self, sides: int = 6):
        self.sides = sides

    def roll(self) -> int:
        return random.randint(1, self.sides)

# Step 4d: Create Board class
class Board:
    def __init__(self, size: int):
        self.size = size
        self.end = size * size
        self.snakes: Dict[int, int] = {}
        self.ladders: Dict[int, int] = {}

    def add_snake(self, snake: Snake):
        if snake.start > self.end or snake.end < 1:
            raise ValueError("Invalid snake position")
        self.snakes[snake.start] = snake.end

    def add_ladder(self, ladder: Ladder):
        if ladder.start >= self.end or ladder.end > self.end:
            raise ValueError("Invalid ladder position")
        self.ladders[ladder.start] = ladder.end

    def get_final_position(self, position: int) -> int:
        """Check for snakes and ladders at position"""
        if position in self.snakes:
            print(f"  🐍 Snake! {position} → {self.snakes[position]}")
            return self.snakes[position]
        if position in self.ladders:
            print(f"  🪜 Ladder! {position} → {self.ladders[position]}")
            return self.ladders[position]
        return position

# Step 4e: Create Game class (most complex)
class SnakeAndLaddersGame:
    def __init__(self, board: Board, players: List[Player], dice: Dice):
        self.board = board
        self.players = players
        self.dice = dice
        self.current_player_index = 0
        self.is_game_over = False
        self.winner = None

    def play_turn(self):
        """Execute one turn for the current player"""
        if self.is_game_over:
            print("Game is already over!")
            return

        current_player = self.players[self.current_player_index]
        dice_value = self.dice.roll()

        print(f"\n{current_player.name}'s turn:")
        print(f"  Rolled: {dice_value}")
        print(f"  Current position: {current_player.position}")

        # Calculate new position
        new_position = current_player.position + dice_value

        # Check if move is valid
        if new_position > self.board.end:
            print(f"  Can't move! Would go beyond end ({self.board.end})")
        else:
            # Move player
            current_player.set_position(new_position)
            print(f"  Moved to: {new_position}")

            # Check for snake or ladder
            final_position = self.board.get_final_position(new_position)
            if final_position != new_position:
                current_player.set_position(final_position)

            print(f"  Final position: {current_player.position}")

            # Check for winner
            if current_player.position == self.board.end:
                self.is_game_over = True
                self.winner = current_player
                print(f"\n🎉 {current_player.name} WINS! 🎉")
                return

        # Move to next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def play_full_game(self, max_turns: int = 1000):
        """Play until someone wins or max turns reached"""
        turn_count = 0
        while not self.is_game_over and turn_count < max_turns:
            self.play_turn()
            turn_count += 1

        if not self.is_game_over:
            print("\nGame reached maximum turns without a winner!")

    def display_status(self):
        """Display current game status"""
        print("\n" + "="*50)
        print("GAME STATUS")
        print("="*50)
        for player in self.players:
            marker = "👑" if player == self.winner else "→"
            print(f"{marker} {player}")
        print("="*50)
```

### Step 5: Create Driver/Main Code (10 min)

```python
def main():
    # Create board
    board = Board(size=10)

    # Add snakes
    snakes = [
        Snake(99, 54),
        Snake(70, 55),
        Snake(52, 42),
        Snake(25, 2),
        Snake(95, 72)
    ]
    for snake in snakes:
        board.add_snake(snake)

    # Add ladders
    ladders = [
        Ladder(6, 25),
        Ladder(11, 40),
        Ladder(60, 85),
        Ladder(46, 90),
        Ladder(17, 69)
    ]
    for ladder in ladders:
        board.add_ladder(ladder)

    # Create players
    players = [
        Player("Alice", 1),
        Player("Bob", 2),
        Player("Charlie", 3)
    ]

    # Create dice
    dice = Dice(sides=6)

    # Create and play game
    game = SnakeAndLaddersGame(board, players, dice)

    print("🎲 SNAKE AND LADDERS GAME 🎲")
    print(f"Board size: {board.size}x{board.size}")
    print(f"Players: {', '.join(p.name for p in players)}\n")

    game.play_full_game()
    game.display_status()

if __name__ == "__main__":
    main()
```

### Step 6: Write Tests (10 min)

```python
import unittest

class TestSnakeAndLadders(unittest.TestCase):

    def setUp(self):
        self.board = Board(size=10)
        self.board.add_snake(Snake(14, 7))
        self.board.add_ladder(Ladder(3, 11))

    def test_player_creation(self):
        player = Player("Test", 1)
        self.assertEqual(player.position, 0)
        self.assertEqual(player.name, "Test")

    def test_player_move(self):
        player = Player("Test", 1)
        player.move(5)
        self.assertEqual(player.position, 5)

    def test_snake_descends(self):
        position = self.board.get_final_position(14)
        self.assertEqual(position, 7)

    def test_ladder_ascends(self):
        position = self.board.get_final_position(3)
        self.assertEqual(position, 11)

    def test_no_snake_or_ladder(self):
        position = self.board.get_final_position(5)
        self.assertEqual(position, 5)

    def test_invalid_snake(self):
        with self.assertRaises(ValueError):
            Snake(5, 10)  # Start should be greater than end

    def test_invalid_ladder(self):
        with self.assertRaises(ValueError):
            Ladder(10, 5)  # Start should be less than end

    def test_dice_roll(self):
        dice = Dice(6)
        for _ in range(100):
            roll = dice.roll()
            self.assertGreaterEqual(roll, 1)
            self.assertLessEqual(roll, 6)

    def test_game_winner(self):
        board = Board(size=3)  # Small board for quick test
        players = [Player("Winner", 1)]
        dice = Dice(6)
        game = SnakeAndLaddersGame(board, players, dice)

        # Manually set player to winning position
        players[0].set_position(9)
        self.assertEqual(game.is_game_over, False)

        # This should trigger win
        game.is_game_over = True
        game.winner = players[0]
        self.assertEqual(game.winner.name, "Winner")

if __name__ == "__main__":
    unittest.main()
```

## Time Management Strategy

```
Total: 120 minutes

00-05 min: Read problem, understand requirements
05-10 min: Clarify assumptions, note edge cases
10-20 min: Design class structure on paper/comments
20-80 min: Implement core functionality
80-95 min: Write driver code, test manually
95-110 min: Write unit tests
110-120 min: Final review, refactor, cleanup
```

## Common Patterns in Machine Coding

### Pattern 1: Game Simulation
- Chess, Tic-Tac-Toe, Snake & Ladders
- **Key**: Game loop, turn management, win conditions

### Pattern 2: Booking/Reservation Systems
- Movie tickets, restaurant tables, parking spots
- **Key**: Availability tracking, concurrent booking handling

### Pattern 3: Data Structure Implementation
- LRU Cache, Rate Limiter, Thread Pool
- **Key**: Efficient algorithms, proper data structure choice

### Pattern 4: Real-World Services
- Splitwise, Logging framework, Notification system
- **Key**: Business logic, service layers, extensibility

## Code Quality Checklist

### ✅ Clean Code
```python
# GOOD: Descriptive names
def calculate_player_final_position(current_position, dice_roll):
    pass

# BAD: Cryptic names
def calc(p, d):
    pass
```

### ✅ Proper Structure
```python
# GOOD: Clear separation
class GameEngine:
    pass

class GameDisplay:
    pass

class GameInput:
    pass

# BAD: Everything in one class
class Game:
    # 500 lines of mixed concerns
    pass
```

### ✅ Error Handling
```python
# GOOD: Handle errors
def add_player(self, player):
    if len(self.players) >= self.max_players:
        raise ValueError("Maximum players reached")
    self.players.append(player)

# BAD: No validation
def add_player(self, player):
    self.players.append(player)
```

### ✅ Constants
```python
# GOOD: Use constants
class Config:
    MIN_PLAYERS = 2
    MAX_PLAYERS = 4
    BOARD_SIZE = 10
    DICE_SIDES = 6

# BAD: Magic numbers
if len(players) > 4:  # What is 4?
    pass
```

## Interview Tips

1. **Set up your environment beforehand**: Know your IDE shortcuts
2. **Use version control**: Commit after each major milestone
3. **Test frequently**: Don't wait until the end
4. **Start with working code**: Then refactor
5. **Communicate**: If remote, explain what you're doing
6. **Don't over-engineer**: Solve the problem first
7. **Handle input validation**: Check for invalid inputs
8. **Use type hints**: Makes code more readable (Python 3.5+)

## Common Mistakes

### ❌ Spending too much time on design
**✅ Do**: Quick design (10 min), then start coding

### ❌ Not testing during development
**✅ Do**: Test each class as you build it

### ❌ Ignoring edge cases
**✅ Do**: List edge cases upfront

### ❌ Poor time management
**✅ Do**: Set timers for each phase

### ❌ Skipping the driver code
**✅ Do**: Write a working main() to demonstrate

## Practice Problems

1. **Snake and Ladders** (above example)
2. **Tic-Tac-Toe** with AI player
3. **LRU Cache** with O(1) operations
4. **Splitwise** expense sharing
5. **Vending Machine** with inventory
6. **Online Shopping Cart** with checkout
7. **Movie Ticket Booking** system
8. **ATM** with cash dispensing logic
9. **Elevator System** simulator
10. **Logger Framework** with different levels

## Sample Repository Structure

```
snake-and-ladders/
├── src/
│   ├── models/
│   │   ├── board.py
│   │   ├── player.py
│   │   ├── dice.py
│   │   └── game.py
│   ├── utils/
│   │   └── validators.py
│   └── main.py
├── tests/
│   ├── test_board.py
│   ├── test_player.py
│   └── test_game.py
├── requirements.txt
└── README.md
```

---

**Next**: Learn about [Concurrency Design Interviews](./concurrency-design.md)
