from pymongo import MongoClient
import urllib.parse


def connector():

    uri='mongodb://AdityaPadwal:carpool123@ds115193.mlab.com:15193/carpool'
    client = MongoClient(uri)
    db = client.carpool #use carpool database
    return db,client
