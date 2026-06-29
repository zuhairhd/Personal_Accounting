# Personal Finance Accounting Template

A clean, reusable local Flask personal accounting system for tracking income, expenses, assets, liabilities, loans, and net worth.

**App URL:** http://127.0.0.1:4444  
**Database:** personal_template.db  
**Port:** 4444 (not 5000 or 6000 — Firefox blocks 6000)

---

## What This Is

This is an **empty reusable template**. It contains:
- A default chart of accounts covering common personal finance needs
- No personal data, no transactions, no imported balances
- Full double-entry accounting system

Anyone can use this template to track their personal finances by entering their own opening balances and transactions.

---

## Setup (Windows)

```cmd
cd C:\dev\Personal_Accounting_Template
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open: **http://127.0.0.1:4444**

---

## First Run

On first startup:
1. `personal_template.db` is created automatically.
2. 50 default accounts are seeded (no balances, no transactions).
3. The dashboard shows all zero balances — ready for your data.

---

## Getting Started

1. Go to **Chart of Accounts** — review and customize account names if needed.
2. Go to **Opening Balances** — enter your current bank balances, cash, credit card balances, loans.
3. Check **Trial Balance** — should show Balanced ✓.
4. Start entering daily transactions via **Journal Entries → New Entry**.

---

## Default Chart of Accounts (50 Accounts)

| Range | Type | Examples |
|-------|------|---------|
| 1000–1999 | Asset | Wallet Cash, Bank Account 1, Savings, Loans to Others |
| 2000–2999 | Liability | Credit Card 1, Credit Card 2, Loan from Family, Loan from Friend |
| 3000–3999 | Equity | Opening Balance / Personal Capital |
| 4000–4999 | Income | Salary, Freelance, Rental, Other Income |
| 5000–5999 | Expense | Food, Rent, Electricity, Mobile, Medical, Education, etc. |

---

## Routes

| Route | Description |
|-------|-------------|
| `/` | Dashboard |
| `/accounts` | Chart of Accounts |
| `/journal-entries` | Journal Entries |
| `/journal-entries/new` | New Journal Entry |
| `/opening-balances` | Enter Opening Balances |
| `/people` | People |
| `/reports/trial-balance` | Trial Balance |
| `/reports/general-ledger` | General Ledger |
| `/reports/income-expense` | Income & Expense Statement |
| `/reports/profit-loss` | (alias for income-expense) |
| `/reports/balance-sheet` | Net Worth Statement |
| `/reports/account-statement` | Account Statement |
| `/reports/transactions-by-date` | Transactions by Date |
| `/reports/expenses-by-category` | Expenses by Category |
| `/bank-reconciliation` | Bank Reconciliation |
| `/import-export` | Export CSV |
| `/manual` | In-app User Manual |
| `/admin/reset-data` | Reset all data (requires RESET confirmation) |

---

## Reset Data

Visit **http://127.0.0.1:4444/admin/reset-data** to clear all transactions and restore the default accounts. Type `RESET` to confirm. This only affects `personal_template.db` — no other files or systems are touched.

---

## Backup

```cmd
copy C:\dev\Personal_Accounting_Template\personal_template.db C:\Backup\personal_template_backup.db
```

---

## Documentation

| File | Contents |
|------|---------|
| `USER_MANUAL.md` | Complete guide to all features |
| `SETUP_MANUAL.md` | Technical setup and troubleshooting |
| `QUICK_START.md` | 8-step quick start |
| In-app: `/manual` | Same manual accessible in the browser |

---

## Confirmation: No Personal Data

This template contains **no personal data**:
- No names, no private balances, no personal transactions
- No connection to any other accounting system (C:\dev\Account, C:\dev\FSS)
- No Excel files from any personal system
- Default accounts use generic names (Bank Account 1, Credit Card 1, etc.)

---

## Tech Stack

- Python 3, Flask, Flask-SQLAlchemy, SQLite
- Bootstrap 5, Bootstrap Icons
- OMR currency (3 decimal places)
