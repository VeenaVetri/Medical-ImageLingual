from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from imagelingual.models import User
from flask_login import current_user

language_list = [
    ('en', 'English'), ('hi', 'Hindi'),('zh', 'Chinese'),('ko', 'Korean'), ('de', 'German'), ('fr', 'French'),  ('ja', 'Japanese') ,('bn', 'Bengali'),
    ('te', 'Telugu'),
    ('mr', 'Marathi'),
    ('ta', 'Tamil'),
    ('ur', 'Urdu'),
    ('gu', 'Gujarati'),
    ('kn', 'Kannada'),
    ('ml', 'Malayalam'),('pa','Punjabi')]
country_list =[
    ('us', 'United States of America'),
    ('in', 'India'),
    ('uk', 'United Kingdom'),
    ('cn', 'China'),
    ('ca', 'Canada'),
    ('au', 'Australia'),
    ('kr', 'South Korea'),
    ('de', 'Germany'),
    ('fr', 'France'),
    ('jp', 'Japan'),
    ('cn','China')
]
role_list = [('user', 'User'), ('admin', 'Admin'), ('guest', 'Guest')]

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    preferred_lang = SelectField('Preferred Language', choices=language_list)
    country = SelectField('Country', choices=country_list)
    role = SelectField('Role', choices=role_list, 
                        validators=[DataRequired()])    
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SearchForm(FlaskForm):
    keyword = StringField('Enter Keyword', validators=[DataRequired()])
    submit = SubmitField('Post')


countries = ['', 'USA', 'India', 'UK', 'Canada', 'Australia', 'SouthKorea', 'Germany', 'France', 'Japan']

fields = ['','Oncology', 'Cardiology', 'Gastroenterology', 'Neurology', 'Pulmonology', 'Hematology', 'Orthopedics', 'Ophthalmology', 'Allergy and Immunology', 'Gynecology']

modalities = ['','PET', 'ECG', 'Endoscopy', 'MRI',  'Reports', 'X-rays', 'Fundus photography', 'CT scan', 'Ultrasound']

class DisplayForm(FlaskForm):
    country = SelectField('Country', choices=countries)
    field = SelectField('Domain', choices=fields)
    modality = SelectField('Modality', choices=modalities)    
    submit = SubmitField('Explore')

