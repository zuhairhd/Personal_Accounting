# Personal Finance Accounting Template — Setup Manual

**App:** Personal Finance Accounting Template  
**URL:** http://127.0.0.1:4444  
**Location:** C:\dev\Personal_Accounting_Template  
**Port:** 4444 (not 5000 or 6000 — Firefox blocks 6000)

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [First-Time Setup](#2-first-time-setup)
3. [Starting the App](#3-starting-the-app)
4. [Stopping the App](#4-stopping-the-app)
5. [File Structure](#5-file-structure)
6. [Database](#6-database)
7. [Backup and Restore](#7-backup-and-restore)
8. [Updating Packages](#8-updating-packages)
9. [Resetting Data](#9-resetting-data)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. System Requirements

| Requirement | Minimum |
|------------|---------|
| Operating System | Windows 10 or Windows 11 |
| Python | 3.8 or higher (3.10+ recommended) |
| RAM | 256 MB free |
| Disk Space | 50 MB |
| Browser | Firefox, Chrome, or Edge |
| Port | 4444 must be available |

**Check Python version:**
```cmd
python --version
```

---

## 2. First-Time Setup

### Step 1: Navigate to the folder
```cmd
cd C:\dev\Personal_Accounting_Template
```

### Step 2: Create virtual environment
```cmd
python -m venv venv
```

### Step 3: Activate virtual environment
```cmd
venv\Scripts\activate
```

You will see `(venv)` at the start of your prompt.

### Step 4: Install dependencies
```cmd
pip install -r requirements.txt
```

Expected: `Successfully installed Flask-3.x.x Flask-SQLAlchemy-3.x.x ...`

### Step 5: Start the app
```cmd
python app.py
```

Expected output:
```
[template] First run — seeding default chart of accounts...
[template] 50 default accounts seeded.
[template] Database is empty and ready. No balances or transactions.
 * Running on http://127.0.0.1:4444
```

### Step 6: Open in browser
Navigate to: **http://127.0.0.1:4444**

The Dashboard will show zero balances and a welcome message.

---

## 3. Starting the App

Every time you want to use the app:

```cmd
cd C:\dev\Personal_Accounting_Template
venv\Scripts\activate
python app.py
```

Then open: **http://127.0.0.1:4444**

### One-Click Start (Optional Batch File)

Create `start.bat` in C:\dev\Personal_Accounting_Template:
```bat
@echo off
cd /d C:\dev\Personal_Accounting_Template
call venv\Scripts\activate
python app.py
```

Double-click `start.bat` to launch.

---

## 4. Stopping the App

In the command prompt where the app is running:
```
Ctrl + C
```

The app stops. All data is already saved in `personal_template.db` and is not lost.

---

## 5. File Structure

```
C:\dev\Personal_Accounting_Template\
├── app.py                          Main Flask application
├── personal_template.db            SQLite database (auto-created on first run)
├── requirements.txt                Flask, Flask-SQLAlchemy, openpyxl
├── README.md                       Project overview and route list
├── USER_MANUAL.md                  Complete user guide (25 sections)
├── SETUP_MANUAL.md                 This file
├── QUICK_START.md                  8-step quick start guide
├── venv\                           Python virtual environment
├── templates\
│   ├── base.html                   Sidebar layout
│   ├── dashboard.html              Dashboard with welcome banner
│   ├── accounts.html               Chart of accounts list
│   ├── account_form.html           Add/edit account
│   ├── journal_entries.html        Journal entries list
│   ├── journal_entry_detail.html   View single entry
│   ├── journal_entry_form.html     Create/edit entry (live balance check)
│   ├── opening_balances.html       Opening balances page
│   ├── people.html                 People list
│   ├── person_form.html            Add/edit person
│   ├── trial_balance.html          Trial balance report
│   ├── general_ledger.html         General ledger
│   ├── income_expense.html         Income & expense statement
│   ├── balance_sheet.html          Net worth statement
│   ├── transactions_by_date.html   Transactions by date
│   ├── expenses_by_category.html   Expenses by category
│   ├── bank_reconciliation.html    Bank reconciliation list
│   ├── reconciliation_form.html    Add/edit reconciliation
│   ├── import_export.html          Export page
│   ├── admin_reset.html            Reset data with confirmation
│   └── manual.html                 In-app user manual
└── static\
    └── style.css                   Custom CSS
```

---

## 6. Database

The SQLite database file: **personal_template.db**

| Table | Contents |
|-------|----------|
| `account` | Chart of accounts |
| `journal_entry` | Transaction headers |
| `journal_line` | Individual debit/credit lines |
| `person` | People records |
| `bank_reconciliation` | Reconciliation records |

**To inspect directly:** Use [DB Browser for SQLite](https://sqlitebrowser.org/) (free).

**To reset:** Use the in-app reset page at `/admin/reset-data`. Type `RESET` to confirm.

---

## 7. Backup and Restore

### Backup
```cmd
copy C:\dev\Personal_Accounting_Template\personal_template.db "C:\Backup\personal_template_%date:~-4,4%%date:~-7,2%%date:~0,2%.db"
```

### Create backup folder if needed
```cmd
mkdir "C:\Backup"
```

### Restore
1. Stop the app (Ctrl+C).
2. Replace the database:
```cmd
copy "C:\Backup\personal_template_20260629.db" C:\dev\Personal_Accounting_Template\personal_template.db
```
3. Start the app again.

---

## 8. Updating Packages

```cmd
cd C:\dev\Personal_Accounting_Template
venv\Scripts\activate
pip install --upgrade Flask Flask-SQLAlchemy openpyxl
```

Test all routes after upgrading.

---

## 9. Resetting Data

To clear all data and start fresh:

1. Open: **http://127.0.0.1:4444/admin/reset-data**
2. Review the warning (shows counts of data to be deleted).
3. Type `RESET` in the confirmation box.
4. Click Reset All Data.

After reset:
- All journal entries, people, and reconciliation records are deleted.
- All accounts are deleted and the 50 default accounts are restored.
- The database file is kept.

This only affects `personal_template.db` inside C:\dev\Personal_Accounting_Template. Nothing else is changed.

---

## 10. Troubleshooting

### Problem 1: "python is not recognized"
**Fix:** Install Python from python.org. Check "Add Python to PATH" during installation. Restart the command prompt.

---

### Problem 2: Port 4444 is already in use
**Symptom:** `OSError: [WinError 10048] Only one usage of each socket address`

**Fix:** Find the process using port 4444:
```cmd
netstat -ano | findstr :4444
```
Note the PID, then:
```cmd
taskkill /PID [PID] /F
```
Then restart the app.

---

### Problem 3: Browser shows "This site can't be reached"
**Fix:**
1. Make sure the command prompt shows `* Running on http://127.0.0.1:4444`
2. Use exactly `http://127.0.0.1:4444` — not `https`, not `localhost:4444`
3. Try a different browser

---

### Problem 4: "ModuleNotFoundError: No module named 'flask'"
**Fix:** Virtual environment is not activated or packages not installed:
```cmd
cd C:\dev\Personal_Accounting_Template
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

---

### Problem 5: Trial Balance shows NOT Balanced
**Fix:**
1. Go to Journal Entries.
2. Look for entries where the Balanced column shows ✗.
3. Click the entry and check the amounts — fix the unequal lines.

---

### Problem 6: Reset page does not work without confirmation
This is by design. You must type the word `RESET` exactly (all capitals) in the confirmation field before the reset will proceed.

---

### Problem 7: App is slow to load
**Fix:**
1. Clear browser cache (Ctrl+Shift+Delete).
2. Restart the app.

---

## Quick Reference

| Task | Command |
|------|---------|
| Navigate to app | `cd C:\dev\Personal_Accounting_Template` |
| Activate venv | `venv\Scripts\activate` |
| Start app | `python app.py` |
| Stop app | `Ctrl+C` |
| Install packages | `pip install -r requirements.txt` |
| Backup database | `copy personal_template.db C:\Backup\backup.db` |

---

*Personal Finance Accounting Template — Setup Manual*  
*Port: 4444 | URL: http://127.0.0.1:4444*
