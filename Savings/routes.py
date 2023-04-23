from flask import render_template, url_for, flash, redirect,request,send_file
from Savings import app,db,bcrypt
from Savings.forms import RegistrationForm, LoginForm , TransactionForm,AdminForm,AccountForm,DateForm
from Savings.models import User,Account,Request
from flask_login import login_user,current_user,logout_user,login_required
import random,string,os
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Image,Paragraph
from flask import Response,current_app
from datetime import datetime
from flask import make_response
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from reportlab.lib import styles
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from flask import request,session




@app.route("/")
@app.route("/home")
def home():
	return render_template('home.html')


def generate_random_numbers(length):
    """
    Generate a random string of numbers with the given length.
    """
    # Define the characters to choose from (0-9)
    characters = string.digits

    # Generate a random string by choosing characters randomly with replacement
    random_string = ''.join(random.choice(characters) for _ in range(length))

    return random_string



@app.route("/register",methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
    	hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    	user = User(username=form.username.data,email=form.email.data,password=hashed_password)
    	db.session.add(user)
    	db.session.commit()
    	flash(f'Account created for {form.username.data}!', 'success')
    	random_numbers = generate_random_numbers(15)
    	hashed_username = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    	account = Account(user_id = user.id,account_number=random_numbers,balance = 0)
    	db.session.add(account)
    	db.session.commit()
    	return redirect(url_for('login'))

    if current_user.is_authenticated:
    	return redirect(url_for('userDashboard'))
        
    return render_template('register.html', title='Register', form=form)

@app.route("/login",methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password,form.password.data):
			login_user(user,remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('userDashboard'))
		else:
			flash("Login Unsuccssful","danger")
	if current_user.is_authenticated:
		return redirect(url_for("userDashboard"))
	return render_template('login.html',title="Login",form=form)

@login_required
@app.route("/user-dashboard",methods=['GET','POST'])
def userDashboard():
	form = DateForm()
	user = User.query.filter_by(username=current_user.username).first()
	account = Account.query.filter_by(user_id=current_user.id).first()
	requests = Request.query.filter_by(user_id=current_user.id).all()
	# account = Account.query.filter_by(user_id = current_user.id)

	if form.validate_on_submit():
		session['start_date'] = form.from_date.data
		session['end_date'] = form.to_date.data 
		return redirect(url_for('generatepdf'))

		
	return render_template('dashboard/user.html',account=account,user=user,requests = requests,form=form)

@app.route("/logout")
def logout():
	logout_user()
	return render_template('home.html')


@app.route("/account")
@login_required
def account():
	return render_template('account.html',title="Account")


@app.route('/requests', methods=['GET', 'POST'])
def requests():
	form = TransactionForm()
	account = Account.query.filter_by(user_id=current_user.id).first()
	account_number = account.account_number
	if form.validate_on_submit():
		if account_number == form.account_number.data:
			transaction = Request(account_number = account_number,user_id=current_user.id,request_type = form.transaction_type.data,amount = form.amount.data)
			db.session.add(transaction)
			db.session.commit()
			return redirect(url_for("userDashboard"))
		else:
			flash("Enter Valid Account Number","danger")

	return render_template('requests.html',form = form)

@app.route("/admin", methods=['GET', 'POST'])
def adminLogin():
	form = AdminForm()
	if form.validate_on_submit():
		if form.email.data == "admin@gmail.com" and form.password.data == "admin":
			return redirect(url_for("AdminDashBoard"))
		else:
			flash("Enter Valid Credentitals","danger")

	return render_template("adminlogin.html",form =form)

@app.route("/admin-dashboard",methods=['GET', 'POST'])
def AdminDashBoard():
	logout_user()
	form = AccountForm()
	pending_requests = Request.query.filter_by(status='Pending').all()

	if form.validate_on_submit():
		request = Request.query.filter((Request.account_number==form.account_number.data) & (Request.status=="Pending")).first()
		account  = Account.query.filter_by(account_number=form.account_number.data).first()
		
		if request.request_type == "deposit":
			account.balance += form.balance.data
			request.status = "Approved"
			db.session.commit()
		elif request.request_type == "withdraw":
			account.balance-=form.balance.data
			request.status = "Approved"
			db.session.commit()
		db.session.commit()
		return redirect(url_for('AdminDashBoard'))
	return render_template("dashboard/admin.html",pending_requests = pending_requests,form=form)


styles = {
    'Title': styles.ParagraphStyle(
        'Title',
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=20
    ),
    'Subtitle': styles.ParagraphStyle(
        'Subtitle',
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=10
    ),
}




@app.route('/generatepdf')
@login_required
def generatepdf():
    accounts = Account.query.filter_by(user_id=current_user.id).first()
    user = User.query.filter_by(username=current_user.username).first()
    start_date = session['start_date']
    end_date = session['end_date']
    start_date_obj = datetime.strptime(start_date,"%a, %d %b %Y %H:%M:%S %Z")
    end_obj = datetime.strptime(end_date,"%a, %d %b %Y %H:%M:%S %Z")
    start_date_formatted = start_date_obj.strftime('%Y-%m-%d')
    end_date_formatted = end_obj.strftime('%Y-%m-%d')

    requests = Request.query.filter(Request.transanct_date.between(start_date_formatted,end_date_formatted)).all()
    # Create a unique filename for the PDF
    filename = "transaction_history_{}.pdf".format(datetime.now().strftime('%Y%m%d%H%M%S'))

    # Create the PDF document
    doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
    elements = []

    # Add the title at the top
    title = Paragraph("Kings College of Engineering-Savings Account Portal", styles['Title'])
    elements.append(title)

    # Add the username, account number, and balance
    elements.append(Paragraph("Username: {}".format(user.username), styles['Subtitle']))
    elements.append(Paragraph("Account Number: {}".format(accounts.account_number), styles['Subtitle']))
    elements.append(Paragraph("Balance: {}".format(accounts.balance), styles['Subtitle']))

    # Create the table for transaction history
    data = [['Date', 'Account Number', 'Request Type', 'Amount', 'Status']]
    for request in requests:
        row = [request.transanct_date, request.account_number, request.request_type, request.amount, request.status]
        data.append(row)
    table = Table(data,colWidths=[doc.width / len(data[0]) for _ in data[0]])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)

    # Build the PDF document
    doc.build(elements)
    file_path = os.path.abspath(filename)

    # Send the generated PDF as a response to the browser
    return send_file(file_path, as_attachment=True)

@app.route('/get_balance', methods=['GET'])
def get_balance():
    # Get the account number from the query parameters
    account_number = request.args.get('account_number')
    account = Request.query.filter((Request.account_number==account_number) & (Request.status=="Pending")).first()
    balance = account.amount
    return str(balance)

if __name__ == '__main__':
    app.run(debug=True)