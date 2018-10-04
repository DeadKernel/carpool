import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from carpool.auth import *
from carpool.db1 import connector
from carpool.auth import login_required

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
            return('Okay')
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
            "Date":date,
            "Time":date,
            "Distance_flex":None,
            "Time_flex":None,
            "No_of_persons":None
        }
        db,conn1 = connector()
        if request.form['Ride'] == 'Book Ride':
            ride= db.bookride
            ride.insert_one(routeinfo)
            return ("okay")

        if request.form['Ride'] == 'Offer Ride':
            ride= db.offerride
            ride.insert_one(routeinfo)
            #print(session['username'])
            return redirect(url_for('insidelogin.update'))

    return render_template('AfterLogin/Begin.html')
