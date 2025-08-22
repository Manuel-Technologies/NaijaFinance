from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Regexp
from models import User

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20),
        Regexp('^[A-Za-z0-9_]+$', message='Username must contain only letters, numbers, and underscores')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Regexp('^(\+234|0)[789][01][0-9]{8}$', message='Please enter a valid Nigerian phone number')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user:
            raise ValidationError('Phone number already registered. Please use a different number.')

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class TransferForm(FlaskForm):
    recipient = StringField('Recipient (Username or Wallet Number)', validators=[
        DataRequired(),
        Length(min=4, max=20)
    ])
    amount = DecimalField('Amount (₦)', validators=[
        DataRequired(),
        NumberRange(min=1, max=999999, message='Amount must be between ₦1 and ₦999,999')
    ])
    description = TextAreaField('Description (Optional)', validators=[
        Length(max=200)
    ])

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Regexp('^(\+234|0)[789][01][0-9]{8}$', message='Please enter a valid Nigerian phone number')
    ])
