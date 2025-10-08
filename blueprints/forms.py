from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, EmailField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, Regexp
from models import User
import re

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters'),
        Regexp(r'^[A-Za-z\s]*$', message='First name must contain only letters and spaces')
    ])
    middle_name = StringField('Middle Name', validators=[
        Optional(),
        Length(max=50, message='Middle name must not exceed 50 characters'),
        Regexp(r'^[A-Za-z\s]*$', message='Middle name must contain only letters and spaces')
    ])
    surname = StringField('Surname', validators=[
        DataRequired(),
        Length(min=2, max=50, message='Surname must be between 2 and 50 characters'),
        Regexp(r'^[A-Za-z\s]*$', message='Surname must contain only letters and spaces')
    ])
    suffix = SelectField('Suffix', choices=[
        ('', 'None'),
        ('Jr.', 'Jr.'),
        ('Sr.', 'Sr.'),
        ('III', 'III'),
        ('IV', 'IV'),
        ('V', 'V')
    ], validators=[Optional()])
    
    id_type = SelectField('ID Type', choices=[
        ('', 'Select ID Type'),
        ('national_id', 'National ID'),
        ('drivers_license', 'Driver\'s License'),
        ('passport', 'Passport'),
        ('sss_id', 'SSS ID'),
        ('postal_id', 'Postal ID'),
        ('voters_id', 'Voter\'s ID'),
        ('prc_id', 'PRC ID'),
        ('school_id', 'School ID')
    ], validators=[DataRequired(message='Please select an ID type')])
    
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    phone = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=15, message='Please enter a valid phone number')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

    def validate_email(self, email):
        # Convert email to lowercase
        email.data = email.data.lower()
        
        # Check if email already exists
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')
        
        # Validate email domain and length
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        email_pattern = r'^[a-z0-9._%+-]{3,}@([a-z0-9.-]+\.[a-z]{2,})$'  # At least 3 chars before @
        
        match = re.match(email_pattern, email.data)
        if not match:
            raise ValidationError('Invalid email format. Email must have at least 3 characters before @ and use lowercase letters.')
        
        domain = match.group(1)
        if domain not in allowed_domains:
            raise ValidationError(f'Email domain not allowed. Please use one of: {", ".join(allowed_domains)}')
            
    def validate_first_name(self, field):
        # Convert to title case
        field.data = field.data.strip().title()
        # Check if the full name combination exists
        full_name = f"{field.data} {self.middle_name.data.strip().title() if self.middle_name.data else ''} {self.surname.data.strip().title()}".strip()
        existing_user = User.query.filter(User.name.ilike(full_name)).first()
        if existing_user:
            raise ValidationError('This name is already registered. Please use a different name.')

    def validate_password(self, field):
        password = field.data
        if (len(password) < 8 or
            not re.search(r'[A-Z]', password) or
            not re.search(r'[a-z]', password) or
            not re.search(r'\d', password) or
            not re.search(r'[^A-Za-z0-9]', password)):
            raise ValidationError('Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.')

class ForgotPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ]) 