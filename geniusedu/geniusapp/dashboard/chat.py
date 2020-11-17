from threading import Lock
from flask import current_app, render_template,session,request
from geniusapp import app
import eventlet
from flask_socketio import SocketIO, emit, join_room, leave_room,close_room, rooms, disconnect

eventlet.monkey_patch()
async_mode = None
# socketio = SocketIO(app, async_mode=async_mode,cors_allowed_origins='*',reconnection=True,reconnectionDelay=6000,request_timeout=10000)
socketio = SocketIO(app, async_mode = 'eventlet', cors_allowed_origins='*',reconnection=True,reconnectionDelay=6000,request_timeout=10000)
thread = None
thread_lock = Lock()


def background_thread():
    count = 0
    while True:
        socketio.sleep(5)
        count += 1

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',{'chat_msg': message['chat_msg'], 'count': session['receive_count']})


# @socketio.on('join', namespace='/test')
# def join(message):
#     join_room(message['room'])
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     #emit('my_response',{'chat_msg': 'In rooms: ' + ', '.join(rooms()),'count': session['receive_count']})
#     message="{} ".format(message['student_name'])
#     emit('my_response2',{'chat_msg': message}, broadcast=True)

@socketio.on('join', namespace='/test')
def join(message):
    username =  message['student_name']
    room = message['room'] 
    join_room(room)   
    emit('my_response2',{'chat_msg': username}, broadcast=True, room=room)


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',{'sid':request.sid,'show_id':message['show_id'],'user_id':message['user_id'],'user_type':message['user_type'],'sender_id':message['sender_id'],'receiver_id':message['receiver_id'],'chat_msg': message['chat_msg'], 'count': session['receive_count']}, room=message['room'])

@socketio.on('ban',namespace='/test')
def ban(message):
    sid = message['sid']
    emit('message',{'msg':'You are banned.','status':'ban'},room=sid)

@socketio.on('broadmsg',namespace='/test')
def broadmsg(message):
    msg = message['message']
    emit('broad_message',{'msg':msg}, broadcast=True, room=message['room'])


@socketio.on('sendfile',namespace='/test')
def broadmsg(message):
    msg = message['message']
    emit('send_file_msg',{'msg':msg,'user_id':message['user_id'],'user_type':message['user_type']}, broadcast=True, room=message['room'])

@socketio.on('left', namespace='/test')
def left(message):
    room = message['room']
    msg = message['msg']
    leave_room(room)
    emit('broad_message', {'msg':msg}, broadcast=True, room=room)

socketio.run(app)