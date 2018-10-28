from carpool.db1 import connector
import datetime
from math import ceil
def automaticDelete():
    db,conn1 = connector()
    currentTime = datetime.datetime.now()-datetime.timedelta(minutes=11)
    currentTime=currentTime.strftime("%m/%d/%Y %H:%M")
    print("Deleting Rides Which are getting active")
    print(currentTime)
    availableRides = db.offerride
    documentstoTransact =list(availableRides.find({'Time':{'$lt':currentTime}}))
    availableRides.delete_many({'Time':{'$lt':currentTime}})
    print(documentstoTransact)
    if documentstoTransact :
        bookedRides = db.bookedRides
        for document in documentstoTransact:
            ridestoTransfer=[]
            ridestoTransfer.extend(list(bookedRides.find({'route.mailid':document['mailid'],'route.time':document['Time']})))
            if not ridestoTransfer:
                findUsers= db.users
                getUserInfo =findUsers.find_one({'mailid':document['mailid']})
                tempdisplay={}
                tempdisplay['mailid']=getUserInfo['mailid']
                tempdisplay['name']=getUserInfo['name']
                tempdisplay['end']=document['End']
                tempdisplay['start']=document['Start']
                tempdisplay['phno']=getUserInfo['phno']
                tempdisplay['model']=getUserInfo['car_details'][0]['model']
                tempdisplay['plate']=getUserInfo['car_details'][0]['plate']
                tempdisplay['cost']= ceil(0)
                tempdisplay['time']=document['Time']
                tempdisplay['code']=document['code']
                activeRides = db.activeRides
                makeBooked = {'mailid':"-",'route':tempdisplay,'start':"-"}
                activeRides.insert_one({'trip':makeBooked})
                print(makeBooked)
