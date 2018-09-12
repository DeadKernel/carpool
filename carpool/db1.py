from pymongo import MongoClient
import urllib.parse


def connector():
    # connect to monogdb as carpooler user
    username = urllib.parse.quote_plus('carpooler')
    password = urllib.parse.quote_plus('makingclean')
    uri='mongodb://%s:%s@127.0.0.1' % (username, password)
    client = MongoClient(uri)
    db = client.carpool #use carpool database
    return db,client
