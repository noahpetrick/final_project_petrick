import pymysql
from flask import g

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            # Database configuration
            # Configure MySQL
            host = 'w1h4cr5sb73o944p.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
            user = 'ctykflbhsrs3g09c',
            password = 'lvzyninku1mwxahn',
            database = 'ph0ckkd6qjxxsh2e',
            cursorclass=pymysql.cursors.DictCursor  # Set the default cursor class to DictCursor
        )
    return g.db

def is_connection_open(conn):
    try:
        conn.ping(reconnect=True)  # PyMySQL's way to check connection health
        return True
    except:
        return False

def close_db():
    db = g.pop('db', None)
    if db:
        db.close()