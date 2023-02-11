import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Character, Stats, Char_Class
from forms import UserSignUpForm, UserLoginForm, CharacterCreationForm


CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///spell-tracker'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

connect_db(app)

app.app_context().push()

###################### SIGNUP + LOGIN #######################
@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = db.session.get(User, session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserSignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken")
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)
    
@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = UserLoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(f"/user/{user.id}")

        flash("Invalid credentials.")

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Successfully logged out!")
    return redirect('/')

###################### USER VIEWS ##########################
    
@app.route('/')
def show_home_page():
    return render_template('home.html', user=g.user)

@app.route('/user/<int:user_id>')
def show_user_page(user_id):
    '''Take user to their profile page'''

    if g.user.id != user_id:
        flash("You can't access this page")
        redirect('/')

    return render_template('users/details.html', user=g.user)

################### CHARACTER VIEWS #########################

@app.route('/characters/new', methods=['GET', 'POST'])
def show_character_form():
    '''Renders character form, or creates new character if form validates'''

    if not g.user:
        flash("You can't access this page")
        redirect('/')

    form = CharacterCreationForm()

    if form.validate_on_submit():
        user = db.session.get(User, g.user.id)

        char = Character(
            name=form.data['name']
        )

        stats = Stats(
            HP = form.data['HP'],
            STR = form.data['STR'],
            DEX = form.data['DEX'],
            CON = form.data['CON'],
            INT = form.data['INT'],
            WIS = form.data['WIS'],
            CHA = form.data['CHA']
        )

        _class = Char_Class(
            class_name = form.data['class_name'],
            subclass_name = form.data['subclass_name'],
            level = form.data['level']
        )

        char.stats.append(stats)
        char.classes.append(_class)
        user.characters.append(char)

        db.session.commit()

        return redirect(f'/char/{char.id}')

    return render_template('char/new.html', form=form)

@app.route('/char/<int:char_id>')
def show_char_details(char_id):
    '''Show the character details page'''
    #Check if the current user is the owner of this character
    # Might move this to jinja template

    if char_id in [char.id for char in g.user.characters]:
        owner = True

    char = db.session.get(Character, char_id)

    return render_template('char/char_details.html', user=g.user, char=char, stats=char.stats[0], owner=owner)
    
