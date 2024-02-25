# app/engine/main.py
# An object that represents the engine of the application.

import sqlite3
from pathlib import Path
### imports for events modules
import app.events.app as events_app
import app.events.database as events_db
import app.events.continents as events_cont
import app.events.countries as events_count
import app.events.regions as events_region
### imports for engine modules (the newly created ones)
import app.engine.applications_level as app_level
import app.engine.continents_related as cont_related
import app.engine.countries_related as count_related
import app.engine.regions_related as region_related

class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self._database = None


    def connect(self, path):
        """
        If given a valid database, it will connect to it
        via sqlite
        """
        sql_connection = sqlite3.connect(path)
        self._database = sql_connection
        self._database.execute('PRAGMA foreign_keys = ON;')


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        if type(event) == events_app.QuitInitiatedEvent:
            result = app_level.end_app_event()
            yield result

        elif type(event) == events_db.OpenDatabaseEvent:
            result = app_level.opening_database_event(event._path)
            self.connect(event._path)
            yield result

        elif type(event) == events_db.CloseDatabaseEvent:
            result = app_level.closing_database_event()
            self._database.commit()
            self._database.close()
            yield result

        elif type(event) == events_cont.StartContinentSearchEvent:
            compiler = cont_related.start_searching_continent_event(event._name, event._continent_code, self._database)
            continent_namedtuples = cont_related.constructing_continent_namedtuple(compiler)
            for continent in continent_namedtuples:
                yield events_cont.ContinentSearchResultEvent(continent)

        elif type(event) == events_cont.LoadContinentEvent:
            continent_namedtuples = cont_related.loading_continent_event(event._continent_id, self._database)
            for continent in continent_namedtuples:
                yield events_cont.ContinentLoadedEvent(continent)

        elif type(event) == events_cont.SaveNewContinentEvent:
            result = cont_related.saving_new_continent(event._continent, self._database)
            if type(result) == events_cont.SaveContinentFailedEvent:
                yield result
            else:
                yield events_cont.ContinentSavedEvent(result)

        elif type(event) == events_cont.SaveContinentEvent:
            result = cont_related.saving_continent_event(event._continent, self._database)
            if type(result) == events_cont.SaveContinentFailedEvent:
                yield result
            else:
                yield events_cont.ContinentSavedEvent(result)

        elif type(event) == events_count.StartCountrySearchEvent:
            result = count_related.searching_country_event(event._name, event._country_code, self._database)
            for entry in result:
                yield events_count.CountrySearchResultEvent(entry)

        elif type(event) == events_count.LoadCountryEvent:
            result = count_related.loading_country_event(event._country_id, self._database)
            yield events_count.CountryLoadedEvent(result)

        elif type(event) == events_count.SaveNewCountryEvent:
            result = count_related.saving_new_country_event(event._country, self._database)
            if type(result) == events_count.SaveCountryFailedEvent:
                yield result
            else:
                yield events_count.CountrySavedEvent(result)

        elif type(event) == events_count.SaveCountryEvent:
            result = count_related.saving_country_event(event._country, self._database)
            if type(result) == events_count.SaveCountryFailedEvent:
                yield result
            else:
                yield events_count.CountrySavedEvent(result)

        elif type(event) == events_region.StartRegionSearchEvent:
            result = region_related.searching_region_event(event._region_code, event._local_code, event._name, self._database)
            for entry in result:
                yield events_region.RegionSearchResultEvent(entry)

        elif type(event) == events_region.LoadRegionEvent:
            result = region_related.loading_region_event(event._region_id, self._database)
            yield events_region.RegionLoadedEvent(result)

        elif type(event) == events_region.SaveNewRegionEvent:
            result = region_related.saving_new_region_event(event._region, self._database)
            if type(result) == events_region.SaveRegionFailedEvent:
                yield result
            else:
                yield events_region.RegionSavedEvent(result)

        elif type(event) == events_region.SaveRegionEvent:
            result = region_related.saving_region_event(event._region, self._database)
            if type(result) == events_region.SaveRegionFailedEvent:
                yield result
            else:
                yield events_region.RegionSavedEvent(result)

