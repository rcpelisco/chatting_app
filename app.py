from flask import Flask , session, render_template, request, redirect, g, url_for, jsonify
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, emit
from DatabaseManager import *
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretparabibo'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'chat_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
socketio = SocketIO(app)

dummy_contacts = [
    {
        'contact_name': 'RC', 
        'time_last_message': 
        '1 min', 'last_message': 'I was down. My dreams were wearing thin ...', 
        'is_active': 'active'
    },
]

online = {

}

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']
    else:
        session['user'] = None

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='Page not Found')

@app.route('/messages/')
@app.route('/messages/<username>')
def messages(username=None):
    contacts = DatabaseManager.get_contacts(mysql, g.user['user_id'])
    if username == None and len(contacts) > 0:
        username = contacts[0]['username']
    elif len(contacts) < 1:
        return render_template('index.html', 
            title='Message',
            contacts=contacts,
            user=g.user['first_name'],
            active_contact='No Friends yet',
            messages='',
            files_shared='')
    active_contact = DatabaseManager.get_user(mysql, username)
    messages = DatabaseManager.get_messages(mysql, g.user['user_id'], username)
    return render_template('index.html', 
        title='Message',
        contacts=contacts,
        user=g.user,
        active_contact={'name': active_contact['first_name'] + ' ' + active_contact['last_name'], 
            'username': username},
        messages=messages,
        files_shared='')

@app.route('/')
def index():
    if session['user'] == None:
        return render_template('login.html')
    return redirect(url_for('messages'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/server/logout')
def logout():
    session.pop('user', None)
    return redirect('./')

@app.route('/server/login', methods=['POST'])
def server_login():
    username = request.form['username']
    password = request.form['password']
    result = DatabaseManager.login(mysql, username, password)
    if len(result) > 0:
        session['user'] = result[0]
        return json.dumps(result[0])
    return 'false'

@app.route('/server/register', methods=['POST'])
def server_register():
    user = request.form
    DatabaseManager.register(mysql, user)
    return redirect('/')

@app.route('/server/search', methods=['POST'])
def server_search():
    user_query = request.form['query']
    result = jsonify(DatabaseManager.search(mysql, g.user['user_id'], user_query))
    return result

@app.route('/server/add_contact', methods=['POST'])
def server_add_contact():
    username = request.form['username']
    DatabaseManager.add_contact(mysql, g.user['user_id'], username)
    return "0"

@socketio.on('new message')
def handle_message(msg):
    print(msg)
    if(msg['recipient'] in online):
        recipient_sid = online[msg['recipient']]
        socketio.emit('send message', msg, room=recipient_sid)        
        
    DatabaseManager.send_message(mysql, 
        msg['message'], 
        msg['sender'], 
        msg['recipient']
    )
    return msg

@socketio.on('login')
def handle_online(data):
    data = json.loads(data)
    online[data['username']] = request.sid
    print(online)
    return data['username']

@socketio.on('update username sid')
def update_username_sid(username):
    online[username] = request.sid
    print('update username sid')
    print(online)

@socketio.on('logout')
def handle_logout(username):
    online.pop(username)
    print('logout')
    print(online)

def remove_user(d, key):
    r = dict(d)
    print(r)
    del r[key]
    return r    

if __name__ == '__main__':
    socketio.run(app, debug=True)
