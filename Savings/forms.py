from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField,DecimalField,FloatField,DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError,NumberRange
from Savings.models import User 

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already Exists")



    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is  already Taken")




class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class TransactionForm(FlaskForm):
    account_number = StringField('Account Number', validators=[DataRequired()])
    transaction_type = SelectField('Transaction Type', choices=[('deposit', 'Deposit'), ('withdraw', 'Withdraw')], validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be greater than 0')])
    submit = SubmitField('Submit')


class AdminForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class AccountForm(FlaskForm):
    account_number = StringField('Account Number', validators=[DataRequired(), Length(min=1, max=20)])
    balance = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('Status', choices=[('pending', 'Pending'), ('Approved', 'Approved')],
                         validators=[DataRequired()])
    submit = SubmitField('Update')


class DateForm(FlaskForm):
    from_date = DateField('From Date', validators=[DataRequired()], format='%Y-%m-%d')
    to_date = DateField('To Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Download')