# Spell List Creator #
 https://spelllistcreator.onrender.com

## Project Description

Spell List Tracker was designed as a Capstone project for the Springboard Software Engineering Bootcamp. Spell List Tracker is used by Dungeons and Dragons players to create spell lists that they can use for their characters.

Spell List Tracker offers a simple user interface for users to create their characters. Once a character is created the user can create a spell list using the sites list creator. 

Inside the list creator users are served a selection of spells that are available to their character. They can click on the spells for more info, filter spells by name, spell level, and other parameters. 

Once a user finds a spell, they simply drag the spell into their spell list. When they have a full list, they give the list a name, and save the spell list to that character.

## API

Spell List Tracker uses this [**API**](https://www.dnd5eapi.co/ "API") 

The API only features spells from Dungeons and Dragons Fifth Edition, that are covered under the Open Game License from Wizards of the Coast. The API does not include spells from any of the expansion books such as Xanathar's Guide To Everything.

## Tech Stack


Front-End: HTML, CSS, Javascript 
Back-End: Python, Flask, Postgresql

Spell List Tracker uses bcrypt for authenification and authorization, WTForms for forms and validation, jinja2 for html templates, and SQLAlchemy as the database ORM.

