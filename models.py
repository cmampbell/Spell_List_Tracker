"""SQLAlchemy models for Spell Tracker."""

import requests
from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

base_url = 'https://www.dnd5eapi.co'

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

    characters = db.relationship('Character', backref='user', cascade="all, delete, delete-orphan", passive_deletes=True) 

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
        
    def has_spell_lists(self):
        '''This method will determine if a user has any spell lists
        associated with their account. This makes things easier for us
        when we are designing the user details page'''
        for char in self.characters:
            if len(char.spell_lists) > 0:
                return True
        
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

    stats = db.relationship('Stats', uselist=False, cascade="all, delete, delete-orphan")

    classes = db.relationship('Char_Class', cascade="all, delete, delete-orphan")

    spell_lists = db.relationship('SpellList', cascade="all, delete-orphan", backref='char')

    def get_classes(self):
        '''Returns a list of classes for this character
        
        This was structured to return an array in order to
        allow for characters to have multiple classes. 
        
        The multiclass functionality is not implemented yet'''
        if len(self.classes) != 0:
            return [{'level':_class.level, 'class_name':_class.class_name.index} for _class in self.classes]
        else:
            return None

    def serialize_character(self):
        '''Returns a dict of all necessary fields for character form'''

        #stats.serialize_stats returns a dict
        char = self.stats.serialize_stats()

        char['name'] = self.name
        # the two lines below would need to change when multi-classing is implemented
        char['classes'] = self.get_classes()[0]['class_name']
        char['level'] = self.get_classes()[0]['level']

        return char

    def get_class_spells(self):
        '''Makes get request to API for a list of spell indexes that are available
        to this class. Then we add those indexes to a set and move onto the next class
        for that character.
    
        If no spells are available we return False, otherwise we return the set of spel
        indexes.'''
    
        available_spells = set()
        for _class in self.get_classes():
            #make request to api for spells available to the current character class
            results = requests.get(f'{base_url}/api/classes/{_class["class_name"]}/spells').json()['results']

            #create a set of spell_indexes from the restults of the api call
            new_spells = {result['index'] for result in results}

            #add the spells to the set of available spells
            available_spells.update(new_spells)

        if len(available_spells) == 0:
            return None
        else:
            return available_spells

    def get_spell_slots(self):
        '''Returns a dict with available spell slots'''
        slots=[]
        for _class in self.get_classes():
            #api call to get level info by character class
            resp = requests.get(f"{base_url}/api/classes/{_class['class_name']}/levels").json()

            #loop through api response to find level info for character level
            for item in resp:
                if item['level'] == _class['level'] and 'spellcasting' in item:
                    slots.append(item['spellcasting'])
    
        return slots

    def get_highest_spell_level(self, slots_by_class):
        '''Return the highest available spell slot to for this character'''
        # clean spellcasting dict of spell levels with no available spell slots
        highest_spell_level = 0

        for spell_slots in slots_by_class:
            for key in list(spell_slots.keys()):
                if spell_slots[key] == 0 and 'spell_slot' in key:
                    del spell_slots[key]

                elif 'spell_slot' in key:
                    highest_spell_level += 1
                    new_key = key.replace('_', ' ').title()
                    spell_slots[new_key] = spell_slots[key]
                    del spell_slots[key]

                elif 'cantrip' in key:
                    new_key = key.replace('_', ' ').title()
                    spell_slots[new_key] = spell_slots[key]
                    del spell_slots[key]
                    
        return highest_spell_level
    
    def get_spells_from_db(self, slots):
        '''Get all available spell objects from db'''
        # query api for index of spells for characters classes
        spells = self.get_class_spells()

        highest_spell_level = self.get_highest_spell_level(slots)

        #get all spells from our database that have a level less than or equal to the highest level spell slot
        spell_objects = (db.session.query(Spell).filter(Spell.level <= highest_spell_level, Spell.index.in_(spells))
                            .order_by(Spell.level, Spell.name))
        
        return spell_objects


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

class Classes(db.Model):
    '''Model for available character classes'''

    __tablename__ = 'classes'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    index = db.Column(
        db.String,
        unique=True
    )

    name = db.Column(
        db.String,
        unique=True
    )

    url = db.Column(
        db.Text
    )

class Subclasses(db.Model):
    '''Model for available character subclasses'''

    __tablename__ = 'subclasses'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    index = db.Column(
        db.String
    )

    name = db.Column(
        db.String,
        nullable=False
    )

    url = db.Column(
        db.Text
    )

    parent_class = db.Column(
        db.String,
        db.ForeignKey('classes.index'),
        nullable=False
    )

class Char_Class(db.Model):
    '''Join table to track characters class, subclass, and level'''

    __tablename__ = 'char_classes'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    char_id = db.Column(
        db.Integer,
        db.ForeignKey('characters.id', ondelete='CASCADE')
    )

    class_id = db.Column(
        db.Integer,
        db.ForeignKey('classes.id')
    )

    subclass_id = db.Column(
        db.Integer,
        db.ForeignKey('subclasses.id')
    )

    level = db.Column(
        db.Integer,
        nullable=False
    )

    class_name = db.relationship('Classes')

class Spell(db.Model):
    '''Table of available spells. We save certain info in the database,
    the rest of the data we can make an AJAX request on front-end to retrieve.
    This is everything we want to save on the backend and display on the spell list page'''

    __tablename__ = 'spells'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    index = db.Column(
        db.String,
        unique=True
    )

    name = db.Column(
        db.String,
        unique=True
    )

    range = db.Column(
        db.String
    )    

    duration = db.Column(
        db.String
    )

    concentration = db.Column(
        db.Boolean
    )

    casting_time = db.Column(
        db.String
    )

    level = db.Column(
        db.Integer
    )

    damaging = db.Column(
        db.Boolean
    )

    healing = db.Column(
        db.Boolean
    )

    school = db.Column(
        db.String
    )

    def serialize_self(self):
        return {
            'name': self.name,
            'range': self.range,
            'duration': self.duration,
            'concentration': self.concentration,
            'casting time': self.casting_time,
            'spell level': self.level,
            'damaging': self.damaging,
            'healing': self.healing,
            'school': self.school
        }

class SpellList(db.Model):
    '''Table of spell lists made by users with their characters'''

    __tablename__ = 'spell_lists'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    char_id = db.Column(
        db.Integer,
        db.ForeignKey('characters.id', ondelete='CASCADE')
    )

    name = db.Column(
        db.String,
        unique=True
    )

    date = db.Column(
        db.Date,
        nullable=False,
        default=datetime.utcnow()
    )

    spells = db.relationship('Spell', secondary="spell_list_spells", backref='spell_lists')

    spell_list_spells = db.relationship('SpellListSpells', cascade='all, delete, delete-orphan', passive_deletes=True, overlaps="spell_lists, spells")

class SpellListSpells(db.Model):
    '''Through table to track which spells are in each spell list'''

    __tablename__ = 'spell_list_spells'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    list_id = db.Column(
        db.Integer,
        db.ForeignKey('spell_lists.id', ondelete='CASCADE')
    )

    spell_id = db.Column(
        db.Integer,
        db.ForeignKey('spells.id')
    )