import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from carpool.db1 import connector

bp = Blueprint('insidelogin', __name__, url_prefix='/loggedin')
@bp.route('/getstarted', methods=('GET', 'POST'))
def takeRoute():
    if request.method == 'POST':
        place1 = request.form['Start']
        place2 = request.form['End']
        date = request.form['Date']
        routeinfo = {
            "Start":place1,
            "End":place2,
            "Date":date,
            "Time":date
        }
        db,conn1 = connector()
        if request.form['Ride'] == 'Book Ride':
            ride= db.bookride
            ride.insert_one(routeinfo)
            return ("okay")

        if request.form['Ride'] == 'Offer Ride':
            ride= db.offerride
            ride.insert_one(routeinfo)
            return ("okay")



        """error = None
        if not username:
            return('1')
        elif not password:
            return('2')
        elif not email:
            return('3')
        elif not phnumber:
            return('4')
        elif confpass != password or  not password :
            return('5')
        elif checkduplicate is not None:
             return('User {} is already registered.'.format(username))
        if error is None:
            user= db.users
            user.insert_one(userinfo)
            return ("okay")
            print("Toshal")
        flash(error)"""
    return render_template('AfterLogin/Begin.html')
@bp.route('/offride', methods=('GET', 'POST'))
def offRide():
    return render_template('AfterLogin/OfferRide.html')
