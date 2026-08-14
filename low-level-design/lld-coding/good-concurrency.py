import threading

class BankAccount:
    def __init__(self, balance):
        self.__balance = balance
        self.__lock = threading.Lock()
    
    def withdraw(self, amount):
        with self.__lock:
            if self.__balance >= amount:
                print(f"Approved withdrawal of ${amount}")
                self.__balance -= amount
                return True
            return False
    @property
    def balance(self):
        return self.__balance
    
account = BankAccount(1000)

threads = [threading.Thread(target=account.withdraw, args=(1000,)) for _ in range(10)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
print(account.balance)