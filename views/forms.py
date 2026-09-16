"""
Application Forms using Flask-WTF
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class RegisterForm(FlaskForm):
    """User Registration Form"""
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=6, message='Password must be at least 6 characters')
        ]
    )
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    """User Login Form"""
    username = StringField(
        'Username',
        validators=[DataRequired(message='Username is required')]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required')]
    )
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')


class SimulationForm(FlaskForm):
    """BB84 Simulation Configuration Form"""
    key_length = IntegerField(
        'Key Length (qubits)',
        validators=[
            DataRequired(message='Key length is required'),
            NumberRange(min=10, max=1000, message='Key length must be between 10 and 1000 qubits')
        ],
        default=64
    )
    has_eve = BooleanField('Enable Eavesdropper (Eve)')
    noise_rate = FloatField(
        'Channel Depolarizing Noise Rate (0.0 - 0.5)',
        validators=[
            Optional(),
            NumberRange(min=0.0, max=1.0, message='Noise rate must be between 0.0 and 1.0')
        ],
        default=0.0
    )
    submit = SubmitField('Run Simulation')

