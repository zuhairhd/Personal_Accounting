# Personal Finance Accounting Template — Quick Start

**App URL:** http://127.0.0.1:4444  
**Time to complete:** ~5 minutes

---

## Step 1: Start the App

```cmd
cd C:\dev\Personal_Accounting_Template
venv\Scripts\activate
python app.py
```

Open Firefox and go to: **http://127.0.0.1:4444**

You will see the Dashboard with a welcome message and zero balances. This is correct — the template starts empty.

---

## Step 2: Review the Chart of Accounts

Go to **Chart of Accounts** in the sidebar.

You will see 50 default accounts:
- **1000–1999** — Cash, bank accounts, savings, loans to others (Assets)
- **2000–2999** — Credit cards, loans from family/friends (Liabilities)
- **3000–3999** — Personal capital / opening balance (Equity)
- **4000–4999** — Salary, freelance, rental income (Income)
- **5000–5999** — Food, rent, utilities, mobile, medical (Expenses)

---

## Step 3: Customize Account Names (Optional)

If you want, rename accounts to match your actual bank names:
- Click **Edit** next to "Bank Account 1" → rename to "OAB Bank" or your actual bank
- Click **Edit** next to "Credit Card 1" → rename to "Visa OAB"

You can also add new accounts that don't exist in the default list.

---

## Step 4: Enter Opening Balances

Go to **Opening Balances** in the sidebar.

Enter your current financial position:
- For each bank account: enter the current balance → select **Debit** (normal for assets)
- For wallet cash: enter current cash amount → select **Debit**
- For each credit card: enter the outstanding balance → select **Credit** (liability)
- For any loan you owe: enter the outstanding amount → select **Credit** (liability)

Leave all other accounts at zero.

Click **Record Opening Balances**.

---

## Step 5: Check the Trial Balance

Go to **Reports → Trial Balance**.

You should see **Balanced ✓** at the top.

If it shows NOT Balanced, go back to Opening Balances and check the amounts — something may have been entered on the wrong side.

---

## Step 6: Enter Daily Transactions

Go to **Journal Entries → New Entry**.

**Example — Salary received:**
- Date: today
- Narration: "Monthly salary — July 2026"
- Line 1: Bank Account 1 → Debit → 500.000
- Line 2: Salary Income → Credit → 500.000
- Balance bar shows ✓ → Click Save

**Example — Grocery expense:**
- Date: today
- Narration: "Lulu supermarket"
- Line 1: Food and Groceries → Debit → 25.000
- Line 2: Wallet Cash → Credit → 25.000
- Balance bar shows ✓ → Click Save

---

## Step 7: Review Your Reports

After entering transactions, check:

| Report | What It Shows |
|--------|--------------|
| **Trial Balance** | All accounts balanced? |
| **Income & Expense** | Surplus or deficit this period? |
| **Net Worth Statement** | Total assets vs liabilities |
| **Expenses by Category** | Where is your money going? |
| **General Ledger** | Full history of any single account |

---

## Step 8: Back Up Your Data

Your data is in `personal_template.db`. Back it up regularly:

```cmd
copy C:\dev\Personal_Accounting_Template\personal_template.db "C:\Backup\personal_template_backup.db"
```

---

## Common Transactions at a Glance

| Transaction | Debit | Credit |
|------------|-------|--------|
| Salary into bank | Bank Account 1 | Salary Income |
| Grocery (cash) | Food and Groceries | Wallet Cash |
| Grocery (credit card) | Food and Groceries | Credit Card 1 |
| Pay credit card bill | Credit Card 1 | Bank Account 1 |
| Pay electricity (bank) | Electricity and Water | Bank Account 1 |
| Borrow from family | Bank Account 1 | Loan from Family |
| Repay family loan | Loan from Family | Bank Account 1 |
| Lend money to someone | Loans to Others | Bank Account 1 |
| They repay you | Bank Account 1 | Loans to Others |
| Withdraw cash from bank | Wallet Cash | Bank Account 1 |

---

## Want to Start Fresh?

Go to: **Admin → Reset Data** in the sidebar.

Type `RESET` to confirm. All data is cleared. The 50 default accounts are restored.

---

*For full instructions see **USER_MANUAL.md** or visit http://127.0.0.1:4444/manual*
