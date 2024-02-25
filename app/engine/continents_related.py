# Module that handles all the process regarding searching,
# loading, saving, and saving a modified continent into
# the database.

# Module is supposed to be imported into the main module

import app.events.continents as events_cont

def start_searching_continent_event(event_name, event_continent_code, database):
    """
    Executes sql query statements depending on the various specific
    situations that are to occur when the user is searching.

    It returns a compiler that is composed of the continent's
    id, code, and name that has been converted into their
    corresponding object types.
    """
    continent_compiler = None
    if event_name is None and event_continent_code is not None:
        continent_cursor = database.execute(
            'SELECT continent_id, continent_code, name FROM continent '
            'WHERE continent_code = (:cont_code);', {'cont_code': event_continent_code}
        )

        continent_compiler = list(continent_cursor)
        continent_cursor.close()

    elif event_name is not None and event_continent_code is None:
        continent_cursor = database.execute(
            'SELECT continent_id, continent_code, name FROM continent '
            'WHERE name = (:cont_name);', {'cont_name': event_name}
        )

        continent_compiler = list(continent_cursor)
        continent_cursor.close()

    elif event_name is not None and event_continent_code is not None:
        continent_cursor = database.execute(
            'SELECT continent_id, continent_code, name FROM continent '
            'WHERE name = (:cont_name) OR continent_code = (:cont_code);'
            , {'cont_name': event_name, 'cont_code': event_continent_code}
        )

        continent_compiler = list(continent_cursor)
        continent_cursor.close()

    return continent_compiler

def constructing_continent_namedtuple(compiler):
    """
    Iterates through the compiler to convert each
    element into a Continent namedtuple by separating
    each element into the id, code and name.

    """
    continent_namedtuples = []
    for element in compiler:
        cont_id = element[0]
        cont_code = element[1]
        cont_name = element[2]
        n_tup = events_cont.Continent(cont_id, cont_code, cont_name)
        continent_namedtuples.append(n_tup)

    return continent_namedtuples


def loading_continent_event(event_cont_id, database):
    """
    Given the continent_id from the event, a sql query
    is executed to convert the result from the cursor as
    a list. This list is then passed on the
    constructing_continent_namedtuple function.

    The results are then yielded in the main module.
    """
    continent_cursor = database.execute(
        'SELECT continent_id, continent_code, name FROM continent '
        'WHERE continent_id = (:cont_id)', {'cont_id': event_cont_id}
    )

    compiler = list(continent_cursor)
    continent_namedtuples = constructing_continent_namedtuple(compiler)
    continent_cursor.close()

    return continent_namedtuples

def saving_new_continent(event_continent, database):
    """
    Executes a sql query statement to get all the current
    continent_id and continent_code to check if the newly
    inputted continent_id and continent_code are already taken
    within the database.

    If so, the function returns a SaveContinentFailedEvent with a
    friendly message that tells the reason why for the failure.

    If not, the function returns a ContinentSavedEvent with a newly
    constructed namedtuple with a new continent_id, the inputted continent_code,
    and the inputted name


    """
    continent_id_cursor = database.execute(
        'SELECT continent_id FROM continent;'
    )
    continent_code_cursor = database.execute(
        'SELECT continent_code FROM continent;'
    )
    continent_id_collection = list(continent_id_cursor)
    continent_code_collection = list(continent_code_cursor)

    id_collection = []
    for entry in continent_id_collection:
        for element in entry:
            id_collection.append(element)

    code_collection = []
    for entry in continent_code_collection:
        for element in entry:
            code_collection.append(element)

    if event_continent.continent_code in code_collection:
        reason = 'Cannot save the new continent. The continent_code for the new continent is already taken'
        return events_cont.SaveContinentFailedEvent(reason)
    else:
        new_continent_id = sorted(id_collection)[-1] + 1
        saving_continent_cursor = database.execute(
            'INSERT INTO continent (continent_id, continent_code, name)'
            'VALUES (:id, :code, :name);', {'id': new_continent_id,
                                            'code': event_continent.continent_code,
                                            'name': event_continent.name}
        )

        new_continent_namedtuple = events_cont.Continent(new_continent_id, event_continent.continent_code, event_continent.name)

        continent_code_cursor.close()
        continent_id_cursor.close()
        saving_continent_cursor.close()


        return new_continent_namedtuple

def saving_continent_event(event_continent, database):
    """
    This function checks whether if the continent_code and/or
    the name has been changed. If so, various sql queries are
    executed to update the database to match the desired changes
    done in the tkinter window.

    If the continent_code has been changed into an already existing
    continent_code within the database, a SaveContinentFailedEvent is
    returned with a user-friendly message.
    """
    current_continent_cursor = database.execute(
        'SELECT * FROM continent WHERE continent_id = (:cont_id);'
        , {'cont_id': event_continent.continent_id}
    )
    view_cursor = list(current_continent_cursor)
    current_continent_id = view_cursor[0][0]
    current_continent_code = view_cursor[0][1]
    current_continent_name = view_cursor[0][2]

    if event_continent.continent_code != current_continent_code and event_continent.name == current_continent_name:
        checking_code_cursor = database.execute(
            'SELECT continent_code FROM continent;'
        )

        continent_code_collection = list(checking_code_cursor)
        code_collection = []
        for entry in continent_code_collection:
            for element in entry:
                code_collection.append(element)

        if event_continent.continent_code in code_collection:
            reason = 'Cannot make this modification to the Continent due to the ' \
                     'new continent_code not being unique'

            return events_cont.SaveContinentFailedEvent(reason)

        changing_only_code_cursor = database.execute(
            'UPDATE continent SET continent_code = (:new_code)'
            'WHERE continent_id = (:cont_id);',
            {'new_code': event_continent.continent_code,
             'cont_id': current_continent_id}
        )

        new_continent_namedtuple = events_cont.Continent(event_continent.continent_id, event_continent.continent_code, event_continent.name)

        checking_code_cursor.close()
        changing_only_code_cursor.close()

    elif event_continent.continent_code == current_continent_code and event_continent.name != current_continent_name:
        changing_only_name_cursor = database.execute(
            'UPDATE continent SET name = (:new_name)'
            'WHERE continent_id = (:cont_id);',
            {'new_name': event_continent.name,
             'cont_id': current_continent_id}
        )

        new_continent_namedtuple = events_cont.Continent(event_continent.continent_id,
                                                         event_continent.continent_code,
                                                         event_continent.name)

        changing_only_name_cursor.close()

    elif event_continent.continent_code != current_continent_code and event_continent.name != current_continent_name:
        checking_code_cursor = database.execute(
            'SELECT continent_code FROM continent;'
        )

        continent_code_collection = list(checking_code_cursor)
        code_collection = []
        for entry in continent_code_collection:
            for element in entry:
                code_collection.append(element)

        if event_continent.continent_code in code_collection:
            reason = 'Cannot make this modification to the Continent due to the ' \
                     'new continent_code not being unique'

            return events_cont.SaveContinentFailedEvent(reason)

        changing_both_cursor = database.execute(
            'UPDATE continent '
            'SET continent_code = (:new_code), name = (:new_name)'
            'WHERE continent_id = (:cont_id);'
            , {'new_code': event_continent.continent_code,
               'new_name': event_continent.name,
               'cont_id': current_continent_id}
        )

        new_continent_namedtuple = events_cont.Continent(event_continent.continent_id,
                                                         event_continent.continent_code,
                                                         event_continent.name)

        changing_both_cursor.close()
        checking_code_cursor.close()

    return new_continent_namedtuple