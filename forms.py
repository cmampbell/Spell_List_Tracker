"""Forms for Spell Tracker app."""

from wtforms import StringField, PasswordField, SelectField, SelectMultipleField, validators, ValidationError
from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory, ModelFormField
from models import db, User, Character, Stats, Classes, Char_Class

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

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken')
        
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email already in use')

class UserLoginForm(FlaskForm):
    '''Login for for Users.'''
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class CharacterModelForm(ModelForm):
    class Meta:
        model = Character

class ClassModelForm(CharacterModelForm):
    class_id = SelectField('Class', coerce=int)
    # subclasses = SelectField('Subclass')

class CharClassModelForm(ClassModelForm):
    class Meta:
        model = Char_Class
        
class CharacterCreationForm(CharClassModelForm):
    class Meta:
        model = Stats

class SpellListForm(FlaskForm):
    '''Hidden form to track spells user selects'''
    name = StringField('Spell List Name', [validators.Length(min=3, max=50), validators.DataRequired()])
    spells = SelectMultipleField('Spells', coerce=int)