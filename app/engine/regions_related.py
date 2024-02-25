# Module that handles all the processes regarding
# searching, loading, creating, and modifying region entries within the database.

# Module is supposed to be imported into the
# main module

import app.events.regions as events_region

def _constructing_namedtuple(alist):
    """
    a private function that creates a
    Region namedtuple that is used for
    various events.

    """
    main_entry = alist[0]
    region_id = main_entry[0]
    region_code = main_entry[1]
    local_code = main_entry[2]
    name = main_entry[3]
    continent_id = main_entry[4]
    country_id = main_entry[5]
    wikipedia_link = main_entry[6]
    keywords = main_entry[7]

    new_region_namedtuple = events_region.Region(region_id, region_code,
                                                 local_code, name,
                                                 continent_id, country_id,
                                                 wikipedia_link, keywords)

    return new_region_namedtuple

def searching_region_event(region_code, local_code, name, database):
    """
    Executes various sql query to access data
    to construct a Region namedtuple that is to
    be returned and yielded a RegionSearchResultEvent.
    """
    namedtuple_collection = []
    if region_code is not None:
        region_code_cursor = database.execute(
            'SELECT * FROM region '
            'WHERE region_code = (:reg_code);',
            {'reg_code': region_code}
        )

        region_code_compiler = list(region_code_cursor)
        reg_code_new_region_namedtuple = _constructing_namedtuple(region_code_compiler)
        namedtuple_collection.append(reg_code_new_region_namedtuple)

        region_code_cursor.close()

    if local_code is not None:
        local_code_cursor = database.execute(
            'SELECT * FROM region '
            'WHERE local_code = (:loc_code);',
            {'loc_code': local_code}
        )
        local_code_compiler = list(local_code_cursor)
        for entry in local_code_compiler:
            loc_code_new_region_namedtuple = _constructing_namedtuple([list(entry)])
            namedtuple_collection.append(loc_code_new_region_namedtuple)

        local_code_cursor.close()

    if name is not None:
        name_cursor = database.execute(
            'SELECT * FROM region '
            'WHERE name = (:reg_name);',
            {'reg_name': name}
        )
        name_compiler = list(name_cursor)
        name_new_region_namedtuple = _constructing_namedtuple(name_compiler)
        namedtuple_collection.append(name_new_region_namedtuple)

        name_cursor.close()

    return namedtuple_collection

def loading_region_event(region_id, database):
    """
    Executes a sql query statement to get all the
    information required to build a new Region
    namedtuple.

    This newly constructed namedtuple is then
    returned to be yielded with a RegionLoadedEvent
    object.

    """
    current_region_cursor = database.execute(
        'SELECT * FROM region '
        'WHERE region_id = (:reg_id);',
        {'reg_id': region_id}
    )

    current_region_compiler = list(current_region_cursor)
    new_region_namedtuple = _constructing_namedtuple(current_region_compiler)

    return new_region_namedtuple


def saving_new_region_event(event_region, database):
    """
    Executes various sql queries to access current
    information and to add a new entry to the database.

    If certain conditions are met, a Region namedtuple
    is going to be constructed and be returned to be
    yielded in the main module. If not, a
    SaveRegionFailedEvent is yielded.
    """
    region_id_cursor = database.execute(
        'SELECT region_id FROM region;'
    )
    region_code_cursor = database.execute(
        'SELECT region_code FROM region;'
    )
    continent_id_cursor = database.execute(
        'SELECT continent_id FROM continent;'
    )

    country_id_cursor = database.execute(
        'SELECT country_id FROM country'
    )

    region_id_compiler = list(region_id_cursor)
    region_code_compiler = list(region_code_cursor)
    continent_id_compiler = list(continent_id_cursor)
    country_id_compiler = list(country_id_cursor)

    region_id_collection = []
    for entry in region_id_compiler:
        for element in entry:
            region_id_collection.append(element)

    region_code_collection = []
    for entry in region_code_compiler:
        for element in entry:
            region_code_collection.append(element)

    continent_id_collection = []
    for entry in continent_id_compiler:
        for element in entry:
            continent_id_collection.append(element)

    country_id_collection = []
    for entry in country_id_compiler:
        for element in entry:
            country_id_collection.append(element)

    if event_region.region_code in region_code_collection:
        reason = 'Cannot add this region as the region_code is already taken, it must be unique.'
        return events_region.SaveRegionFailedEvent(reason)

    if event_region.continent_id not in continent_id_collection:
        reason = 'Cannot add this region due to the continent_id assigned to it being invalid.'
        return events_region.SaveRegionFailedEvent(reason)

    if event_region.country_id not in country_id_collection:
        reason = 'Cannot add this region due to the country_id assigned to it being invalid'
        return events_region.SaveRegionFailedEvent(reason)

    new_region_id = sorted(region_id_collection)[-1] + 1
    adding_region_cursor = database.execute(
        'INSERT INTO region '
        'VALUES (:reg_id, :reg_code, :loc_code, :name, :cont_id,'
        ':count_id, :wiki, :keys);',
        {'reg_id': new_region_id,
         'reg_code': event_region.region_code,
         'loc_code': event_region.local_code,
         'name': event_region.name,
         'cont_id': event_region.continent_id,
         'count_id': event_region.country_id,
         'wiki': event_region.wikipedia_link,
         'keys': event_region.keywords}
    )

    new_region_namedtuple = events_region.Region(new_region_id, event_region.region_code,
                                                 event_region.local_code, event_region.name,
                                                 event_region.continent_id, event_region.country_id,
                                                 event_region.wikipedia_link, event_region.keywords)

    adding_region_cursor.close()

    return new_region_namedtuple


def saving_region_event(event_region, database):
    """
    Executes various sql queries depending on the type
    of modifications done on the region. If certain
    conditions are not met, a SaveRegionFailedEvent is
    raised. Otherwise, a RegionSavedEvent is yielded

    """
    current_region_cursor = database.execute(
        'SELECT * FROM region '
        'WHERE region_id = (:reg_id);',
        {'reg_id': event_region.region_id}
    )
    current_region_viewer = list(current_region_cursor)
    current_region_id = current_region_viewer[0][0]
    current_region_code = current_region_viewer[0][1]
    current_local_code = current_region_viewer[0][2]
    current_name = current_region_viewer[0][3]
    current_continent_id = current_region_viewer[0][4]
    current_country_id = current_region_viewer[0][5]
    current_wiki_link = current_region_viewer[0][6]
    current_keywords = current_region_viewer[0][7]

    current_region_cursor.close()

    if current_region_code != event_region.region_code:
        checking_region_code_cursor = database.execute(
            'SELECT region_code FROM region;'
        )
        checking_region_code_compiler = list(checking_region_code_cursor)
        region_code_collection = []
        for entry in checking_region_code_compiler:
            for element in entry:
                region_code_collection.append(element)

        if event_region.region_code in region_code_collection:
            reason = 'Cannot modify the region as the region code must be unique'
            return events_region.SaveRegionFailedEvent(reason)

        saving_reg_code_cursor = database.execute(
            'UPDATE region '
            'SET region_code = (:reg_code) WHERE region_id = (:reg_id);',
            {'reg_code': event_region.region_code,
             'reg_id': current_region_id}
        )

        saving_reg_code_cursor.close()
        checking_region_code_cursor.close()

    if current_local_code != event_region.local_code:
        saving_local_code_cursor = database.execute(
            'UPDATE region SET local_code = (:loc_code) '
            'WHERE region_id = (:reg_id);',
            {'loc_code': event_region.local_code,
             'reg_id': current_region_id}
        )

        saving_local_code_cursor.close()

    if current_name != event_region.name:
        saving_name_cursor = database.execute(
            'UPDATE region SET name = (:reg_name) '
            'WHERE region_id = (:reg_id);',
            {'reg_name': event_region.name,
             'reg_id': current_region_id}
        )

        saving_name_cursor.close()

    if current_continent_id != event_region.continent_id:
        checking_continent_id_cursor = database.execute(
            'SELECT continent_id FROM continent;'
        )
        continent_id_compiler = list(checking_continent_id_cursor)
        continent_id_collection = []
        for entry in continent_id_compiler:
            for element in entry:
                continent_id_collection.append(element)
        if event_region.continent_id not in continent_id_collection:
            reason = 'Cannot make this modification as the continent_id must be of an existing one already.'
            return events_region.SaveRegionFailedEvent(reason)

        saving_continent_id_cursor = database.execute(
            'UPDATE region SET continent_id = (:cont_id) '
            'WHERE region_id = (:reg_id);',
            {'cont_id': event_region.continent_id,
             'reg_id': current_region_id}
        )

        checking_continent_id_cursor.close()
        saving_continent_id_cursor.close()

    if current_country_id != event_region.country_id:
        checking_country_id_cursor = database.execute(
            'SELECT country_id FROM country;'
            )
        country_id_compiler = list(checking_country_id_cursor)
        country_id_collection = []
        for entry in country_id_compiler:
            for element in entry:
                country_id_collection.append(element)

        if event_region.country_id not in country_id_collection:
            reason = 'Cannot make this modification to the region as the country_id has to be one of the existing ones.'
            return events_region.SaveRegionFailedEvent(reason)

        saving_country_id_cursor = database.execute(
            'UPDATE region SET country_id = (:count_id)'
            'WHERE region_id = (:reg_id);',
            {'count_id': event_region.country_id,
             'reg_id': current_region_id}
        )
        saving_country_id_cursor.close()
        checking_country_id_cursor.close()

    if current_wiki_link != event_region.wikipedia_link:
        saving_wiki_cursor = database.execute(
            'UPDATE region SET wikipedia_link = (:wiki_link)'
            'WHERE region_id = (:reg_id);',
            {'wiki_link': event_region.wikipedia_link,
             'reg_id': current_region_id}
        )
        saving_wiki_cursor.close()

    if current_keywords != event_region.keywords:
        saving_keywords_cursor = database.execute(
            'UPDATE region SET keywords = (:keys)'
            'WHERE region_id = (:reg_id);',
            {'keys': event_region.keywords,
             'reg_id': current_region_id}
        )

        saving_keywords_cursor.close()

    new_region_namedtuple = events_region.Region(current_region_id, event_region.region_code,
                                                 event_region.local_code, event_region.name,
                                                 event_region.continent_id, event_region.country_id,
                                                 event_region.wikipedia_link, event_region.keywords)

    return new_region_namedtuple

