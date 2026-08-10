class BankAccount:
    def __init__(self, initial_balance):
        self.__balance = initial_balance
    
    @property
    def balance(self):
        return self.__balance
    
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            print(f"Deposited: {amount}. New balance: {self.__balance}")
        else:
            print("Deposit amount must be positive.")
    
    def withdraw(self, amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            print(f"Withdrew: {amount}. Remaining balance: {self.__balance}")
        else:
            raise ValueError("Invalid withdrawal amount or insufficient funds.")
        
# Example usage:
if __name__ == "__main__":
    account = BankAccount(1000)
    print(f"Initial balance: {account.balance}")
    
    account.deposit(500)
    account.withdraw(200)
    
    try:
        account.withdraw(2000)  # This should raise an error
    except ValueError as e:
        print(e)