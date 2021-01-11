#from starcast import app as application
from geniusapp import app as application
#from gevent import monkey

if __name__ == "__main__":

    #monkey.patch_all()
    application.run(debug=True,port=8000,use_reloader=False)
