from carpool.db1 import connector
import datetime

def automaticDelete():
    db,conn1 = connector()
    currentTime = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
    print(currentTime)
    availableRides = db.offerrides
    documentstoTransact =availableRides.find({'Time':currentTime})
