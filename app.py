import os

from flask import Flask, render_template, flash, redirect, session, g

from models import db, connect_db, User, Character, Stats, Char_Class, Classes, Spell, SpellList
from forms import UserSignUpForm, UserLoginForm, DeleteUserForm, CharacterCreationForm, SpellListForm 

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///spell-tracker'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

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
        user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
                )
        db.session.commit()

        do_login(user)

        return redirect(f"/user/{user.id}")
    
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

        flash("Invalid credentials.", 'error')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Successfully logged out!", 'success')
    return redirect('/')

###################### USER VIEWS ##########################
    
@app.route('/')
def show_home_page():
    '''Shows home page if a user is not logged in'''

    if g.user:
        flash(f'Welcome back {g.user.username}!', 'success')
        return redirect(f'/user/{g.user.id}')

    else:
        user = None
    return render_template('home.html', user=user)

@app.route('/user/<int:user_id>')
def show_user_page(user_id):
    '''Take user to their profile page'''

    if g.user.id != user_id:
        flash("You can't access another users profile", 'error')
        redirect('/')

    return render_template('users/details.html', user=g.user, chars=g.user.characters)

@app.route('/user/<int:user_id>/delete', methods=['GET','POST'])
def delete_user(user_id):
    '''Delete users account'''
    user = db.session.get(User, user_id)

    if g.user.id != user_id:
        flash("You can't delete another user", 'error')
        redirect('/')

    form = DeleteUserForm()

    if form.validate_on_submit():

        # Delete the users characters first
        for char in user.characters:
            db.session.delete(char)

        db.session.commit()

        #then delete user
        db.session.delete(user)
        db.session.commit()

        flash(f'Deleted {user.username} account', 'success')
        return redirect('/')
    
    return render_template('users/delete.html', user=user, form=form)


################### CHARACTER VIEWS #########################

@app.route('/characters/new', methods=['GET', 'POST'])
def show_character_form():
    '''Renders character form, or creates new character if form validates'''

    if not g.user:
        flash("You need to be logged in to create a character", 'error')
        redirect('/login')

    form = CharacterCreationForm()

    # Pass in list of character class names from class table
    form.class_id.choices = [(_class.id, _class.name) for _class in db.session.query(Classes).all()]

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
            class_id = form.data['class_id'],
            level = form.data['level']
        )

        char.stats = stats
        char.classes.append(_class)
        user.characters.append(char)

        db.session.commit()

        flash(f'Successfully created {char.name}!', 'success')
        return redirect(f'/char/{char.id}')

    return render_template('char/new.html', form=form)

@app.route('/char/<int:char_id>')
def show_char_details(char_id):
    '''Show the character details page'''

    owner = False
    if g.user and char_id in [char.id for char in g.user.characters]:
        owner = True

    char = db.session.get(Character, char_id)

    stats = char.stats.serialize_stats().items()

    return render_template('char/char_details.html', user=g.user, char=char, stats=stats, owner=owner)

@app.route('/char/<int:char_id>/edit', methods=['GET', 'POST'])
def char_edit_form(char_id):
    '''Show form to edit a chracter
    Might change this later to be a front-end thing'''

    char = db.session.get(Character, char_id)

    form = CharacterCreationForm(data=char.serialize_character(), class_id=char.classes[0].class_name.id)
    form.class_id.choices = [(_class.id, _class.name) for _class in db.session.query(Classes).all()]

    if g.user.id != char.user_id:
        flash("You can not edit another users characters", 'error')
        return redirect(f'/char/{char_id}')

    if form.validate_on_submit():
        char.name = form.data['name']
        form.populate_obj(char.stats)
        form.populate_obj(char.classes[0])

        db.session.add(char)
        db.session.commit()

        flash(f'Succesfully updated {char.name}', 'success')
        return redirect(f'/char/{char_id}')

    return render_template('char/char_edit.html', char=char, form=form)

@app.route('/char/<int:char_id>/delete', methods=['POST'])
def delete_char(char_id):
    char = db.session.get(Character, char_id)

    if g.user.id != char.user_id:
        flash("You can not delete another users characters", 'error')
        return redirect(f'/char/{char.id}')
    
    db.session.delete(char)
    db.session.commit()

    flash(f'Successfully deleted {char.name}', 'success')
    return redirect(f'/user/{char.user_id}')
    

###################### SPELL LIST VIEWS #####################################    
@app.route('/char/<int:char_id>/spell_list/new', methods=['GET', 'POST'])
def new_spell_list_form(char_id):
    '''Show form to create a new spell list'''

    char = db.session.get(Character, char_id)

    if g.user.id != char.user_id:
        flash("You can not create a new spell list for another users character", 'error')
        return redirect(f'/char/{char_id}')

    #get spell slots available to character
    slots_by_class = char.get_spell_slots()
    
    if len(slots_by_class) == 0:
        flash(f'No spells available for {char.name}', 'error')
        return redirect(f'/char/{char_id}')
    
    #get all spells in db available to character
    spells = char.get_spells_from_db(slots_by_class)

    form = SpellListForm()
    form.spells.choices = [(spell.id, spell.name) for spell in spells]
    stats = char.stats.serialize_stats().items()

    if form.validate_on_submit():
        spell_list = SpellList(char_id=char.id, name=form.data['name'])

        # spells returned with the hidden select field
        selected_spells = form.data['spells']

        for spell in spells:
            if spell.id in selected_spells:
                spell_list.spells.append(spell)

        db.session.add(spell_list)
        db.session.commit()

        flash(f'Successdully created {spell_list.name} for {char.name}', 'success')
        return redirect(f'/char/{char.id}/spell_list/{spell_list.id}')

    return render_template('spell_list/new_spell_list.html', char=char, spells=spells, slots=slots_by_class, stats=stats, form=form)

@app.route('/char/<int:char_id>/spell_list/<int:spell_list_id>')
def show_spell_list_details(char_id, spell_list_id):
    '''Displays the selected spell list for that character'''
    char = db.session.get(Character, char_id)

    spell_list = db.session.get(SpellList, spell_list_id)

    owner = False
    if (g.user.id == char.user_id):
        owner = True

    return render_template('spell_list/spell_list_details.html', char=char, list=spell_list, owner=owner)

@app.route('/spell_list/<int:spell_list_id>/delete', methods=['POST'])
def delete_spell_list(spell_list_id):
    '''Allows users to delete their spell lists'''
    spell_list = db.session.get(SpellList, spell_list_id)

    if g.user.id != spell_list.char.user_id:
        flash("You can not delete another users spell list", 'error')
        return redirect(f'/char/{spell_list.char.id}')

    db.session.delete(spell_list)
    db.session.commit()

    flash(f'Successfully deleted {spell_list.name}', 'success')
    return redirect(f'/char/{spell_list.char_id}')