from geniusapp import app
import datetime


def get_date(dateFormat="%d-%m-%Y", addDays=0):

    timeNow = datetime.datetime.now()
    if (addDays!=0):
        anotherTime = timeNow + datetime.timedelta(days=addDays)
    else:
        anotherTime = timeNow

    return anotherTime.strftime(dateFormat)