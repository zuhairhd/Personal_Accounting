# Personal Finance Accounting Template — User Manual

**App:** Personal Finance Accounting Template  
**URL:** http://127.0.0.1:4444  
**Currency:** OMR (Omani Rial, 3 decimal places)  
**Database:** personal_template.db

> This is a clean, empty template. It contains no personal data, no private balances, and no imported transactions. All data you enter is your own.

---

## Table of Contents

1. [What This System Is](#1-what-this-system-is)
2. [Why It Starts Empty](#2-why-it-starts-empty)
3. [Double-Entry Accounting Basics](#3-double-entry-accounting-basics)
4. [What Debit and Credit Mean](#4-what-debit-and-credit-mean)
5. [Account Types Explained](#5-account-types-explained)
6. [Setting Up Your Accounts](#6-setting-up-your-accounts)
7. [Entering Opening Balances](#7-entering-opening-balances)
8. [Recording Daily Transactions](#8-recording-daily-transactions)
9. [How to Record Salary](#9-how-to-record-salary)
10. [How to Record Expenses](#10-how-to-record-expenses)
11. [Credit Card Purchases](#11-credit-card-purchases)
12. [Paying a Credit Card Bill](#12-paying-a-credit-card-bill)
13. [Loan from Family or Friend](#13-loan-from-family-or-friend)
14. [Lending Money to Someone Else](#14-lending-money-to-someone-else)
15. [Repayment from Someone](#15-repayment-from-someone)
16. [Reading the Trial Balance](#16-reading-the-trial-balance)
17. [Reading the Income and Expense Statement](#17-reading-the-income-and-expense-statement)
18. [Reading the Net Worth Statement](#18-reading-the-net-worth-statement)
19. [Bank Reconciliation](#19-bank-reconciliation)
20. [People Module](#20-people-module)
21. [Import and Export](#21-import-and-export)
22. [Backup Your Database](#22-backup-your-database)
23. [Resetting Data Safely](#23-resetting-data-safely)
24. [Month-End Checklist](#24-month-end-checklist)
25. [Common Mistakes and How to Fix Them](#25-common-mistakes-and-how-to-fix-them)

---

## 1. What This System Is

This is a **personal double-entry accounting system** that helps you:

- Track all your bank accounts, cash, and savings in one place
- Monitor credit card balances and payments
- Categorize income (salary, freelance, rental) and expenses (food, utilities, etc.)
- Track loans you have borrowed or lent to others
- Calculate your net worth (what you own minus what you owe)
- Generate financial reports (income & expense, balance sheet, trial balance)

The system uses **double-entry bookkeeping** — the same method used by professional accountants worldwide. Every transaction is recorded in at least two accounts, ensuring your books always balance.

---

## 2. Why It Starts Empty

This is a reusable template, not a pre-filled personal finance file. It starts with:
- A default chart of 50 accounts (generic names like "Bank Account 1", "Credit Card 1")
- Zero balances everywhere
- No transactions

**This is intentional.** Different people have different banks, different accounts, and different starting balances. You customize the account names and enter your own opening balances.

---

## 3. Double-Entry Accounting Basics

The core rule of double-entry accounting:

> **Every transaction must have equal Debit and Credit amounts.**

Think of it this way: when money moves, it always comes from somewhere and goes somewhere. Both the source and the destination must be recorded.

**Example:** You receive your salary of 500.000 OMR into your bank.
- Money enters your Bank Account (Bank Account 1 increases)
- Salary Income is recognized (Salary Income increases)

Both sides: 500.000 = 500.000 ✓

---

## 4. What Debit and Credit Mean

In personal accounting, "debit" and "credit" do NOT mean what they mean in everyday banking. They are simply labels for the two sides of every transaction.

| Account Type | Normal Balance | Grows With | Shrinks With |
|-------------|----------------|-----------|-------------|
| Asset | Debit | Debit | Credit |
| Liability | Credit | Credit | Debit |
| Equity | Credit | Credit | Debit |
| Income | Credit | Credit | Debit |
| Expense | Debit | Debit | Credit |

**Memory aid:**
- **Debit** = left side of the accounting equation
- **Credit** = right side of the accounting equation
- Assets and Expenses naturally sit on the left (debit side)
- Liabilities, Equity, and Income naturally sit on the right (credit side)

---

## 5. Account Types Explained

**Asset** — Things you own or money owed to you.
- Examples: Wallet Cash, Bank Account 1, Savings Account, Loans to Others

**Liability** — Money you owe to others.
- Examples: Credit Card 1, Loan from Family, Loan from Friend

**Equity** — Your personal net worth / capital.
- Examples: Opening Balance / Personal Capital, Owner Drawings

**Income** — Money coming in.
- Examples: Salary Income, Freelance Income, Rental Income

**Expense** — Money going out (spending).
- Examples: Food and Groceries, Rent / Housing, Electricity, Medical

---

## 6. Setting Up Your Accounts

The system includes 50 default accounts. You can:

**Rename accounts** to match your actual bank or card names:
- "Bank Account 1" → "OAB Current Account"
- "Credit Card 1" → "Visa OAB"
- "Salary Income" → "Government Salary"

**Add new accounts** that are specific to you:
- A specific savings account not in the defaults
- A new expense category (e.g., "Gym Membership")

**Deactivate accounts** you don't need (they won't appear in forms but history is kept).

**To edit:** Sidebar → Chart of Accounts → Click Edit next to any account.  
**To add:** Click New Account and fill in code, name, and type.

---

## 7. Entering Opening Balances

Opening balances are your account amounts **before** you start using the system. Enter them once at the beginning.

Go to: **Opening Balances** in the sidebar.

**Which accounts need opening balances?**
- Wallet Cash — how much cash do you currently have?
- Each bank account — what is your current balance?
- Each credit card — what is the current outstanding balance?
- Loans from family/friends — how much do you currently owe?
- Loans to others — how much does someone owe you?

**Opening balance sides (which side to select):**

| Account | Side |
|---------|------|
| Cash / Bank / Savings | Debit (assets go on debit side) |
| Loans to Others | Debit (it's an asset — someone owes you) |
| Credit Card balance | Credit (liability — you owe the bank) |
| Loan from Family | Credit (liability — you owe them) |
| Opening Balance / Personal Capital | Auto-balanced by the system |

**Example opening balances:**

| Account | Amount | Side |
|---------|--------|------|
| Wallet Cash | 80.000 | Debit |
| Bank Account 1 | 450.000 | Debit |
| Savings Account | 1,200.000 | Debit |
| Credit Card 1 | 350.000 | Credit |
| Loan from Family | 500.000 | Credit |

The system automatically balances the entry using **Opening Balance / Personal Capital**.

After saving, verify the **Trial Balance** shows **Balanced ✓**.

---

## 8. Recording Daily Transactions

Go to: **Journal Entries → New Entry**

Fill in:
1. **Date** — the date of the transaction
2. **Narration** — a short description ("July salary", "Lulu supermarket", etc.)
3. **Lines** — at least two lines, each with an account and either a debit or credit amount
4. **Check the balance bar** — it must show ✓ Balanced before saving

Reference numbers are auto-generated: **PJ-2026-0001**

---

## 9. How to Record Salary

Salary of 500.000 OMR deposited into Bank Account 1:

| Account | Debit | Credit |
|---------|-------|--------|
| Bank Account 1 | 500.000 | |
| Salary Income | | 500.000 |

If salary is received as cash:

| Account | Debit | Credit |
|---------|-------|--------|
| Wallet Cash | 500.000 | |
| Salary Income | | 500.000 |

---

## 10. How to Record Expenses

**Groceries 30.000 OMR paid with wallet cash:**

| Account | Debit | Credit |
|---------|-------|--------|
| Food and Groceries | 30.000 | |
| Wallet Cash | | 30.000 |

**Electricity bill 25.000 OMR paid from Bank Account 1:**

| Account | Debit | Credit |
|---------|-------|--------|
| Electricity and Water | 25.000 | |
| Bank Account 1 | | 25.000 |

**Multiple expenses in one entry (e.g., all bills paid from bank):**

| Account | Debit | Credit |
|---------|-------|--------|
| Internet | 8.000 | |
| Mobile / Telephone | 5.000 | |
| Electricity and Water | 22.000 | |
| Bank Account 1 | | 35.000 |

Total Debit = Total Credit = 35.000 ✓

---

## 11. Credit Card Purchases

When you buy something with a credit card:
- The expense increases (debit the expense)
- The credit card balance increases (credit the card — you owe more)

**Restaurant meal 40.000 OMR on Credit Card 1:**

| Account | Debit | Credit |
|---------|-------|--------|
| Food and Groceries | 40.000 | |
| Credit Card 1 | | 40.000 |

**Fuel 22.000 OMR on Credit Card 2:**

| Account | Debit | Credit |
|---------|-------|--------|
| Fuel | 22.000 | |
| Credit Card 2 | | 22.000 |

---

## 12. Paying a Credit Card Bill

When you pay your credit card statement:
- The credit card balance decreases (debit the card — reducing what you owe)
- The bank balance decreases (credit the bank)

**Pay Credit Card 1 bill of 200.000 OMR from Bank Account 1:**

| Account | Debit | Credit |
|---------|-------|--------|
| Credit Card 1 | 200.000 | |
| Bank Account 1 | | 200.000 |

> **Important:** Paying a credit card bill is NOT an expense. The expenses were recorded when you made each purchase. The payment just clears the liability.

---

## 13. Loan from Family or Friend

When you borrow money from a family member or friend:
- Your bank balance increases (debit bank — you received money)
- Your loan liability increases (credit the loan account — you owe them)

**Borrow 800.000 OMR from family into Bank Account 1:**

| Account | Debit | Credit |
|---------|-------|--------|
| Bank Account 1 | 800.000 | |
| Loan from Family | | 800.000 |

**Repay 200.000 OMR of the loan:**

| Account | Debit | Credit |
|---------|-------|--------|
| Loan from Family | 200.000 | |
| Bank Account 1 | | 200.000 |

---

## 14. Lending Money to Someone Else

When you lend money to another person:
- Your "Loans to Others" asset increases (debit — they owe you)
- Your bank or cash decreases (credit — you gave them money)

**Lend 300.000 OMR to a friend from Bank Account 1:**

| Account | Debit | Credit |
|---------|-------|--------|
| Loans to Others | 300.000 | |
| Bank Account 1 | | 300.000 |

---

## 15. Repayment from Someone

When the person repays part or all of what they owe you:

**Friend returns 150.000 OMR in cash:**

| Account | Debit | Credit |
|---------|-------|--------|
| Wallet Cash | 150.000 | |
| Loans to Others | | 150.000 |

The Loans to Others balance decreases — they still owe 150.000 OMR.

---

## 16. Reading the Trial Balance

**Route:** /reports/trial-balance

The trial balance lists every account with a non-zero balance in two columns:
- **Debit column** — accounts with debit balances (assets, expenses)
- **Credit column** — accounts with credit balances (liabilities, equity, income)

The totals at the bottom must be equal.

| Result | Meaning |
|--------|---------|
| **Balanced ✓** | Your books are correct |
| **NOT Balanced ✗** | Something is wrong — a transaction was entered incorrectly |

Use date filters to see the trial balance for a specific period.

---

## 17. Reading the Income and Expense Statement

**Route:** /reports/income-expense

This report shows:
- All income accounts with their totals
- All expense accounts with their totals
- The **Surplus** (if income > expenses) or **Deficit** (if expenses > income)

**Formula:** Surplus / Deficit = Total Income − Total Expenses

A surplus means you earned more than you spent — your savings are growing.  
A deficit means you spent more than you earned — you are drawing down savings or going into debt.

Use date filters to see a specific month or period.

---

## 18. Reading the Net Worth Statement

**Route:** /reports/balance-sheet

This report shows your complete financial position:

**Assets** = Everything you own (cash, bank, savings)  
**Liabilities** = Everything you owe (credit cards, loans)  
**Equity** = Your personal capital + current year result  
**Net Worth** = Total Assets − Total Liabilities

A **positive net worth** means you own more than you owe — financially healthy.  
A **negative net worth** means your debts exceed your assets.

This report should balance: **Assets = Liabilities + Equity**

---

## 19. Bank Reconciliation

Bank reconciliation compares what your system shows (book balance) against your actual bank statement.

**Route:** /bank-reconciliation → New Reconciliation

Steps:
1. Get your bank statement for the end of the month.
2. Select the bank account.
3. Enter the statement date, your book balance (from General Ledger), and the bank statement balance.
4. The system shows the difference.
5. Investigate and resolve any difference.

Reconcile monthly for each bank account and credit card.

---

## 20. People Module

**Route:** /people

Add people who appear in your financial transactions:
- Family members you lend to or borrow from
- Tenants paying you rent
- Employers paying salary
- Friends who owe you or you owe them

Fields:
- Name (required)
- Relationship / Category (e.g., Family, Friend, Employer, Tenant)
- Phone, Email, Notes

When creating a journal entry, you can optionally link it to a person for reference.

---

## 21. Import and Export

**Route:** /import-export

Export any report to CSV (can be opened in Excel):
- Chart of Accounts
- Journal Entries (all lines)
- Trial Balance
- Income & Expense Statement
- Net Worth Statement (Balance Sheet)

---

## 22. Backup Your Database

All your data is in one file: **personal_template.db**

**Backup command:**
```cmd
copy C:\dev\Personal_Accounting_Template\personal_template.db "C:\Backup\personal_template_%date:~-4,4%%date:~-7,2%%date:~0,2%.db"
```

**Restore:** Stop the app, replace `personal_template.db` with your backup copy, restart.

Back up at least once a week. If you enter many daily transactions, back up daily.

---

## 23. Resetting Data Safely

**Route:** /admin/reset-data

The reset page:
1. Shows a count of all current data (entries, people, accounts, reconciliations).
2. Warns you clearly that this cannot be undone.
3. Requires you to type **RESET** exactly (capital letters) to confirm.
4. After reset: all data is deleted and the 50 default accounts are restored.

**What reset does:**
- Deletes all journal entries and lines
- Deletes all people records
- Deletes all reconciliation records
- Deletes all accounts
- Restores the default 50-account chart of accounts

**What reset does NOT do:**
- Does not delete the database file itself
- Does not touch any files outside C:\dev\Personal_Accounting_Template
- Does not affect any other accounting system on your computer

> Always back up `personal_template.db` before resetting.

---

## 24. Month-End Checklist

At the end of each month:

- [ ] Enter all remaining transactions for the month.
- [ ] Check Trial Balance — must show **Balanced ✓**.
- [ ] Review Income & Expense Statement — check surplus or deficit.
- [ ] Review Expenses by Category — identify where you are overspending.
- [ ] Reconcile each bank account and credit card.
- [ ] Review Net Worth Statement — is it improving?
- [ ] Export CSV reports and save as a monthly archive.
- [ ] Back up `personal_template.db`.

---

## 25. Common Mistakes and How to Fix Them

**Mistake 1: Trial Balance is NOT Balanced**  
Cause: A journal entry has unequal debits and credits.  
Fix: Go to Journal Entries. Look for entries showing ✗ in the Balanced column. Edit and correct them.

**Mistake 2: Recorded an expense to the wrong account**  
Fix: Edit the journal entry (click Edit). Change the account on the incorrect line and save.

**Mistake 3: Entered the wrong amount**  
Fix: Edit the journal entry. Update the amount on the relevant line. Save. The system recalculates.

**Mistake 4: Forgot to enter a transaction**  
Fix: Create a new journal entry with the correct date and amounts. The system accepts back-dated entries.

**Mistake 5: Entered an expense instead of a payment of a credit card bill**  
Fix: Credit card bill payments are NOT expenses. The entry should be:  
Debit Credit Card → Credit Bank. If you entered Debit Expense → Credit Bank, that was wrong.  
Delete the incorrect entry and create the correct one.

**Mistake 6: Forgot to enter opening balances**  
Fix: Go to Opening Balances and enter them. They will be saved as an OB-YYYY-0001 reference entry dated the day you enter them.

**Mistake 7: App shows "this site can't be reached"**  
Fix: The app is not running. Open a command prompt and run: `cd C:\dev\Personal_Accounting_Template && venv\Scripts\activate && python app.py`

---

*Personal Finance Accounting Template — User Manual*  
*Currency: OMR (3 decimal places) | Port: 4444 | URL: http://127.0.0.1:4444*
