# Basic Classes - Multi-Language Comparison

The same `BankAccount` class implemented in Python, Go, Java, and JavaScript.

## What This Example Shows

- ✅ Class/Struct definition
- ✅ Constructor/initialization
- ✅ Instance variables
- ✅ Methods
- ✅ Encapsulation

## Comparison Table

| Feature | Python | Go | Java | JavaScript |
|---------|--------|-----|------|------------|
| Class keyword | `class` | `type ... struct` | `class` | `class` |
| Constructor | `__init__` | No constructor | `Constructor` | `constructor` |
| Instance var | `self.var` | `receiver.Var` | `this.var` | `this.var` |
| Method | `def method(self)` | `func (r Type) method()` | `public void method()` | `method() { }` |
| Private | `_var` convention | lowercase | `private` keyword | `#var` or `_var` |

## Key Differences

### Python
- **Pros**: Clean syntax, readable
- **Cons**: No true private fields (convention only)
- **Note**: `self` must be explicit

### Go
- **Pros**: Simple, fast, great concurrency
- **Cons**: No classes, must use structs
- **Note**: Methods defined outside struct

### Java
- **Pros**: Strong typing, IDE support
- **Cons**: Verbose, requires more boilerplate
- **Note**: Everything must be in a class

### JavaScript
- **Pros**: Flexible, works everywhere
- **Cons**: `this` binding issues, dynamic typing
- **Note**: Modern ES6+ class syntax is clean

## Running the Examples

```bash
# Python
python3 bank_account.py

# Go
go run bank_account.go

# Java
javac BankAccount.java && java BankAccount

# JavaScript
node bank_account.js
```

## Expected Output (All Languages)

```
Created account: ACC001
Initial balance: $1000.00
After deposit of $500: $1500.00
After withdrawal of $200: $1300.00
Failed withdrawal of $2000
Final balance: $1300.00
```
