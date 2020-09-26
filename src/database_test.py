from database import database, clear_database

def test_database_clear():
    # use some test helpers to populate with some more realistic data
    database['users'].append(1)
    database['users'].append(2)
    database['channels'].append(3)
    database['channels'].append(4)
    database['channels'].append(5)
    database['active_tokens'].append(6)
    database['active_tokens'].append(7)

    clear_database()

    # make sure we still have all of our keys
    assert "users" in database
    assert "channels" in database
    assert "active_tokens" in database

    for key in database:
        # make sure it's still a list
        assert isinstance(database[key], list)
        # make sure we have a bunch of empty lists
        assert len(database[key]) == 0