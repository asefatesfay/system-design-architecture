import threading
import time

class BankAccount:
    def __init__(self, balance):
        self.__balance = balance
        
    def withdraw(self, amount):
        if self.__balance >= amount:
            print(f"Approved withdrawal of ${amount}")
            time.sleep(0.001) # Simulating network delay
            
            self.__balance -= amount
            return True
        return False
    
    @property
    def balance(self):
        return self.__balance

def attack(account, amount):
    account.withdraw(amount)
    
# Usage example
if __name__ == "__main__":
    account = BankAccount(1000)
    
    threads = [threading.Thread(target=attack, args=(account, 1000)) for _ in range(10)]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print(account.balance)
    