import urllib.request
import json
from carpool.db1 import connector
from carpool.auth import login_required,session_name
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

bp = Blueprint('afterbookride', __name__, url_prefix='/bookride')

@bp.route('/bookprocess', methods=['GET', 'POST'])
@login_required
def showRides(passroute):
    db,conn1=connector()
    rides= db.offerride
    originPassenger = passroute['Start']
    destinationPassenger = passroute['End']
    base = 'https://maps.googleapis.com/maps/api/directions/json?'
    api_key ='AIzaSyDsDBCYF8CBpzPI4kE7PxqtuQBoLVv2Crc'
    for document in rides.find({"End":destinationPassenger}):
                originDriver = document['Start']
                destinationDriver =document['End']
                originalWaypoints=document['waypoints']

                requestDriver = base + urllib.parse.urlencode({'origin':originDriver, 'destination':destinationDriver, 'waypoints':originalWaypoints,'key':api_key})
                responseOne= urllib.request.urlopen(requestDriver).read()
                directionOne = json.loads(responseOne)
                

                if document['Time'] > passroute['Time']:
                    continue
                else:
                    addedWaypoints =originalWaypoints+'|'+originPassenger
                    requestDriver = base + urllib.parse.urlencode({'origin':originDriver, 'destination':destinationDriver, 'waypoints':originalWaypoints,'key':api_key})
                    requestTotal = base + urllib.parse.urlencode({'origin':originDriver, 'destination':destinationDriver, 'waypoints':addedWaypoints, 'key':api_key})
                    responseOne= urllib.request.urlopen(requestDriver).read()
                    responseTwo = urllib.request.urlopen(requestTotal).read()

                    directionOne = json.loads(responseOne)
                    directionTwo = json.loads(responseTwo)

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
                    total_time_one = timedelta(seconds=sum(durationOne))
                    print(round(total_distance_one,1),'km')
                    print(str(total_time_one))

                    routesTwo = directionTwo['routes']
                    legsTwo = routesTwo[0]['legs']
                    distanceTwo = []
                    durationTwo = []
                    for index in range(len(legsTwo)):
                        distanceTwo.append(legsTwo[index]['distance']['value'])
                        durationTwo.append(legsTwo[index]['duration']['value'])

                    total_distance_two = float(sum(distanceTwo))/1000
                    total_time_two = timedelta(seconds=sum(durationTwo))
                    print(round(total_distance_two,1),'km')
                    print(str(total_time_two))

                #waypoints.append('Swargate')
                #waypoints.append('Baner')

    return render_template('AfterLogin/Begin.html')
