from . import appbuilder, db
from .models import Country

def countries_fill():
    try:
        db.session.add(Country(country="United States", country_abbreviation="US"))
        db.session.add(Country(country="Canada", country_abbreviation="CA"))
        db.session.commit()
    except Exception as e:
        print(str(e))
        db.session.rollback()

def geo_fill():
    session = db.session()
    fd = open('app/geo_fill.sql', 'r')
    sqlFile = fd.read()
    fd.close()
    sqlCommands = sqlFile.split(';')
    print('Number of Commands to run:', len(sqlCommands))
    for command in sqlCommands:
        print(len(command))
        try:
            cursor = session.execute(command).cursor
            print(cursor)
            print('City State Filled')
            session.commit()
        except Exception as e:
            print("Command skipped: ", str(e))
