import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash
from carpool.db1 import connector
from carpool.auth import login_required,session_name
from carpool.transaction import *

bp = Blueprint('insidelogin', __name__, url_prefix='/auth')

@bp.route('/offerRide',methods=('GET','POST'))
@login_required
def update():
    if request.method=='POST':
            mailid1= session_name()
            distance=request.form['slider1']
            time=100-int(distance)
            persons=request.form['seats']

            db,conn1 = connector()
            ride= db.offerride
            ride.update_many(
            {"mailid": mailid1},
            {'$set': { "Distance_flex":distance,
                    "Time_flex":time,
                    "No_of_persons":persons}
            }
            )
            return redirect(url_for('insidelogin.profile'))
    return render_template('AfterLogin/offerRide.html')

@bp.route('/begin', methods=['GET', 'POST'])
@login_required
def takeRoute():
    if request.method == 'POST':
        mailid1 = session_name()
        place1 = request.form['Start']
        place2 = request.form['End']
        date = request.form['Date']
        routeinfo = {
            "mailid":mailid1,
            "Start":place1,
            "End":place2,
            "Time":date,
            "Distance_flex":None,
            "Time_flex":None,
            "No_of_persons":None,
            "waypoints":""
        }
        db,conn1 = connector()
        if request.form['Ride'] == 'Book Ride':
            showRides(routeinfo)

        if request.form['Ride'] == 'Offer Ride':
            ride= db.offerride
            ride.insert_one(routeinfo)
            #print(session['username'])
            return redirect(url_for('insidelogin.update'))

    return render_template('AfterLogin/Begin.html')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    mailid=session_name()
    db,conn1=connector()
    users = db.users
    user_prof = users.find_one({'mailid' : mailid })
    user_details = {
        'Name':user_prof['name'],
        'email':mailid,
        'Mobile_No':user_prof['phno'],
        'Car_Number':user_prof['car_details'],
        'Car_Model':user_prof['car_details'][0]
        #'licence_Number':user_prof['car_details'][2]
    }
    return render_template('AfterLogin/index.html',user=user_details)
