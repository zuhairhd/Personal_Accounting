import os
import csv
import io
from datetime import date, datetime
from decimal import Decimal
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   flash, make_response, session)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'personal-accounting-template-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(basedir, 'personal_template.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ── Login credentials — change these before sharing the app ──
LOGIN_USERNAME = 'admin'
LOGIN_PASSWORD = 'admin123'

db = SQLAlchemy(app)

ACCOUNT_TYPES = ['Asset', 'Liability', 'Equity', 'Income', 'Expense']


# ─────────────────────────── AUTH ───────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────── MODELS ───────────────────────────

class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    parent_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    parent = db.relationship('Account', remote_side='Account.id',
                             backref=db.backref('children', lazy='dynamic'))

    @property
    def computed_normal_balance(self):
        if self.account_type in ('Asset', 'Expense'):
            return 'Debit'
        return 'Credit'

    @property
    def is_bank_or_cash(self):
        name_lower = self.name.lower()
        return any(k in name_lower for k in ('bank', 'cash', 'wallet', 'savings', 'account'))


class JournalEntry(db.Model):
    __tablename__ = 'journal_entry'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    reference = db.Column(db.String(50), unique=True)
    narration = db.Column(db.Text, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    lines = db.relationship('JournalLine', backref='entry',
                            cascade='all, delete-orphan',
                            order_by='JournalLine.id')
    person = db.relationship('Person', foreign_keys=[person_id])

    @property
    def total_debit(self):
        return sum(dec(l.debit) for l in self.lines)

    @property
    def total_credit(self):
        return sum(dec(l.credit) for l in self.lines)

    @property
    def is_balanced(self):
        return self.total_debit == self.total_credit


class JournalLine(db.Model):
    __tablename__ = 'journal_line'
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    debit = db.Column(db.Numeric(15, 3), default=Decimal('0'))
    credit = db.Column(db.Numeric(15, 3), default=Decimal('0'))
    description = db.Column(db.String(500))
    account = db.relationship('Account')


class Person(db.Model):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    relationship_or_category = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)


class BankReconciliation(db.Model):
    __tablename__ = 'bank_reconciliation'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    statement_date = db.Column(db.Date, nullable=False)
    book_balance = db.Column(db.Numeric(15, 3), default=Decimal('0'))
    statement_balance = db.Column(db.Numeric(15, 3), default=Decimal('0'))
    difference = db.Column(db.Numeric(15, 3), default=Decimal('0'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    account = db.relationship('Account')


# ─────────────────────────── HELPERS ───────────────────────────

def omr(value):
    if value is None:
        return '0.000 OMR'
    try:
        return f'{float(value):,.3f} OMR'
    except (TypeError, ValueError):
        return '0.000 OMR'


app.jinja_env.globals['omr'] = omr


@app.context_processor
def inject_globals():
    return {'now': datetime.utcnow()}


def dec(value):
    if value is None:
        return Decimal('0')
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal('0')


def parse_amount(value):
    if not value or str(value).strip() == '':
        return Decimal('0')
    try:
        v = Decimal(str(value).replace(',', '').strip())
        return v if v >= 0 else None
    except Exception:
        return None


def generate_reference(entry_date=None):
    if entry_date is None:
        entry_date = date.today()
    year = entry_date.year if isinstance(entry_date, date) else date.today().year
    count = JournalEntry.query.filter(
        func.strftime('%Y', JournalEntry.date) == str(year)
    ).count()
    ref = f'PJ-{year}-{count + 1:04d}'
    safety = 0
    while JournalEntry.query.filter_by(reference=ref).first() and safety < 9999:
        count += 1
        safety += 1
        ref = f'PJ-{year}-{count + 1:04d}'
    return ref


def get_account_totals(account_id, from_date=None, to_date=None):
    q = db.session.query(
        func.coalesce(func.sum(JournalLine.debit), 0),
        func.coalesce(func.sum(JournalLine.credit), 0)
    ).join(JournalEntry).filter(JournalLine.account_id == account_id)
    if from_date:
        q = q.filter(JournalEntry.date >= from_date)
    if to_date:
        q = q.filter(JournalEntry.date <= to_date)
    row = q.first()
    return dec(row[0]), dec(row[1])


def account_net_balance(account, from_date=None, to_date=None):
    td, tc = get_account_totals(account.id, from_date, to_date)
    if account.computed_normal_balance == 'Debit':
        return td - tc
    return tc - td


def build_trial_balance(from_date=None, to_date=None):
    accounts = Account.query.order_by(Account.code).all()
    rows = []
    total_debit = Decimal('0')
    total_credit = Decimal('0')
    for acct in accounts:
        td, tc = get_account_totals(acct.id, from_date, to_date)
        net = td - tc
        if net == 0:
            continue
        if net > 0:
            debit_col, credit_col = net, Decimal('0')
        else:
            debit_col, credit_col = Decimal('0'), abs(net)
        total_debit += debit_col
        total_credit += credit_col
        rows.append({'account': acct, 'debit': debit_col, 'credit': credit_col})
    return rows, total_debit, total_credit


def build_income_expense(from_date=None, to_date=None):
    income_accounts = Account.query.filter_by(account_type='Income').order_by(Account.code).all()
    expense_accounts = Account.query.filter_by(account_type='Expense').order_by(Account.code).all()

    def rows_total(accounts):
        rows, total = [], Decimal('0')
        for a in accounts:
            bal = account_net_balance(a, from_date, to_date)
            rows.append({'account': a, 'balance': bal})
            total += bal
        return rows, total

    income_rows, total_income = rows_total(income_accounts)
    exp_rows, total_exp = rows_total(expense_accounts)
    surplus = total_income - total_exp
    return {
        'income_rows': income_rows, 'exp_rows': exp_rows,
        'total_income': total_income, 'total_exp': total_exp,
        'surplus': surplus,
    }


def build_balance_sheet():
    asset_accts = Account.query.filter_by(account_type='Asset').order_by(Account.code).all()
    liab_accts = Account.query.filter_by(account_type='Liability').order_by(Account.code).all()
    equity_accts = Account.query.filter_by(account_type='Equity').order_by(Account.code).all()

    def rows_total(accounts):
        rows, total = [], Decimal('0')
        for a in accounts:
            bal = account_net_balance(a)
            rows.append({'account': a, 'balance': bal})
            total += bal
        return rows, total

    asset_rows, total_assets = rows_total(asset_accts)
    liab_rows, total_liab = rows_total(liab_accts)
    equity_rows, total_equity_accounts = rows_total(equity_accts)

    ie = build_income_expense()
    surplus = ie['surplus']
    total_equity = total_equity_accounts + surplus
    total_liab_equity = total_liab + total_equity

    return {
        'asset_rows': asset_rows, 'liab_rows': liab_rows,
        'equity_rows': equity_rows, 'total_assets': total_assets,
        'total_liab': total_liab, 'total_equity_accounts': total_equity_accounts,
        'surplus': surplus, 'total_equity': total_equity,
        'total_liab_equity': total_liab_equity,
        'balanced': abs(total_assets - total_liab_equity) < Decimal('0.01'),
        'net_worth': total_assets - total_liab,
    }


def build_account_ledger(account, from_date=None, to_date=None):
    is_debit_normal = (account.computed_normal_balance == 'Debit')
    opening_balance = Decimal('0')

    if from_date:
        q = db.session.query(
            func.coalesce(func.sum(JournalLine.debit), 0),
            func.coalesce(func.sum(JournalLine.credit), 0)
        ).join(JournalEntry).filter(
            JournalLine.account_id == account.id,
            JournalEntry.date < from_date
        )
        r = q.first()
        raw_td, raw_tc = dec(r[0]), dec(r[1])
        opening_balance = (raw_td - raw_tc) if is_debit_normal else (raw_tc - raw_td)

    running_balance = opening_balance
    q = (db.session.query(JournalLine, JournalEntry)
         .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
         .filter(JournalLine.account_id == account.id))
    if from_date:
        q = q.filter(JournalEntry.date >= from_date)
    if to_date:
        q = q.filter(JournalEntry.date <= to_date)
    q = q.order_by(JournalEntry.date, JournalEntry.id, JournalLine.id)

    ledger_rows = []
    for line, je in q.all():
        d, c = dec(line.debit), dec(line.credit)
        running_balance += (d - c) if is_debit_normal else (c - d)
        ledger_rows.append({
            'date': je.date, 'reference': je.reference, 'narration': je.narration,
            'description': line.description, 'debit': d, 'credit': c,
            'balance': running_balance,
        })

    return ledger_rows, opening_balance, running_balance


def _process_journal_form():
    entry_date_str = request.form.get('date', '').strip()
    narration = request.form.get('narration', '').strip()
    person_id = request.form.get('person_id') or None

    account_ids = request.form.getlist('account_id')
    debits = request.form.getlist('debit')
    credits = request.form.getlist('credit')
    line_descs = request.form.getlist('line_desc')

    errors = []
    if not entry_date_str:
        errors.append('Date is required.')
    if not narration:
        errors.append('Narration is required.')

    entry_date = None
    if entry_date_str:
        try:
            entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append('Invalid date format.')

    lines_data = []
    total_debit = Decimal('0')
    total_credit = Decimal('0')

    for i, aid in enumerate(account_ids):
        if not aid:
            continue
        d = parse_amount(debits[i] if i < len(debits) else '0')
        c = parse_amount(credits[i] if i < len(credits) else '0')
        if d is None or c is None:
            errors.append(f'Line {i+1}: amounts must be positive numbers.')
            continue
        if d > 0 and c > 0:
            errors.append(f'Line {i+1}: debit and credit cannot both have values.')
            continue
        if d == 0 and c == 0:
            errors.append(f'Line {i+1}: both debit and credit are zero.')
            continue
        desc = line_descs[i] if i < len(line_descs) else ''
        lines_data.append({'account_id': int(aid), 'debit': d, 'credit': c, 'desc': desc})
        total_debit += d
        total_credit += c

    if len(lines_data) < 2:
        errors.append('Journal entry must have at least two lines.')
    if lines_data and total_debit != total_credit:
        errors.append(
            f'Entry not balanced. Debit {omr(total_debit)} ≠ Credit {omr(total_credit)}.')

    return errors, entry_date, narration, person_id, lines_data


def _csv_response(filename, headers, rows):
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(headers)
    writer.writerows(rows)
    resp = make_response(si.getvalue())
    resp.headers['Content-Disposition'] = f'attachment; filename={filename}'
    resp.headers['Content-Type'] = 'text/csv'
    return resp


def _parse_date_range(from_str, to_str):
    from_date = to_date = None
    try:
        if from_str:
            from_date = datetime.strptime(from_str, '%Y-%m-%d').date()
        if to_str:
            to_date = datetime.strptime(to_str, '%Y-%m-%d').date()
    except ValueError:
        pass
    return from_date, to_date


# ─────────────────────────── DEFAULT ACCOUNTS ───────────────────────────

_DEFAULT_ACCOUNTS = [
    # (code, name, type, description)
    # ASSETS
    ('1000', 'Cash',                        'Asset', 'Cash on hand (parent)'),
    ('1010', 'Wallet Cash',                 'Asset', 'Cash carried in wallet'),
    ('1020', 'Bank Account 1',              'Asset', 'Primary bank account'),
    ('1030', 'Bank Account 2',              'Asset', 'Secondary bank account'),
    ('1040', 'Savings Account',             'Asset', 'Savings or deposit account'),
    ('1100', 'Accounts Receivable',         'Asset', 'Money owed to you by others'),
    ('1110', 'Loans to Others',             'Asset', 'Money lent to friends or family expected to be returned'),
    ('1200', 'Personal Assets',             'Asset', 'Personal property and belongings (parent)'),
    ('1210', 'Computer / Electronics',      'Asset', 'Computers, phones, and electronic devices'),
    ('1220', 'Car / Vehicle',               'Asset', 'Car or other vehicle value'),
    ('1230', 'Furniture and Equipment',     'Asset', 'Furniture and household equipment'),
    # LIABILITIES
    ('2000', 'Credit Card',                 'Liability', 'Credit card balances (parent)'),
    ('2010', 'Credit Card 1',               'Liability', 'Primary credit card'),
    ('2020', 'Credit Card 2',               'Liability', 'Secondary credit card'),
    ('2100', 'Personal Loan',               'Liability', 'Personal loans (parent)'),
    ('2110', 'Loan from Family',            'Liability', 'Money borrowed from family members'),
    ('2120', 'Loan from Friend',            'Liability', 'Money borrowed from friends'),
    ('2200', 'Accounts Payable',            'Liability', 'Money you owe to others'),
    ('2300', 'Other Liabilities',           'Liability', 'Other debts and obligations'),
    # EQUITY
    ('3000', 'Opening Balance / Personal Capital', 'Equity', 'Starting personal capital and net worth'),
    ('3100', 'Current Year Surplus or Deficit',    'Equity', 'Accumulated surplus or deficit for the current year'),
    ('3200', 'Personal Net Worth',                 'Equity', 'Total personal net worth'),
    ('3300', 'Owner Drawings / Personal Withdrawals', 'Equity', 'Personal withdrawals from savings'),
    # INCOME
    ('4000', 'Salary Income',               'Income', 'Monthly salary from employer'),
    ('4010', 'Business / Freelance Income', 'Income', 'Self-employment or freelance income'),
    ('4020', 'Rental Income',               'Income', 'Income from renting property'),
    ('4030', 'Family Support Received',     'Income', 'Financial support received from family'),
    ('4040', 'Other Income',                'Income', 'Miscellaneous income not classified elsewhere'),
    # EXPENSES
    ('5000', 'Food and Groceries',          'Expense', 'Supermarket, restaurants, food delivery'),
    ('5010', 'Rent / Housing',              'Expense', 'Monthly rent or housing cost'),
    ('5020', 'Electricity and Water',       'Expense', 'Utility bills'),
    ('5030', 'Internet',                    'Expense', 'Home internet service'),
    ('5040', 'Mobile / Telephone',          'Expense', 'Mobile phone bills'),
    ('5050', 'Fuel',                        'Expense', 'Petrol or diesel for vehicle'),
    ('5060', 'Car Maintenance',             'Expense', 'Car servicing, tyres, repairs'),
    ('5070', 'Insurance',                   'Expense', 'Health, car, or life insurance'),
    ('5080', 'Medical',                     'Expense', 'Medical and pharmacy expenses'),
    ('5090', 'Education',                   'Expense', 'School fees, courses, books'),
    ('5100', 'Children Expense',            'Expense', 'Children clothing, activities, supplies'),
    ('5110', 'Housemaid / Domestic Help',   'Expense', 'Salary for housemaid or domestic workers'),
    ('5120', 'Travel',                      'Expense', 'Travel, flights, accommodation'),
    ('5130', 'Charity / Donations',         'Expense', 'Charitable giving and donations'),
    ('5140', 'Subscriptions',               'Expense', 'Streaming, software, and other subscriptions'),
    ('5150', 'Clothing',                    'Expense', 'Clothing and apparel'),
    ('5160', 'Personal Shopping',           'Expense', 'Mall, online shopping, non-essential purchases'),
    ('5170', 'Bank Charges',                'Expense', 'Bank fees and service charges'),
    ('5180', 'Loan Interest Expense',       'Expense', 'Interest paid on loans or credit cards'),
    ('5190', 'Other Expense',               'Expense', 'Miscellaneous expenses not categorised elsewhere'),
]


def seed_default_accounts():
    """Seed the default generic chart of accounts. Called only when Account table is empty."""
    imported = 0
    for code, name, atype, desc in _DEFAULT_ACCOUNTS:
        if Account.query.filter_by(code=code).first():
            continue
        db.session.add(Account(code=code, name=name, account_type=atype,
                               description=desc, is_active=True))
        imported += 1
    db.session.commit()
    print(f'[template] {imported} default accounts seeded.')
    return imported


def reset_to_defaults():
    """Delete all user data and restore the default account list. Used by /admin/reset-data."""
    JournalLine.query.delete()
    JournalEntry.query.delete()
    Person.query.delete()
    BankReconciliation.query.delete()
    Account.query.delete()
    db.session.commit()
    count = seed_default_accounts()
    print(f'[reset] Data cleared. {count} default accounts restored.')
    return count


# ─────────────────────────── DASHBOARD ───────────────────────────

@app.route('/')
@login_required
def dashboard():
    def sum_type(atype):
        return sum(account_net_balance(a)
                   for a in Account.query.filter_by(account_type=atype).all())

    total_assets = sum_type('Asset')
    total_liab = sum_type('Liability')
    total_equity = sum_type('Equity')
    total_income = sum_type('Income')
    total_exp = sum_type('Expense')
    surplus = total_income - total_exp
    net_worth = total_assets - total_liab

    total_dr = db.session.query(func.coalesce(func.sum(JournalLine.debit), 0)).scalar()
    total_cr = db.session.query(func.coalesce(func.sum(JournalLine.credit), 0)).scalar()
    tb_balanced = abs(dec(total_dr) - dec(total_cr)) < Decimal('0.01')

    bank_cash = []
    for a in Account.query.filter_by(account_type='Asset', is_active=True).order_by(Account.code).all():
        if a.is_bank_or_cash:
            bank_cash.append({'account': a, 'balance': account_net_balance(a)})

    credit_cards = []
    for a in Account.query.filter_by(account_type='Liability', is_active=True).order_by(Account.code).all():
        if any(k in a.name.lower() for k in ('credit card', 'visa', 'mastercard', 'credit')):
            credit_cards.append({'account': a, 'balance': account_net_balance(a)})

    recent = JournalEntry.query.order_by(
        JournalEntry.date.desc(), JournalEntry.id.desc()
    ).limit(10).all()

    entry_count = JournalEntry.query.count()
    account_count = Account.query.count()

    return render_template('dashboard.html',
                           total_assets=total_assets, total_liab=total_liab,
                           total_equity=total_equity, total_income=total_income,
                           total_exp=total_exp, surplus=surplus, net_worth=net_worth,
                           tb_balanced=tb_balanced, bank_cash=bank_cash,
                           credit_cards=credit_cards, recent=recent,
                           entry_count=entry_count, account_count=account_count)


# ─────────────────────────── ACCOUNTS ───────────────────────────

@app.route('/accounts')
@login_required
def accounts():
    q = Account.query
    filter_type = request.args.get('type', '')
    search = request.args.get('search', '').strip()
    if filter_type:
        q = q.filter_by(account_type=filter_type)
    if search:
        q = q.filter((Account.code.ilike(f'%{search}%')) | (Account.name.ilike(f'%{search}%')))
    accts = q.order_by(Account.code).all()
    return render_template('accounts.html', accounts=accts,
                           account_types=ACCOUNT_TYPES, filter_type=filter_type, search=search)


@app.route('/accounts/new', methods=['GET', 'POST'])
@login_required
def account_new():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        name = request.form.get('name', '').strip()
        atype = request.form.get('account_type', '').strip()
        desc = request.form.get('description', '').strip() or None
        is_active = request.form.get('is_active') == '1'
        parent_id = request.form.get('parent_account_id') or None

        errors = []
        if not code:
            errors.append('Account code is required.')
        if not name:
            errors.append('Account name is required.')
        if atype not in ACCOUNT_TYPES:
            errors.append('Valid account type is required.')
        if code and Account.query.filter_by(code=code).first():
            errors.append(f'Code {code} already exists.')
        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('account_form.html', account=None,
                                   account_types=ACCOUNT_TYPES,
                                   all_accounts=Account.query.order_by(Account.code).all())

        db.session.add(Account(code=code, name=name, account_type=atype,
                               description=desc, is_active=is_active,
                               parent_account_id=int(parent_id) if parent_id else None))
        db.session.commit()
        flash(f'Account {code} — {name} created.', 'success')
        return redirect(url_for('accounts'))

    return render_template('account_form.html', account=None,
                           account_types=ACCOUNT_TYPES,
                           all_accounts=Account.query.order_by(Account.code).all())


@app.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
@login_required
def account_edit(account_id):
    acct = Account.query.get_or_404(account_id)
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        name = request.form.get('name', '').strip()
        atype = request.form.get('account_type', '').strip()
        desc = request.form.get('description', '').strip() or None
        is_active = request.form.get('is_active') == '1'
        parent_id = request.form.get('parent_account_id') or None

        errors = []
        if not code:
            errors.append('Account code is required.')
        if not name:
            errors.append('Account name is required.')
        existing = Account.query.filter_by(code=code).first()
        if existing and existing.id != account_id:
            errors.append(f'Code {code} is used by another account.')
        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('account_form.html', account=acct,
                                   account_types=ACCOUNT_TYPES,
                                   all_accounts=Account.query.order_by(Account.code).all())

        acct.code = code
        acct.name = name
        acct.account_type = atype
        acct.description = desc
        acct.is_active = is_active
        acct.parent_account_id = int(parent_id) if parent_id else None
        db.session.commit()
        flash('Account updated.', 'success')
        return redirect(url_for('accounts'))

    return render_template('account_form.html', account=acct,
                           account_types=ACCOUNT_TYPES,
                           all_accounts=Account.query.filter(
                               Account.id != account_id).order_by(Account.code).all())


@app.route('/accounts/<int:account_id>/inactive', methods=['POST'])
@login_required
def account_toggle(account_id):
    acct = Account.query.get_or_404(account_id)
    acct.is_active = not acct.is_active
    db.session.commit()
    flash(f'Account {acct.code} {"activated" if acct.is_active else "deactivated"}.', 'info')
    return redirect(url_for('accounts'))


# ─────────────────────────── JOURNAL ENTRIES ───────────────────────────

@app.route('/journal-entries')
@login_required
def journal_entries():
    search = request.args.get('search', '').strip()
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    page = request.args.get('page', 1, type=int)

    q = JournalEntry.query
    if search:
        q = q.filter((JournalEntry.reference.ilike(f'%{search}%')) |
                     (JournalEntry.narration.ilike(f'%{search}%')))
    if from_date:
        try:
            q = q.filter(JournalEntry.date >= datetime.strptime(from_date, '%Y-%m-%d').date())
        except ValueError:
            pass
    if to_date:
        try:
            q = q.filter(JournalEntry.date <= datetime.strptime(to_date, '%Y-%m-%d').date())
        except ValueError:
            pass

    entries = q.order_by(JournalEntry.date.desc(), JournalEntry.id.desc())\
                .paginate(page=page, per_page=25, error_out=False)
    return render_template('journal_entries.html', entries=entries,
                           search=search, from_date=from_date, to_date=to_date)


@app.route('/journal-entries/<int:entry_id>')
@login_required
def journal_entry_detail(entry_id):
    je = JournalEntry.query.get_or_404(entry_id)
    return render_template('journal_entry_detail.html', entry=je)


@app.route('/journal-entries/new', methods=['GET', 'POST'])
@login_required
def journal_entry_new():
    active_accounts = Account.query.filter_by(is_active=True).order_by(Account.code).all()
    people = Person.query.filter_by(is_active=True).order_by(Person.name).all()

    if request.method == 'POST':
        errors, entry_date, narration, person_id, lines_data = _process_journal_form()
        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('journal_entry_form.html', entry=None,
                                   accounts=active_accounts, people=people,
                                   today=date.today().isoformat())

        ref = generate_reference(entry_date)
        je = JournalEntry(date=entry_date, reference=ref,
                          narration=narration, person_id=person_id)
        db.session.add(je)
        db.session.flush()
        for ld in lines_data:
            db.session.add(JournalLine(
                journal_entry_id=je.id, account_id=ld['account_id'],
                debit=ld['debit'], credit=ld['credit'], description=ld['desc']))
        db.session.commit()
        flash(f'Journal entry {ref} created.', 'success')
        return redirect(url_for('journal_entry_detail', entry_id=je.id))

    return render_template('journal_entry_form.html', entry=None,
                           accounts=active_accounts, people=people,
                           today=date.today().isoformat(),
                           default_ref=generate_reference())


@app.route('/journal-entries/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def journal_entry_edit(entry_id):
    je = JournalEntry.query.get_or_404(entry_id)
    active_accounts = Account.query.filter_by(is_active=True).order_by(Account.code).all()
    people = Person.query.filter_by(is_active=True).order_by(Person.name).all()

    if request.method == 'POST':
        errors, entry_date, narration, person_id, lines_data = _process_journal_form()
        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('journal_entry_form.html', entry=je,
                                   accounts=active_accounts, people=people,
                                   today=date.today().isoformat())

        je.date = entry_date
        je.narration = narration
        je.person_id = person_id
        for line in list(je.lines):
            db.session.delete(line)
        db.session.flush()
        for ld in lines_data:
            db.session.add(JournalLine(
                journal_entry_id=je.id, account_id=ld['account_id'],
                debit=ld['debit'], credit=ld['credit'], description=ld['desc']))
        db.session.commit()
        flash(f'Journal entry {je.reference} updated.', 'success')
        return redirect(url_for('journal_entry_detail', entry_id=je.id))

    return render_template('journal_entry_form.html', entry=je,
                           accounts=active_accounts, people=people,
                           today=date.today().isoformat())


@app.route('/journal-entries/<int:entry_id>/delete', methods=['POST'])
@login_required
def journal_entry_delete(entry_id):
    je = JournalEntry.query.get_or_404(entry_id)
    ref = je.reference
    db.session.delete(je)
    db.session.commit()
    flash(f'Journal entry {ref} deleted.', 'warning')
    return redirect(url_for('journal_entries'))


# ─────────────────────────── OPENING BALANCES ───────────────────────────

@app.route('/opening-balances', methods=['GET', 'POST'])
@login_required
def opening_balances():
    accounts = Account.query.filter_by(is_active=True).order_by(Account.code).all()
    ob_account = next((a for a in Account.query.all()
                       if 'opening balance' in a.name.lower() or 'personal capital' in a.name.lower()), None)

    if request.method == 'POST':
        account_ids = request.form.getlist('account_id')
        amounts = request.form.getlist('amount')
        sides = request.form.getlist('side')
        ob_date_str = request.form.get('ob_date', date.today().isoformat())

        try:
            ob_date = datetime.strptime(ob_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date.', 'danger')
            return render_template('opening_balances.html', accounts=accounts,
                                   ob_account=ob_account, today=date.today().isoformat())

        lines_data = []
        total_debit = Decimal('0')
        total_credit = Decimal('0')

        for i, aid in enumerate(account_ids):
            if not aid:
                continue
            amt = parse_amount(amounts[i] if i < len(amounts) else '0')
            if amt is None or amt == 0:
                continue
            side = sides[i] if i < len(sides) else 'debit'
            d = amt if side == 'debit' else Decimal('0')
            c = amt if side == 'credit' else Decimal('0')
            lines_data.append({'account_id': int(aid), 'debit': d, 'credit': c,
                                'desc': 'Opening Balance'})
            total_debit += d
            total_credit += c

        if not lines_data:
            flash('No opening balance amounts entered.', 'danger')
            return render_template('opening_balances.html', accounts=accounts,
                                   ob_account=ob_account, today=date.today().isoformat())

        diff = total_debit - total_credit
        if diff != 0 and ob_account:
            if diff > 0:
                lines_data.append({'account_id': ob_account.id, 'debit': Decimal('0'),
                                   'credit': diff, 'desc': 'Opening balance offset'})
                total_credit += diff
            else:
                lines_data.append({'account_id': ob_account.id, 'debit': abs(diff),
                                   'credit': Decimal('0'), 'desc': 'Opening balance offset'})
                total_debit += abs(diff)

        if abs(total_debit - total_credit) > Decimal('0.001'):
            flash(f'Entry is not balanced (Debit {omr(total_debit)} ≠ Credit {omr(total_credit)}) '
                  f'and no Opening Balance account was found to auto-balance.', 'danger')
            return render_template('opening_balances.html', accounts=accounts,
                                   ob_account=ob_account, today=date.today().isoformat())

        year = ob_date.year
        count = JournalEntry.query.filter(
            JournalEntry.reference.like(f'OB-{year}-%')
        ).count()
        ref = f'OB-{year}-{count + 1:04d}'
        while JournalEntry.query.filter_by(reference=ref).first():
            count += 1
            ref = f'OB-{year}-{count + 1:04d}'

        je = JournalEntry(date=ob_date, reference=ref, narration='Opening Balances')
        db.session.add(je)
        db.session.flush()
        for ld in lines_data:
            db.session.add(JournalLine(
                journal_entry_id=je.id, account_id=ld['account_id'],
                debit=ld['debit'], credit=ld['credit'], description=ld['desc']))
        db.session.commit()
        flash(f'Opening balances recorded as {ref}.', 'success')
        return redirect(url_for('journal_entry_detail', entry_id=je.id))

    return render_template('opening_balances.html', accounts=accounts,
                           ob_account=ob_account, today=date.today().isoformat())


# ─────────────────────────── PEOPLE ───────────────────────────

@app.route('/people')
@login_required
def people():
    search = request.args.get('search', '').strip()
    show_inactive = request.args.get('show_inactive') == '1'
    q = Person.query
    if not show_inactive:
        q = q.filter_by(is_active=True)
    if search:
        q = q.filter((Person.name.ilike(f'%{search}%')) |
                     (Person.relationship_or_category.ilike(f'%{search}%')))
    person_list = q.order_by(Person.name).all()
    return render_template('people.html', people=person_list, search=search,
                           show_inactive=show_inactive)


@app.route('/people/new', methods=['GET', 'POST'])
@login_required
def person_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Name is required.', 'danger')
            return render_template('person_form.html', person=None)
        db.session.add(Person(
            name=name,
            relationship_or_category=request.form.get('relationship_or_category', '').strip() or None,
            phone=request.form.get('phone', '').strip() or None,
            email=request.form.get('email', '').strip() or None,
            notes=request.form.get('notes', '').strip() or None,
            is_active=True,
        ))
        db.session.commit()
        flash(f'{name} added.', 'success')
        return redirect(url_for('people'))
    return render_template('person_form.html', person=None)


@app.route('/people/<int:person_id>/edit', methods=['GET', 'POST'])
@login_required
def person_edit(person_id):
    p = Person.query.get_or_404(person_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Name is required.', 'danger')
            return render_template('person_form.html', person=p)
        p.name = name
        p.relationship_or_category = request.form.get('relationship_or_category', '').strip() or None
        p.phone = request.form.get('phone', '').strip() or None
        p.email = request.form.get('email', '').strip() or None
        p.notes = request.form.get('notes', '').strip() or None
        p.is_active = request.form.get('is_active') == '1'
        db.session.commit()
        flash('Person updated.', 'success')
        return redirect(url_for('people'))
    return render_template('person_form.html', person=p)


@app.route('/people/<int:person_id>/toggle', methods=['POST'])
@login_required
def person_toggle(person_id):
    p = Person.query.get_or_404(person_id)
    p.is_active = not p.is_active
    db.session.commit()
    flash(f'{p.name} {"activated" if p.is_active else "deactivated"}.', 'info')
    return redirect(url_for('people'))


# ─────────────────────────── BANK RECONCILIATION ───────────────────────────

@app.route('/bank-reconciliation')
@login_required
def bank_reconciliation():
    recs = BankReconciliation.query.order_by(BankReconciliation.statement_date.desc()).all()
    return render_template('bank_reconciliation.html', reconciliations=recs)


@app.route('/bank-reconciliation/new', methods=['GET', 'POST'])
@login_required
def reconciliation_new():
    bank_accounts = Account.query.filter_by(is_active=True).order_by(Account.code).all()
    if request.method == 'POST':
        account_id = request.form.get('account_id', type=int)
        stmt_date_str = request.form.get('statement_date', '').strip()
        book_bal = parse_amount(request.form.get('book_balance', '0')) or Decimal('0')
        stmt_bal = parse_amount(request.form.get('statement_balance', '0')) or Decimal('0')
        notes = request.form.get('notes', '').strip() or None

        errors = []
        if not account_id:
            errors.append('Account is required.')
        stmt_date = None
        if not stmt_date_str:
            errors.append('Statement date is required.')
        else:
            try:
                stmt_date = datetime.strptime(stmt_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid date.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('reconciliation_form.html', rec=None,
                                   bank_accounts=bank_accounts, today=date.today().isoformat())

        db.session.add(BankReconciliation(
            account_id=account_id, statement_date=stmt_date,
            book_balance=book_bal, statement_balance=stmt_bal,
            difference=book_bal - stmt_bal, notes=notes))
        db.session.commit()
        flash('Reconciliation saved.', 'success')
        return redirect(url_for('bank_reconciliation'))

    return render_template('reconciliation_form.html', rec=None,
                           bank_accounts=bank_accounts, today=date.today().isoformat())


@app.route('/bank-reconciliation/<int:rec_id>/edit', methods=['GET', 'POST'])
@login_required
def reconciliation_edit(rec_id):
    rec = BankReconciliation.query.get_or_404(rec_id)
    bank_accounts = Account.query.filter_by(is_active=True).order_by(Account.code).all()
    if request.method == 'POST':
        account_id = request.form.get('account_id', type=int)
        stmt_date_str = request.form.get('statement_date', '').strip()
        book_bal = parse_amount(request.form.get('book_balance', '0')) or Decimal('0')
        stmt_bal = parse_amount(request.form.get('statement_balance', '0')) or Decimal('0')
        notes = request.form.get('notes', '').strip() or None
        try:
            stmt_date = datetime.strptime(stmt_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date.', 'danger')
            return render_template('reconciliation_form.html', rec=rec,
                                   bank_accounts=bank_accounts, today=date.today().isoformat())
        rec.account_id = account_id
        rec.statement_date = stmt_date
        rec.book_balance = book_bal
        rec.statement_balance = stmt_bal
        rec.difference = book_bal - stmt_bal
        rec.notes = notes
        db.session.commit()
        flash('Reconciliation updated.', 'success')
        return redirect(url_for('bank_reconciliation'))
    return render_template('reconciliation_form.html', rec=rec,
                           bank_accounts=bank_accounts, today=date.today().isoformat())


# ─────────────────────────── REPORTS ───────────────────────────

@app.route('/reports/trial-balance')
@login_required
def trial_balance():
    from_date_str = request.args.get('from_date', '')
    to_date_str = request.args.get('to_date', '')
    from_date, to_date = _parse_date_range(from_date_str, to_date_str)
    rows, total_debit, total_credit = build_trial_balance(from_date, to_date)
    diff = total_debit - total_credit
    return render_template('trial_balance.html', rows=rows,
                           total_debit=total_debit, total_credit=total_credit,
                           difference=diff, balanced=abs(diff) < Decimal('0.01'),
                           from_date=from_date_str, to_date=to_date_str)


@app.route('/reports/general-ledger')
@login_required
def general_ledger():
    account_id = request.args.get('account_id', type=int)
    from_date_str = request.args.get('from_date', '')
    to_date_str = request.args.get('to_date', '')
    from_date, to_date = _parse_date_range(from_date_str, to_date_str)
    all_accounts = Account.query.order_by(Account.code).all()

    selected_account = None
    ledger_rows = []
    opening_balance = Decimal('0')
    closing_balance = Decimal('0')

    if account_id:
        selected_account = Account.query.get(account_id)
        if selected_account:
            ledger_rows, opening_balance, closing_balance = \
                build_account_ledger(selected_account, from_date, to_date)

    return render_template('general_ledger.html', all_accounts=all_accounts,
                           selected_account=selected_account, account_id=account_id,
                           ledger_rows=ledger_rows, opening_balance=opening_balance,
                           closing_balance=closing_balance,
                           from_date=from_date_str, to_date=to_date_str)


@app.route('/reports/income-expense')
@app.route('/reports/profit-loss')
@login_required
def income_expense():
    from_date_str = request.args.get('from_date', '')
    to_date_str = request.args.get('to_date', '')
    from_date, to_date = _parse_date_range(from_date_str, to_date_str)
    data = build_income_expense(from_date, to_date)
    return render_template('income_expense.html', **data,
                           from_date=from_date_str, to_date=to_date_str)


@app.route('/reports/balance-sheet')
@login_required
def balance_sheet():
    data = build_balance_sheet()
    return render_template('balance_sheet.html', **data)


@app.route('/reports/account-statement')
@login_required
def account_statement():
    return redirect(url_for('general_ledger', **request.args))


@app.route('/reports/transactions-by-date')
@login_required
def transactions_by_date():
    from_date_str = request.args.get('from_date', '')
    to_date_str = request.args.get('to_date', '')
    from_date, to_date = _parse_date_range(from_date_str, to_date_str)
    q = JournalEntry.query
    if from_date:
        q = q.filter(JournalEntry.date >= from_date)
    if to_date:
        q = q.filter(JournalEntry.date <= to_date)
    entries = q.order_by(JournalEntry.date, JournalEntry.id).all()
    return render_template('transactions_by_date.html', entries=entries,
                           from_date=from_date_str, to_date=to_date_str)


@app.route('/reports/expenses-by-category')
@login_required
def expenses_by_category():
    from_date_str = request.args.get('from_date', '')
    to_date_str = request.args.get('to_date', '')
    from_date, to_date = _parse_date_range(from_date_str, to_date_str)
    expense_accts = Account.query.filter_by(account_type='Expense').order_by(Account.code).all()
    rows = []
    grand_total = Decimal('0')
    for a in expense_accts:
        bal = account_net_balance(a, from_date, to_date)
        if bal != 0:
            rows.append({'account': a, 'balance': bal})
            grand_total += bal
    return render_template('expenses_by_category.html', rows=rows,
                           grand_total=grand_total,
                           from_date=from_date_str, to_date=to_date_str)


# ─────────────────────────── IMPORT / EXPORT ───────────────────────────

@app.route('/import-export')
@login_required
def import_export():
    return render_template('import_export.html')


@app.route('/export/accounts')
@login_required
def export_accounts():
    accts = Account.query.order_by(Account.code).all()
    rows = [[a.code, a.name, a.account_type, a.description or '',
             'Active' if a.is_active else 'Inactive'] for a in accts]
    return _csv_response('accounts.csv',
                         ['Code', 'Name', 'Type', 'Description', 'Status'], rows)


@app.route('/export/journal-entries')
@login_required
def export_journal_entries():
    entries = JournalEntry.query.order_by(JournalEntry.date, JournalEntry.id).all()
    rows = []
    for je in entries:
        for line in je.lines:
            rows.append([je.date.isoformat(), je.reference, je.narration,
                         line.account.code, line.account.name,
                         f'{float(line.debit):.3f}', f'{float(line.credit):.3f}',
                         line.description or ''])
    return _csv_response('journal_entries.csv',
                         ['Date', 'Reference', 'Narration', 'Code', 'Account',
                          'Debit', 'Credit', 'Line Description'], rows)


@app.route('/export/trial-balance')
@login_required
def export_trial_balance():
    rows_data, td, tc = build_trial_balance()
    rows = [[r['account'].code, r['account'].name,
             f'{float(r["debit"]):.3f}', f'{float(r["credit"]):.3f}']
            for r in rows_data]
    rows.append(['', 'TOTAL', f'{float(td):.3f}', f'{float(tc):.3f}'])
    return _csv_response('trial_balance.csv', ['Code', 'Account', 'Debit', 'Credit'], rows)


@app.route('/export/income-expense')
@login_required
def export_income_expense():
    data = build_income_expense()
    rows = [['INCOME', '', '']]
    for r in data['income_rows']:
        rows.append([r['account'].code, r['account'].name, f'{float(r["balance"]):.3f}'])
    rows.append(['', 'Total Income', f'{float(data["total_income"]):.3f}'])
    rows.append(['EXPENSES', '', ''])
    for r in data['exp_rows']:
        rows.append([r['account'].code, r['account'].name, f'{float(r["balance"]):.3f}'])
    rows.append(['', 'Total Expenses', f'{float(data["total_exp"]):.3f}'])
    rows.append(['', 'SURPLUS / DEFICIT', f'{float(data["surplus"]):.3f}'])
    return _csv_response('income_expense.csv', ['Code', 'Account', 'Amount OMR'], rows)


@app.route('/export/balance-sheet')
@login_required
def export_balance_sheet():
    data = build_balance_sheet()
    rows = [['ASSETS', '', '']]
    for r in data['asset_rows']:
        rows.append([r['account'].code, r['account'].name, f'{float(r["balance"]):.3f}'])
    rows.append(['', 'Total Assets', f'{float(data["total_assets"]):.3f}'])
    rows.append(['LIABILITIES', '', ''])
    for r in data['liab_rows']:
        rows.append([r['account'].code, r['account'].name, f'{float(r["balance"]):.3f}'])
    rows.append(['', 'Total Liabilities', f'{float(data["total_liab"]):.3f}'])
    rows.append(['EQUITY', '', ''])
    for r in data['equity_rows']:
        rows.append([r['account'].code, r['account'].name, f'{float(r["balance"]):.3f}'])
    rows.append(['', 'Current Year Surplus/Deficit', f'{float(data["surplus"]):.3f}'])
    rows.append(['', 'Total Equity', f'{float(data["total_equity"]):.3f}'])
    rows.append(['', 'Net Worth', f'{float(data["net_worth"]):.3f}'])
    return _csv_response('balance_sheet.csv', ['Code', 'Account', 'Amount OMR'], rows)


# ─────────────────────────── ADMIN — RESET ───────────────────────────

@app.route('/admin/reset-data', methods=['GET', 'POST'])
@login_required
def admin_reset():
    stats = {
        'accounts': Account.query.count(),
        'entries': JournalEntry.query.count(),
        'people': Person.query.count(),
        'reconciliations': BankReconciliation.query.count(),
    }

    if request.method == 'POST':
        confirmation = request.form.get('confirmation', '').strip()
        if confirmation != 'RESET':
            flash('Incorrect confirmation text. Type exactly: RESET', 'danger')
            return render_template('admin_reset.html', stats=stats)

        count = reset_to_defaults()
        flash(f'All data has been cleared. {count} default accounts restored. '
              f'The system is now empty and ready for new data.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('admin_reset.html', stats=stats)


# ─────────────────────────── MANUAL ───────────────────────────

@app.route('/manual')
@login_required
def manual():
    return render_template('manual.html')


# ─────────────────────────── LOGIN / LOGOUT ───────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if username == LOGIN_USERNAME and password == LOGIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            next_url = request.args.get('next') or url_for('dashboard')
            return redirect(next_url)
        error = 'Incorrect username or password.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ─────────────────────────── STARTUP ───────────────────────────

def init_db():
    with app.app_context():
        db.create_all()
        if Account.query.count() == 0:
            print('[template] First run — seeding default chart of accounts...')
            seed_default_accounts()
            print('[template] Database is empty and ready. No balances or transactions.')
        else:
            print(f'[template] {Account.query.count()} accounts ready. '
                  f'{JournalEntry.query.count()} journal entries.')


init_db()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4444, debug=False, use_reloader=False)
