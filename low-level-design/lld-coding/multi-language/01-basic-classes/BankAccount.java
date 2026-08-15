/*
 * Java Implementation: BankAccount Class
 * =======================================
 * Features:
 * - Classic class-based OOP
 * - Constructor with same name as class
 * - Private fields with getters
 * - Explicit types everywhere
 * - Strong encapsulation with private/public
 */

public class BankAccount {
    // Private instance variables
    private String accountNumber;
    private double balance;

    /**
     * Constructor - Creates a new bank account
     *
     * @param accountNumber Unique account identifier
     * @param initialBalance Starting balance
     */
    public BankAccount(String accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
        System.out.println("Created account: " + accountNumber);
    }

    /**
     * Overloaded constructor with default balance of 0
     */
    public BankAccount(String accountNumber) {
        this(accountNumber, 0.0);
    }

    /**
     * Deposit money into account
     *
     * @param amount Amount to deposit
     * @return true if successful, false otherwise
     */
    public boolean deposit(double amount) {
        if (amount <= 0) {
            System.out.println("Error: Deposit amount must be positive");
            return false;
        }

        this.balance += amount;
        System.out.printf("Deposited $%.2f%n", amount);
        return true;
    }

    /**
     * Withdraw money from account
     *
     * @param amount Amount to withdraw
     * @return true if successful, false if insufficient funds
     */
    public boolean withdraw(double amount) {
        if (amount <= 0) {
            System.out.println("Error: Withdrawal amount must be positive");
            return false;
        }

        if (amount > this.balance) {
            System.out.printf("Error: Insufficient funds. Balance: $%.2f%n", this.balance);
            return false;
        }

        this.balance -= amount;
        System.out.printf("Withdrew $%.2f%n", amount);
        return true;
    }

    /**
     * Get current account balance
     *
     * @return Current balance
     */
    public double getBalance() {
        return this.balance;
    }

    /**
     * Get account number
     *
     * @return Account number
     */
    public String getAccountNumber() {
        return this.accountNumber;
    }

    /**
     * String representation (like __str__ in Python)
     */
    @Override
    public String toString() {
        return String.format("Account %s: $%.2f", this.accountNumber, this.balance);
    }

    /**
     * Main method - Demo the BankAccount class
     */
    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("Java: Bank Account Example");
        System.out.println("============================================================");

        // Create account
        BankAccount account = new BankAccount("ACC001", 1000);
        System.out.printf("Initial balance: $%.2f%n%n", account.getBalance());

        // Deposit
        account.deposit(500);
        System.out.printf("After deposit of $500: $%.2f%n%n", account.getBalance());

        // Withdraw
        account.withdraw(200);
        System.out.printf("After withdrawal of $200: $%.2f%n%n", account.getBalance());

        // Failed withdrawal
        account.withdraw(2000);
        System.out.printf("Final balance: $%.2f%n%n", account.getBalance());

        // String representation
        System.out.println("Using toString(): " + account);
    }
}
