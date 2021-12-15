import psycopg2


def GetDb():
        return psycopg2.connect(host="localhost", dbname="books", user="admin", password="test_password")
