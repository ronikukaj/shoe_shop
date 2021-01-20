from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from shoe_shopping.models import User

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=7, max=30)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken please choose a different one!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use!')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=7, max=30)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ManagerForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login Manager')

class AddProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=["male", "female", "kids"])
    size = IntegerField('Size', validators=[DataRequired(), NumberRange(min=1, max=47)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    # picture_file = FileField('Upload Product Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Product')
