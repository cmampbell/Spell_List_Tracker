'''Character model tests'''

import os
from unittest import TestCase

from models import db, User, Character, Stats, Char_Class, Spell

os.environ['DATABASE_URL'] = 'postgresql:///spell-tracker-test'

from app import app

# only needed to seed initial db
# db.drop_all()
# db.create_all()
# seed_db_classes()

class UnitCharacterModelTestCase(TestCase):
    '''Test Character Model'''
    def setUp(self):
        User.query.delete()
        Character.query.delete()

        self.user = User(
            email="test@hotmail.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(self.user)
        db.session.commit()

    def test_new_character(self):
        '''Does the character model work as intended?'''

        char = Character(
            name='TestChar',
            user_id=self.user.id
        )

        db.session.add(char)
        db.session.commit()

        #check that char object name is correct
        self.assertEqual(char.name, 'TestChar')

        #check that char is assigned an id
        self.assertIsNotNone(char.id)

        #check that user id is correct
        self.assertEqual(char.user_id, self.user.id)

    def test_character_user_integration(self):
        '''Do the chracter and user classes work as intended?'''

        char = Character(
            name='TestChar',
            user_id=self.user.id
        )

        self.user.characters.append(char)

        #check that the character is in user.characters
        self.assertEqual(len(self.user.characters), 1)
        self.assertIn(char, self.user.characters)

        #check that get_classes returns None when the character has no classes
        self.assertIsNone(char.get_classes())

class StatsModelTestCase(TestCase):
    '''Testing Stats Model'''

    def setUp(self):
        User.query.delete()
        Character.query.delete()

        self.user = User(
            email="test@hotmail.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.char = Character(
            name='TestChar',
            user_id=self.user.id
        )

        db.session.add(self.user)
        db.session.commit()

    def test_stats_model(self):
        '''Testing the stats model'''

        stats = Stats(            
            HP=10,
            STR=10,
            DEX=10,
            CON=10,
            INT=10,
            WIS=10,
            CHA=10
        )

        self.char.stats = stats
        db.session.commit()

        #check that the character has stats
        self.assertIsNotNone(self.char.stats)

        #check that serialize stats returns a dict
        self.assertTrue(isinstance(stats.serialize_stats(), dict))

        stat_dict = stats.serialize_stats()
        #check that serialize stats contains all field needed
        self.assertIn('HP', stat_dict)
        self.assertIn('STR', stat_dict)
        self.assertIn('DEX', stat_dict)
        self.assertIn('CON', stat_dict)
        self.assertIn('INT', stat_dict)
        self.assertIn('WIS', stat_dict)
        self.assertIn('CHA', stat_dict)

class CharacterModelClassesModelIntegrationTestCase(TestCase):
    '''Testing the character model methods'''
    def setUp(self):
        User.query.delete()
        Character.query.delete()

        self.user = User(
            email="test@hotmail.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.char = Character(
            name='TestChar',
            user_id=self.user.id
        )

        db.session.add(self.user)
        db.session.commit()

    def test_char_classes_model(self):
        '''Testing the character and char_class relationship'''

        _class = Char_Class(class_id=4, level=5)

        self.char.classes.append(_class)

        self.assertEqual(len(self.char.classes), 1)
        self.assertIn(_class, self.char.classes)


class CharacterModelMethodsTestCase(TestCase):
    '''Testing the character model methods'''
    def setUp(self):
        Character.query.delete()
        User.query.delete()
        Spell.query.delete()

        self.user = User(
            email="test@hotmail.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.stats = Stats(            
            HP=10,
            STR=10,
            DEX=10,
            CON=10,
            INT=10,
            WIS=10,
            CHA=10
        )

        db.session.add(self.user)
        db.session.commit()

        self.char = Character(
            name='TestChar',
            user_id=self.user.id
        )

        char_class = Char_Class(class_id=4, level=4)

        self.char.classes.append(char_class)
        self.char.stats = self.stats
        db.session.add(self.char)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_get_classes_method(self):
        '''Does get classes return the correct classes in list form'''

        classes = self.char.get_classes()

        self.assertEqual(self.char.classes[0].class_name.index, classes[0]['class_name'])
        self.assertTrue(isinstance(classes, list))

    def test_serialize_character(self):
        '''Does serialize character return the necessary info?'''

        info = self.char.serialize_character().values()

        self.assertIn(self.char.name, info)
        self.assertIn(self.char.classes[0].class_name.index, info)
        self.assertIn(self.char.classes[0].level, info)

    def test_get_class_spells(self):
        '''Does get_class_spells return a set of available spells for the class?'''

        spells = self.char.get_class_spells()

        self.assertIsNotNone(spells)
        self.assertTrue(isinstance(spells, set))
        self.assertGreater(len(spells), 0)

    def test_get_spell_slots(self):
        '''Does get_spell_slots method return a list of spell slots?'''

        slots = self.char.get_spell_slots()
        keys = slots[0].keys()

        self.assertIsNotNone(slots)
        self.assertTrue(isinstance(slots, list))
        self.assertIn('spell_slots_level_1', keys)

    def test_get_spell_slots_no_spells(self):
        char_class = Char_Class(class_id=1, level=4)
        self.char.classes.pop()
        self.char.classes.append(char_class)
        db.session.commit()

        slots = self.char.get_spell_slots()

        #check that slots is an empty array
        self.assertEqual(len(slots), 0)

    def test_get_highest_spell_level(self):
        '''Does get_highest_spell_level return
        the highest available spell level?'''

        slots = self.char.get_spell_slots()
        highest_spell_level = self.char.get_highest_spell_level(slots)

        self.assertIsNotNone(highest_spell_level)
        self.assertGreater(highest_spell_level, 0)
        self.assertTrue(highest_spell_level < 10)

    def add_spells_to_db(self):
        '''Add spells to test db for testing purposes'''
        self.spell1 = Spell(index='cure-wounds', name='Cure Wounds', level=1)
        self.spell2 = Spell(index='guidance', name='Guidance', level=0)
        db.session.add(self.spell1)
        db.session.add(self.spell2)
        db.session.commit()

    def test_get_spells_from_db(self):
        '''Does the get spells from db method return a list
        of available spells for that character?'''

        slots = self.char.get_spell_slots()

        self.add_spells_to_db()
        spell_objects = self.char.get_spells_from_db(slots)

        spells = [(spell.id, spell.name) for spell in spell_objects]

        # check that the method returned the two spells in our db
        self.assertEqual(len(spells), 2)

        self.assertIn((self.spell1.id, self.spell1.name), spells)
        self.assertIn((self.spell2.id, self.spell2.name), spells)





