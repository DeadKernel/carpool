from carpool.db1 import connector
import datetime

def automaticDelete():
    db,conn1 = connector()
    currentTime = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
    print("Deleting Rides Which are getting active")
    print(currentTime)
    availableRides = db.offerride
    documentstoTransact =list(availableRides.find({'Time':{'$lt':currentTime}}))
    availableRides.delete_many({'Time':{'$lt':currentTime}})
    print(documentstoTransact)
    if documentstoTransact :
        bookedRides = db.bookedRides
        ridestoTransfer=[]
        for document in documentstoTransact:
            ridestoTransfer.extend(list(bookedRides.find({'route.mailid':document['mailid'],'route.time':document['Time']})))

        bookedRides.delete_many({'route.time':{'$lt':currentTime}})
        print(ridestoTransfer)
        activeRides=db.activeRides
        for ride in ridestoTransfer:
            activeRides.insert_one({'trip':ride})

        #bookedRides.insert_many(documentstoTransact);
