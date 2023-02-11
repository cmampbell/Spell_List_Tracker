"""Forms for Spell Tracker app."""

from wtforms import StringField, PasswordField, validators
from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory, ModelFormField
from models import db, Character, Stats, Char_Class

BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

class UserSignUpForm(FlaskForm):
    """Sign up form for Users."""
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Length(min=6),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class UserLoginForm(FlaskForm):
    '''Login for for Users.'''
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class CharacterModelForm(ModelForm):
    class Meta:
        model = Character

class ClassModelForm(CharacterModelForm):
    class Meta:
        model = Char_Class

class CharacterCreationForm(ClassModelForm):
    class Meta:
        model = Stats