# This module is for handling all the processes that are
# related to the tkinter window closing, opening a database,
# and closing the current opened database.

# This module is to be imported into the main.py module
from pathlib import Path
import app.events.app as events_app
import app.events.database as events_db

def end_app_event():
    """
    A function that returns the EndApplicationEvent
    from the events.app module
    """

    return events_app.EndApplicationEvent

def opening_database_event(event_path):
    """
    Checks whether chosen file is existing
    valid database that can be accessed.

    If not, user-friendly statements will be
    printed and return a DatabaseOpenFailedEvent object

    """
    if not Path(event_path).exists():
        reason = 'The given database does not exist'
        return events_db.DatabaseOpenFailedEvent(reason)
    else:
        if not Path(event_path).suffix == '.db':
            reason = 'The given database is an invalid one'
            return events_db.DatabaseOpenFailedEvent(reason)
        else:
            return events_db.DatabaseOpenedEvent(event_path)

def closing_database_event():
    """
    A function that returns DatabaseClosedEvent object
    to the main module.
    """
    return events_db.DatabaseClosedEvent

