# Module that handles all the process regarding searching,
# loading, saving, and saving a modified countries into
# the database.

# Module is supposed to be imported into the main module

import app.events.countries as events_count


def _constructing_country_namedtuple(alist):
    """
    A private function that is used in other functions
    of this module to construct a namedtuple from a list.
    """
    main_entry = alist[0]
    country_id, country_code, name, continent_id, wiki_link, keywords = main_entry
    new_country_namedtuple = events_count.Country(country_id, country_code, name, continent_id, wiki_link, keywords)

    return new_country_namedtuple

def searching_country_event(event_name, event_country_code, database):
    """
    A function that executes various sql statements that match the
    different events that can occur when searching for continent(s).

    The information from the sql statement is then processed into a
    Country namedtuple(s) to be returned and yielded in the main module.
    """
    if event_name is None and event_country_code is not None:
        country_code_cursor = database.execute(
            'SELECT * FROM country '
            'WHERE country_code = (:count_code);',
            {'count_code': event_country_code}
        )

        country_code_compiler = list(country_code_cursor)
        new_country_namedtuple = [_constructing_country_namedtuple(country_code_compiler)]
        country_code_cursor.close()

    elif event_name is not None and event_country_code is None:
        country_name_cursor = database.execute(
            'SELECT * FROM country '
            'WHERE name = (:count_name);',
            {'count_name': event_name}
        )

        country_name_compiler = list(country_name_cursor)
        new_country_namedtuple = [_constructing_country_namedtuple(country_name_compiler)]
        country_name_cursor.close()

    elif event_name is not None and event_country_code is not None:
        country_code_and_name_cursor = database.execute(
            'SELECT * FROM country '
            'WHERE country_code = (:count_code) OR name = (:count_name);',
            {'count_code': event_country_code,
             'count_name': event_name}
        )

        country_name_and_code_compiler = list(country_code_and_name_cursor)
        namedtuple_list = []
        for entry in country_name_and_code_compiler:
            ind_country = _constructing_country_namedtuple([list(entry)])
            namedtuple_list.append(ind_country)

        new_country_namedtuple = namedtuple_list
        country_code_and_name_cursor.close()

    return new_country_namedtuple

def loading_country_event(event_country_id, database):
    """
    Executes a sql query to get all the information of the
    specific entry within the database based on the current
    country_id.

    Based on the information given from the sql query, a country
    namedtuple is constructed to be returned and be yielded
    with the ContinentLoadedEvent object

    """

    current_country_cursor = database.execute(
        'SELECT * FROM country WHERE country_id = (:count_id);',
        {'count_id': event_country_id}
    )

    current_country_compiler = list(current_country_cursor)

    new_country_namedtuple = _constructing_country_namedtuple(current_country_compiler)
    current_country_cursor.close()

    return new_country_namedtuple

def saving_new_country_event(event_country, database):
    """
    Executes various sql queries to get all the
    country_id, country_code, and continent_code
    from all the data table of country.

    It then checks whether if the newly inputted
    information for the country are valid, if not
    a CountrySavedEvent object is returned and yielded.
    Otherwise, a new Country namedtuple is returned
    and yielded with a CountrySavedEvent.
    """
    country_id_cursor = database.execute(
        'SELECT country_id FROM country;'
    )
    country_code_cursor = database.execute(
        'SELECT country_code FROM country;'
    )
    continent_id_cursor = database.execute(
        'SELECT continent_id FROM country;'
    )

    country_id_compiler = list(country_id_cursor)
    country_code_compiler = list(country_code_cursor)
    continent_id_compiler = list(continent_id_cursor)

    country_id_cursor.close()
    country_code_cursor.close()
    continent_id_cursor.close()

    country_id_collection = []
    for ind in country_id_compiler:
        for entry in ind:
            country_id_collection.append(entry)

    country_code_collection = []
    for ind in country_code_compiler:
        for entry in ind:
            country_code_collection.append(entry)

    continent_id_collection = set()
    for ind in continent_id_compiler:
        for entry in ind:
            continent_id_collection.add(entry)

    if event_country.country_code in country_code_collection:
        reason = "Cannot add this country due to the country code is already taken as it must be unique."
        return events_count.SaveCountryFailedEvent(reason)

    if event_country.country_code.isnumeric():
        reason = 'Cannot add this country due to having an invalid type of a country_code.'
        return events_count.SaveCountryFailedEvent(reason)

    if event_country.name.isnumeric():
        reason = "Cannot add this country due to the name being of an invalid type."
        return events_count.SaveCountryFailedEvent(reason)

    if event_country.wikipedia_link.isnumeric():
        reason = "Cannot add this country due to the wikipedia link being of the wrong type."
        return events_count.SaveCountryFailedEvent(reason)

    if event_country.keywords.isnumeric():
        reason = "Cannot add this country due to the keywords not being the wrong type."
        return events_count.SaveCountryFailedEvent(reason)

    if event_country.continent_id not in continent_id_collection:
        reason = "Cannot add this country due to the continent_id not being a valid one."
        return events_count.SaveCountryFailedEvent(reason)

    new_country_id = sorted(country_id_collection)[-1] + 1
    adding_new_country_cursor = database.execute(
        'INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords)'
        'VALUES (:new_count_id, :count_code, :count_name, :cont_id, :wiki, :keys);',
        {'new_count_id': new_country_id, 'count_code': event_country.country_code,
         'count_name': event_country.name, 'cont_id': event_country.continent_id,
         'wiki': event_country.wikipedia_link, 'keys': event_country.keywords}
    )

    new_country_namedtuple = events_count.Country(new_country_id, event_country.country_code,
                                                  event_country.name, event_country.continent_id,
                                                  event_country.wikipedia_link, event_country.keywords)
    adding_new_country_cursor.close()

    return new_country_namedtuple

def saving_country_event(event_country, database):
    """
    Executes various different sql queries depending
    on the changes or modifications that have been
    done in the tkinter window.

    If certain conditions are not met, a
    SaveCountryFailedEvent object is returned
    and yielded in the main module.

    Otherwise, a newly created namedtuple is returned
    and yielded with a CountrySavedEvent object.
    """
    current_country_cursor = database.execute(
        'SELECT * FROM country WHERE country_id = (:count_id);',
        {'count_id': event_country.country_id}
    )
    current_country_viewer = list(current_country_cursor)
    current_country_id = current_country_viewer[0][0]
    current_country_code = current_country_viewer[0][1]
    current_country_name = current_country_viewer[0][2]
    current_continent_id = current_country_viewer[0][3]
    current_continent_wiki = current_country_viewer[0][4]
    current_continent_keys = current_country_viewer[0][5]

    current_country_cursor.close()

    if current_country_code != event_country.country_code:
        if event_country.country_code.isnumeric():
            reason = 'Cannot make this modification on the country due to the country_code being an invalid type'
            return events_count.SaveCountryFailedEvent(reason)

        checking_code_cursor = database.execute(
            'SELECT country_code FROM country;'
        )

        country_code_compiler = list(checking_code_cursor)
        country_code_collection = []
        for entry in country_code_compiler:
            for element in entry:
                country_code_collection.append(element)
        if event_country.country_code in country_code_collection:
            reason = 'Cannot make this modification since the country code is already taken and must be unique'
            return events_count.SaveCountryFailedEvent(reason)

        saving_code_cursor = database.execute(
            'UPDATE country SET country_code = (:count_code)'
            'WHERE country_id = (:count_id);',
            {'count_code': event_country.country_code,
             'count_id': current_country_id}
        )

        saving_code_cursor.close()
        checking_code_cursor.close()

    if current_country_name != event_country.name:
        if event_country.name.isnumeric():
            reason = 'Cannot make this modification due to the name being of the wrong type'
            return events_count.SaveCountryFailedEvent(reason)

        saving_name_cursor = database.execute(
            'UPDATE country SET name = (:count_name)'
            'WHERE country_id = (:count_id);',
            {'count_name': event_country.name,
             'count_id': current_country_id}
        )

        saving_name_cursor.close()

    if current_continent_id != event_country.continent_id:
        checking_cont_id_cursor = database.execute(
            'SELECT continent_id FROM country '
        )
        cont_id_compiler = list(checking_cont_id_cursor)
        cont_id_set = set()
        for entry in cont_id_compiler:
            for element in entry:
                cont_id_set.add(element)
        if event_country.continent_id not in cont_id_set:
            reason = 'Cannot make this modification as the continent_id must be one of the existing ones already.'
            return events_count.SaveCountryFailedEvent(reason)

        saving_continent_id_cursor = database.execute(
            'UPDATE country SET continent_id = (:cont_id)'
            'WHERE country_id = (:count_id);',
            {'cont_id': event_country.continent_id,
             'count_id': event_country.country_id}
        )

        checking_cont_id_cursor.close()
        saving_continent_id_cursor.close()

    if current_continent_wiki != event_country.wikipedia_link:
        if event_country.wikipedia_link.isnumeric():
            reason = 'Cannot make this modification as the wikipedia_link is of the wrong type'
            return events_count.SaveCountryFailedEvent(reason)

        saving_wiki_cursor = database.execute(
            'UPDATE country SET wikipedia_link = (:wiki)'
            'WHERE country_id = (:count_id);',
            {'wiki': event_country.wikipedia_link,
             'count_id': current_country_id}
        )

        saving_wiki_cursor.close()

    if current_continent_keys != event_country.keywords:
        if event_country.keywords.isnumeric():
            reason = 'Cannot make this modification due to the keywords being of the wrong type.'
            return events_count.SaveCountryFailedEvent(reason)

        saving_keys_cursor = database.execute(
            'UPDATE country SET keywords = (:keys)'
            'WHERE country_id = (:count_id);',
            {'keys': event_country.keywords,
             'count_id': current_country_id}
        )

        saving_keys_cursor.close()

    return events_count.Country(current_country_id, event_country.country_code,
                                event_country.name, event_country.continent_id,
                                event_country.wikipedia_link, event_country.keywords)

