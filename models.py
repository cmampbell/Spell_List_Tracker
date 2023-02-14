"""SQLAlchemy models for Spell Tracker."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.String,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.String,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.String,
        nullable=False,
    )

    characters = db.relationship('Character', backref='user', cascade="all, delete-orphan", passive_deletes=True) 

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            if bcrypt.check_password_hash(user.password, password):
                return user

        return False
    
class Character(db.Model):
    '''DnD Character Model for users'''

    __tablename__ = 'characters'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    name = db.Column(
        db.String,
        nullable=False,
    )

    stats = db.relationship('Stats', uselist=False, cascade="all, delete-orphan", passive_deletes=True)

    classes = db.relationship('Char_Class', cascade="all, delete-orphan", passive_deletes=True)

    # db.relationship('spell_lists', cascade="all,delete")

    def get_classes(self):
        '''Returns a list of classes for this character'''
        if len(self.classes) != 0:
            return [_class for _class in self.classes]
        else:
            return None

    def serialize_character(self):
        '''Returns a dict of all necessary fields for character form'''

        #stats.serialize_stats returns a dict
        char = self.stats.serialize_stats()

        char['name'] = self.name
        char['class_name'] = self.get_classes()[0].class_name
        char['subclass_name'] = self.get_classes()[0].subclass_name
        char['level'] = self.get_classes()[0].level

        return char

    def user_dupe_character(self, name):
        '''This method will check the users list of characters.
        Returns true if a character with the same name already exists,
        will return false if the name is unique to this user
        
        This will prevent users from having multiples of the same character
        while allowing users to have characters with names already taken by other users'''

        if name in [char.name for char in self.characters]:
            return True
        else:
            return False

    

class Stats(db.Model):
    '''Model for character stats'''

    __tablename__='stats'

    def __repr__(self):
        return f"<Char #{self.char_id}: HP:{self.HP}, STR:{self.STR}, DEX:{self.DEX}, CON:{self.CON}, INT:{self.INT}, WIS:{self.WIS}, CHA:{self.CHA}>"

    char_id = db.Column(
        db.Integer,
        db.ForeignKey('characters.id', ondelete='CASCADE'),
        primary_key=True
    )

    HP = db.Column(
        db.Integer,
        nullable=False
    )

    STR = db.Column(
        db.Integer,
        nullable=False
    )

    DEX = db.Column(
        db.Integer,
        nullable=False
    )

    CON = db.Column(
        db.Integer,
        nullable=False
    )

    INT = db.Column(
        db.Integer,
        nullable=False
    )

    WIS = db.Column(
        db.Integer,
        nullable=False
    )

    CHA = db.Column(
        db.Integer,
        nullable=False
    )

    def serialize_stats(self):
        '''Returns a dict of stats'''
        return {
            'HP': self.HP,
            'STR': self.STR,
            'DEX': self.DEX,
            'CON': self.CON,
            'INT': self.INT,
            'WIS': self.WIS,
            'CHA': self.CHA
        }

class Char_Class(db.Model):
    '''Model for game classes for characters'''

    __tablename__ = 'char_classes'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    char_id = db.Column(
        db.Integer,
        db.ForeignKey('characters.id', ondelete='CASCADE')
    )

    class_name = db.Column(
        db.String,
        nullable=False
    )

    subclass_name = db.Column(
        db.String
    )

    level = db.Column(
        db.Integer,
        nullable=False
    )