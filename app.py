from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///membership.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    employees = db.relationship('Employee', backref='institution', lazy=True)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    join_date = db.Column(db.Date, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    loans = db.relationship('Loan', backref='employee', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    payment_date = db.Column(db.Date, default=datetime.utcnow)
    payment_type = db.Column(db.String(50))  # Membership, Loan, Other
    amount = db.Column(db.Float, default=0)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    category = db.Column(db.String(120))
    amount = db.Column(db.Float, default=0)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.Date, default=datetime.utcnow)

class LoanPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'), nullable=False)
    payment_date = db.Column(db.Date, default=datetime.utcnow)
    amount = db.Column(db.Float, default=0)

@app.route('/')
def index():
    institutions = Institution.query.all()
    return render_template('index.html', institutions=institutions)

@app.route('/institution/<int:inst_id>')
def institution_detail(inst_id):
    institution = Institution.query.get_or_404(inst_id)
    employees = Employee.query.filter_by(institution_id=inst_id).all()
    payments = Payment.query.filter_by(institution_id=inst_id).all()
    return render_template('institution.html', institution=institution, employees=employees, payments=payments)

@app.route('/employee/<int:emp_id>')
def employee_detail(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    payments = Payment.query.filter_by(employee_id=emp_id).all()
    loans = Loan.query.filter_by(employee_id=emp_id).all()
    return render_template('employee.html', employee=employee, payments=payments, loans=loans)

@app.route('/add_institution', methods=['GET', 'POST'])
def add_institution():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        inst = Institution(name=name, email=email, address=address)
        db.session.add(inst)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_institution.html')

@app.route('/add_employee/<int:inst_id>', methods=['GET', 'POST'])
def add_employee(inst_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        emp = Employee(name=name, email=email, institution_id=inst_id)
        db.session.add(emp)
        db.session.commit()
        return redirect(url_for('institution_detail', inst_id=inst_id))
    return render_template('add_employee.html', inst_id=inst_id)

@app.route('/add_payment/<int:inst_id>/<int:emp_id>', methods=['GET', 'POST'])
def add_payment(inst_id, emp_id):
    if request.method == 'POST':
        ptype = request.form['payment_type']
        amount = float(request.form['amount'])
        pay = Payment(institution_id=inst_id, employee_id=emp_id, payment_type=ptype, amount=amount)
        db.session.add(pay)
        db.session.commit()
        return redirect(url_for('employee_detail', emp_id=emp_id))
    return render_template('add_payment.html', inst_id=inst_id, emp_id=emp_id)

@app.route('/apply_loan/<int:emp_id>', methods=['GET', 'POST'])
def apply_loan(emp_id):
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        loan = Loan(employee_id=emp_id, category=category, amount=amount)
        db.session.add(loan)
        db.session.commit()
        return redirect(url_for('employee_detail', emp_id=emp_id))
    return render_template('apply_loan.html', emp_id=emp_id)

@app.route('/approve_loan/<int:loan_id>')
def approve_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    loan.approved = True
    db.session.commit()
    return redirect(url_for('employee_detail', emp_id=loan.employee_id))

@app.cli.command('init-db')
def init_db():
    db.create_all()
    print('Database initialized')

if __name__ == '__main__':
    app.run(debug=True)
