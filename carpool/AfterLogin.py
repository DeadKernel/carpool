import functools
import random
import string
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import json
import time
from sinchsms import SinchSMS
from werkzeug.security import check_password_hash, generate_password_hash
from carpool.db1 import connector
from carpool.auth import login_required,session_name
from carpool.transaction import *
from bson.code import Code
bp = Blueprint('insidelogin', __name__, url_prefix='/auth')
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))
@bp.route('/admin',methods=('GET','POST'))
@login_required
def admin():
        db,conn1 = connector()
        user=db.users
        count1=user.find().count()
        price=db.activeRides
        cost=price.aggregate([{'$group': {'_id': '','cost': { '$sum': '$trip.route.cost' }}},{'$project':{'_id': 0,'cost': '$cost'}}])
        user_rating=db.contact
        star=[]
        star.append(user_rating.find().count())
        star.append(user_rating.find({"star":5}).count())
        star.append(user_rating.find({"star":4}).count())
        star.append(user_rating.find({"star":3}).count())
        star.append(user_rating.find({"star":2}).count())
        star.append(user_rating.find({"star":1}).count())
        print(cost)
        admin=db.base_price
        admin_pass=admin.find_one()
        return render_template('AfterLogin/admin_prof.html',admin=admin_pass,cost=cost,count1=count1,star=star)
@bp.route('/admincontrol',methods=('GET','POST'))
@login_required
def admincontrol():
    db,conn1 = connector()
    user=db.users
    if request.method=='POST':
        del_user=request.form['username']
        user_check=user.find_one({'mailid':del_user})
        if user_check is None:
            return render_template('AfterLogin/admin_delete.html',exists=0)
        user.find_one_and_delete({'mailid':del_user})
    return render_template('AfterLogin/admin_delete.html')


@bp.route('/offerRide',methods=('GET','POST'))
@login_required
def update():
    if request.method=='POST':
            mailid1= session_name()
            distance=int(request.form['slider1'])
            time=100-distance
            persons=int(request.form['seats'])

            db,conn1 = connector()
            ride= db.offerride
            ride.update_many(
            {"mailid": mailid1,"Time":session.get('time',None)},
            {'$set': { "Distance_flex":distance,
                    "Time_flex":time,
                    "No_of_persons":persons}
            }
            )
            return redirect(url_for('insidelogin.offerhistory'))
    return render_template('AfterLogin/offerRide.html')

@bp.route('/cardeets',methods=['GET','POST'])
@login_required
def cardeets():
        if request.method=='POST':
                mailid1= session_name()
                plate=request.form['plate']
                model=request.form['model']
                license=request.form['license']

                db,conn1 = connector()
                user= db.users
                admin=db.base_price
                admin.update({},{'$inc':{'No_of_offers':1}})
                user.update_many(
                {"mailid": mailid1},
                {'$set': { "car_details.0.plate":plate,
                        "car_details.0.model":model,
                        "car_details.0.license":license}
                }
                )
                return redirect(url_for('insidelogin.profile'))
        return render_template('auth/cardeets.html')
@bp.route('/begin', methods=['GET', 'POST'])
@login_required
def takeRoute():
    if request.method == 'POST':
        mailid1 = session_name()
        place1 = request.form['Start']
        place2 = request.form['End']
        date = request.form['Date']
        code=id_generator()
        routeinfo = {
            "mailid":mailid1,
            "Start":place1,
            "End":place2,
            "Time":date,
            "Distance_flex":None,
            "Time_flex":None,
            "No_of_persons":None,
            "waypoints":"",
            "code":code
        }
        db,conn1 = connector()

        session['routeinfo']=str(routeinfo)
        if request.form['Ride'] == 'Book Ride':
            return redirect(url_for('afterbookride.showRides'))
            print("ComeBack")
        elif request.form['Ride'] == 'Offer Ride':
            user=db.users
            print("In offer Ride")
            car=user.find({'mailid':mailid1},{'_id':0,'car_details':1})
            plate=car[0]['car_details'][0]['plate']
            print (plate)
            if plate == None:
                return render_template('AfterLogin/Begin.html',check=0)
            ride= db.offerride
            ride.insert_one(routeinfo)
            #print(session['username'])
            session['time'] = routeinfo['Time']
            print("Going to slider")
            return redirect(url_for('insidelogin.update'))

    return render_template('AfterLogin/Begin.html')



@bp.route('/drivercode', methods=['GET', 'POST'])
@login_required
def drivercode():
    client = SinchSMS('826e4cc7-3f6e-4fa2-a9a6-176ccec744c2','iDeaWwa6S0yMxrTt4ohqcA==')
    db,conn1=connector()
    mailid=session_name()
    booked=db.bookedRides
    rides=db.offerride
    codeValue=session.get('code',None)
    starttime=rides.find_one({'mailid':mailid,'code':codeValue})
    passengerRides=[]
    for document in booked.find({'route.mailid':mailid,'route.time':starttime['Time']}):
        passengerRides.append(document)
    if request.method == 'POST':
        phno=booked.find({'route.mailid':mailid})
        for phno in booked.find({'route.mailid':session_name()}):
            phno1=phno['route']['phno']
            print (phno1)
            number = '+91' +phno1
            print(number)
        number = '+918237822234'
        message = 'Your Ride has started .'
        print("ABC")
        client.send_message(number,message)
        return redirect(url_for('insidelogin.profile'))
    return render_template('AfterLogin/congrat.html',code=codeValue,time=starttime['Time'],passengerRides = passengerRides)

@bp.route('/passengercode',methods=['GET','POST'])
@login_required
def passengercode():
    mailid=session_name()
    db,conn1=connector()
    activeRides=db.activeRides
    bookedRides=db.bookedRides
    if request.method=='POST':
        code=request.form['code1']
        match=bookedRides.find_one({'route.code':code})
        if match is None:
            return render_template('AfterLogin/yay.html',match=0)
        else:
            passengerActiveRide=bookedRides.find_one({'mailid':match['mailid'],'mailid':mailid})
            activeRides.insert_one({'trip':passengerActiveRide})
            bookedRides.find_one_and_delete({'mailid':match['mailid'],'mailid':mailid})
            return redirect(url_for('insidelogin.profile'))
    return render_template('AfterLogin/yay.html')
@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    mailid=session_name()
    db,conn1=connector()
    users = db.users
    user_prof = users.find_one({'mailid' : mailid })
    car=users.find({'mailid':mailid},{'_id':0,'car_details':1})
    plate=car[0]['car_details'][0]['plate']
    model=car[0]['car_details'][0]['model']
    license=car[0]['car_details'][0]['license']
    user_details = {
        'Name':user_prof['name'],
        'email':mailid,
        'Mobile_No':user_prof['phno'],
        'Car_Number':plate,
        'Car_Model':model,
        'licence_Number':license
        }
    return render_template('AfterLogin/index.html',user=user_details)

@bp.route('/mytrips',methods=['GET','POST'])
@login_required
def mytrips():
    db,conn1=connector()
    bookedRides=db.bookedRides
    passengerRides=[]
    for document in bookedRides.find({'mailid':session_name()}):
        passengerRides.append(document)
    if request.method=='POST':
        return redirect(url_for('insidelogin.passengercode'))
    return render_template('AfterLogin/mytrips.html',passengerRides=passengerRides)
@bp.route('/offerhistory',methods=['GET','POST'])
@login_required
def offerhistory():
    db,conn1=connector()
    activeRides=db.activeRides
    rides=db.offerride
    history1=[]
    for document in rides.find({'mailid':session_name()}):
        history1.append(document)
    if request.method=='POST':
        print (history1)
        offerOption=int(request.form['offeroption'])
        code=history1[offerOption]['code']
        session['code']=code
        return redirect(url_for('insidelogin.drivercode'))
    return render_template('AfterLogin/offerhistory.html',history1=history1)
@bp.route('/ridehistory',methods=['GET','POST'])
@login_required
def ridehistory():
    db,conn1=connector()
    activeRides=db.activeRides
    rideHistory=[]
    for document in activeRides.find({'trip.mailid':session_name()}):
        rideHistory.append(document)
    for document1 in activeRides.find({'trip.route.mailid':session_name()}):
        rideHistory.append(document1)
    print (rideHistory)
    return render_template('AfterLogin/history.html',ridehistory=rideHistory)
