import urllib.request
import json
import ast
from carpool.db1 import connector
from carpool.auth import login_required,session_name
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from datetime import datetime as dt
from math import ceil

bp = Blueprint('afterbookride', __name__, url_prefix='/bookride')

@bp.route('/bookprocess', methods=['GET', 'POST'])
@login_required
def showRides():
    passroute =ast.literal_eval(session['routeinfo'])
    #passroute= (passroute)
    print(passroute)
    db,conn1=connector()
    rides= db.offerride
    originPassenger = passroute['Start']
    destinationPassenger = passroute['End']
    base = 'https://maps.googleapis.com/maps/api/directions/json?'
    displayrides = []
    waypointsList =[]
    api_key ='AIzaSyDsDBCYF8CBpzPI4kE7PxqtuQBoLVv2Crc'
     # request to calculate cost
    requestCost = base + urllib.parse.urlencode({'origin':originPassenger, 'destination':destinationPassenger,'key':api_key})
    responseCost= urllib.request.urlopen(requestCost).read()
    directionCost = json.loads(responseCost.decode('utf-8'))
    routesCost = directionCost['routes']
    legsCost = routesCost[0]['legs']
    distanceCost = []
    for index in range(len(legsCost)):
        distanceCost.append(legsCost[index]['distance']['value'])
    total_distance_cost = float(sum(distanceCost))/1000
    totalCost = 15
    if total_distance_cost>1:
        totalCost+= (total_distance_cost-1)*5

    for document in rides.find({"End":destinationPassenger}):
        a = dt.strptime(document['Time'],"%m/%d/%Y %I:%M %p")
        b = dt.strptime(passroute['Time'], "%m/%d/%Y  %I:%M %p")
        if a>b:
                continue
        originDriver = document['Start']
        destinationDriver =document['End']
        originalWaypoints=document['waypoints']
        print("Toshal")
        requestChecker = base + urllib.parse.urlencode({'origin':originDriver, 'destination':originPassenger, 'waypoints':originalWaypoints,'key':api_key})
        responseCheck= urllib.request.urlopen(requestChecker).read()
        directionCheck = json.loads(responseCheck.decode('utf-8'))
        routesCheck = directionCheck['routes']
        legsCheck = routesCheck[0]['legs']
        distanceCheck = []
        durationCheck = []
        for index in range(len(legsCheck)):
            distanceCheck.append(legsCheck[index]['distance']['value'])
            durationCheck.append(legsCheck[index]['duration']['value'])
        total_distance_check = float(sum(distanceCheck))/1000
        total_time_check = timedelta(seconds=sum(durationCheck))
        startDriver = a
        startPassenger = b
        print("Toshal")
        if startDriver+total_time_check > startPassenger:
            continue
        else:
            addedWaypoints =originalWaypoints+'|'+originPassenger

            requestDriver = base + urllib.parse.urlencode({'origin':originDriver, 'destination':destinationDriver, 'waypoints':originalWaypoints,'key':api_key})
            requestTotal = base + urllib.parse.urlencode({'origin':originDriver, 'destination':destinationDriver, 'waypoints':addedWaypoints, 'key':api_key})
            responseOne= urllib.request.urlopen(requestDriver).read()
            responseTwo = urllib.request.urlopen(requestTotal).read()

            directionOne = json.loads(responseOne.decode('utf-8'))
            directionTwo = json.loads(responseTwo.decode('utf-8'))

            #print(directionOne)
            #print(directionTwo)

            routesOne = directionOne['routes']
            legsOne = routesOne[0]['legs']
            distanceOne = []
            durationOne = []
            for index in range(len(legsOne)):
                distanceOne.append(legsOne[index]['distance']['value'])
                durationOne.append(legsOne[index]['duration']['value'])

            total_distance_one = float(sum(distanceOne))/1000
            total_distance_one =round(total_distance_one,1)
            total_time_one = timedelta(seconds=sum(durationOne))
            totalDurationOne = sum(durationOne)
            print(total_distance_one,'km')
            print(str(total_time_one))

            routesTwo = directionTwo['routes']
            legsTwo = routesTwo[0]['legs']
            distanceTwo = []
            durationTwo = []
            for index in range(len(legsTwo)):
                distanceTwo.append(legsTwo[index]['distance']['value'])
                durationTwo.append(legsTwo[index]['duration']['value'])

            total_distance_two = float(sum(distanceTwo))/1000
            total_distance_two =round(total_distance_two,1)
            total_time_two = timedelta(seconds=sum(durationTwo))
            totalDurationTwo= sum(durationTwo)
            print(total_distance_two,'km')
            print(str(total_time_two))

            distanceFlex =document['Distance_flex']
            timeFlex = document['Time_flex']
            newDistanceFlex = round((total_distance_two-total_distance_one)/total_distance_one*100)
            newTimeFlex = round((totalDurationTwo-totalDurationOne)/totalDurationOne*100)
            if newDistanceFlex>distanceFlex:
                print("rejected")
                continue
            elif newTimeFlex>timeFlex:
                print("rejected")
                continue

            print(total_distance_two,'km')
            print(str(total_time_two))
            #section after validation
            totalCost += (total_distance_two - total_distance_one)*5
            findUsers= db.users
            getUserInfo =findUsers.find_one({'mailid':document['mailid']})
            print(getUserInfo)

            tempdisplay={}
            tempdisplay['mailid']=getUserInfo['mailid']
            tempdisplay['name']=getUserInfo['name']
            tempdisplay['end']=document['End']
            tempdisplay['start']=document['Start']
            tempdisplay['phno']=getUserInfo['phno']
            tempdisplay['model']=getUserInfo['car_details'][0]['model']
            tempdisplay['plate']=getUserInfo['car_details'][0]['plate']
            tempdisplay['cost']= ceil(totalCost)
            tempdisplay['time']=document['Time']

            #print(tempdisplay)
            displayrides.append(tempdisplay)
            waypointsList.append(addedWaypoints)

    if request.method=='POST':
        rideOption=int(request.form['rides'])
        bookedRides=db.bookedRides
        bookedRides.insert_one({'mailid':session_name(),'route':displayrides[rideOption],'start':originPassenger})
        rides.find_one_and_update({'mailid':displayrides[rideOption]['mailid'],"Time":displayrides[rideOption]['time']},{'$inc':{'No_of_persons':-1}})
        rides.find_one_and_update({'mailid':displayrides[rideOption]['mailid'],"Time":displayrides[rideOption]['time']},{'$set':{'waypoints':waypointsList[rideOption]}})
        rides.find_one_and_delete({'mailid':displayrides[rideOption]['mailid'],'No_of_persons':0})
        return redirect(url_for('insidelogin.passengercode'))



                #waypoints.append('Swargate')
                #waypoints.append('Baner')


    return render_template('AfterLogin/disprides.html',displayrides=displayrides)
