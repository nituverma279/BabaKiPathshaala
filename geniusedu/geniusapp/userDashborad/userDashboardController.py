from geniusapp import app,db,csrf,config,login_manager
from flask import current_app,render_template,url_for, abort,request,make_response,flash,redirect,jsonify,session,json,send_from_directory


@app.route('/userDashboard')
def userDashboard():
    # return make_response(render_template('dashboard/usersBoard/dashboard.html'))
    try:
         return render_template('home/home.html')
    except Exception as e:
         app.logger.error(str(e))
         return abort(500)