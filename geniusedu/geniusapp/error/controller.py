from geniusapp import app
from flask import current_app,render_template

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error/404.html'), 404


@app.errorhandler(401)
def custom_401(error):
    return 'Login is required.'
    # return ('<Why access is denied string goes here...>', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})


@app.errorhandler(500)
def custom_500(error):
    return render_template('error/500.html')