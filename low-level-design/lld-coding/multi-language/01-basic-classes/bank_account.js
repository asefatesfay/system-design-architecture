/*
 * JavaScript Implementation: BankAccount Class
 * =============================================
 * Features:
 * - ES6 class syntax
 * - Constructor method
 * - Private fields with # (ES2022)
 * - Template literals for strings
 * - Dynamic typing
 */

class BankAccount {
    // Private fields (ES2022 feature)
    #balance;

    /**
     * Constructor - Creates a new bank account
     * @param {string} accountNumber - Unique account identifier
     * @param {number} initialBalance - Starting balance (default: 0)
     */
    constructor(accountNumber, initialBalance = 0) {
        this.accountNumber = accountNumber;
        this.#balance = initialBalance;
        console.log(`Created account: ${accountNumber}`);
    }

    /**
     * Deposit money into account
     * @param {number} amount - Amount to deposit
     * @returns {boolean} - true if successful, false otherwise
     */
    deposit(amount) {
        if (amount <= 0) {
            console.log("Error: Deposit amount must be positive");
            return false;
        }

        this.#balance += amount;
        console.log(`Deposited $${amount.toFixed(2)}`);
        return true;
    }

    /**
     * Withdraw money from account
     * @param {number} amount - Amount to withdraw
     * @returns {boolean} - true if successful, false if insufficient funds
     */
    withdraw(amount) {
        if (amount <= 0) {
            console.log("Error: Withdrawal amount must be positive");
            return false;
        }

        if (amount > this.#balance) {
            console.log(`Error: Insufficient funds. Balance: $${this.#balance.toFixed(2)}`);
            return false;
        }

        this.#balance -= amount;
        console.log(`Withdrew $${amount.toFixed(2)}`);
        return true;
    }

    /**
     * Get current account balance
     * @returns {number} - Current balance
     */
    getBalance() {
        return this.#balance;
    }

    /**
     * String representation (like __str__ in Python)
     * @returns {string}
     */
    toString() {
        return `Account ${this.accountNumber}: $${this.#balance.toFixed(2)}`;
    }
}

// Demo the BankAccount class
function main() {
    console.log("============================================================");
    console.log("JavaScript: Bank Account Example");
    console.log("============================================================");

    // Create account
    const account = new BankAccount("ACC001", 1000);
    console.log(`Initial balance: $${account.getBalance().toFixed(2)}\n`);

    // Deposit
    account.deposit(500);
    console.log(`After deposit of $500: $${account.getBalance().toFixed(2)}\n`);

    // Withdraw
    account.withdraw(200);
    console.log(`After withdrawal of $200: $${account.getBalance().toFixed(2)}\n`);

    // Failed withdrawal
    account.withdraw(2000);
    console.log(`Final balance: $${account.getBalance().toFixed(2)}\n`);

    // String representation
    console.log("Using toString():", account.toString());

    // Try to access private field (will fail)
    console.log("\nTrying to access private field directly:");
    console.log("account.#balance:", typeof account.balance === 'undefined' ? "❌ Cannot access private field" : account.balance);
}

// Run the demo
main();
