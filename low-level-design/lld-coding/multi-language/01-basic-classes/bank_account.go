/*
Go Implementation: BankAccount Struct
======================================
Features:
- Struct-based (no classes)
- Constructor function (NewBankAccount)
- Receiver methods
- Private fields (lowercase)
- Public methods (uppercase)
*/

package main

import (
	"fmt"
)

// BankAccount represents a bank account with basic operations
// Note: Fields starting with uppercase are public, lowercase are private
type BankAccount struct {
	AccountNumber string
	balance       float64 // lowercase = private
}

// NewBankAccount creates a new bank account (constructor pattern)
func NewBankAccount(accountNumber string, initialBalance float64) *BankAccount {
	fmt.Printf("Created account: %s\n", accountNumber)
	return &BankAccount{
		AccountNumber: accountNumber,
		balance:       initialBalance,
	}
}

// Deposit adds money to the account
// (ba *BankAccount) is the receiver - like 'self' in Python
func (ba *BankAccount) Deposit(amount float64) bool {
	if amount <= 0 {
		fmt.Println("Error: Deposit amount must be positive")
		return false
	}

	ba.balance += amount
	fmt.Printf("Deposited $%.2f\n", amount)
	return true
}

// Withdraw removes money from the account
func (ba *BankAccount) Withdraw(amount float64) bool {
	if amount <= 0 {
		fmt.Println("Error: Withdrawal amount must be positive")
		return false
	}

	if amount > ba.balance {
		fmt.Printf("Error: Insufficient funds. Balance: $%.2f\n", ba.balance)
		return false
	}

	ba.balance -= amount
	fmt.Printf("Withdrew $%.2f\n", amount)
	return true
}

// GetBalance returns the current balance
func (ba *BankAccount) GetBalance() float64 {
	return ba.balance
}

// String implements the Stringer interface (like __str__ in Python)
func (ba *BankAccount) String() string {
	return fmt.Sprintf("Account %s: $%.2f", ba.AccountNumber, ba.balance)
}

func main() {
	fmt.Println("============================================================")
	fmt.Println("Go: Bank Account Example")
	fmt.Println("============================================================")

	// Create account
	account := NewBankAccount("ACC001", 1000)
	fmt.Printf("Initial balance: $%.2f\n\n", account.GetBalance())

	// Deposit
	account.Deposit(500)
	fmt.Printf("After deposit of $500: $%.2f\n\n", account.GetBalance())

	// Withdraw
	account.Withdraw(200)
	fmt.Printf("After withdrawal of $200: $%.2f\n\n", account.GetBalance())

	// Failed withdrawal
	account.Withdraw(2000)
	fmt.Printf("Final balance: $%.2f\n\n", account.GetBalance())

	// String representation
	fmt.Println("Using String():", account)
}
