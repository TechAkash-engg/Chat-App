from bson.json_util import dumps
from flask import Flask, render_template, Response, request, url_for, redirect, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room
from pymongo.errors import DuplicateKeyError
from werkzeug.utils import secure_filename
import base64
import os,io
from datetime import datetime
from time import strftime
from pymongo import MongoClient
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytz
import smtplib
from flask_headers import headers
from flask_jwt_extended import create_access_token, decode_token, JWTManager
from return_time import return_expiry_time
import cryptocode
import itertools
import dynamic_online
dynamic_online

from db import get_user, save_user, save_room, add_room_members, get_rooms_for_user, get_room, is_room_member, \
    get_room_members, is_room_admin, update_room, remove_room_members, save_message, get_messages, get_group_id, \
    get_user_id, delete_room, check_ids, get_username, get_username_count, make_room_admin, get_email, get_usernames,user_not_in_room, \
    get_mailid,get_group_name, get_object_id_from_email, get_user_mail_from_object_id, update_password_for_user, get_rooms_for_userpic, \
    user_status_offline, user_status_online,user_status_offline2, user_status_online2, member_count_of_room,  return_online_members


app = Flask(__name__)
app.secret_key = 'my_secret_key'
socketio = SocketIO(app)
jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

PEOPLE_FOLDER = os.path.join('static','uploads')
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/firebase-messaging-sw.js')
@headers({"Content-Type":"application/javascript; charset=utf-8"})
def send_js():
    return send_from_directory('static', 'firebase-messaging-sw.js', cache_timeout=0)


def upload_image(room_id):
    if 'file' not in request.files:   
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
#         print('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(filename)
        imgss = filename
        imgs = Image.open(imgss).convert("RGB")
        img = imgs.resize((300,300))
        npImage = np.array(img)
        h, w = img.size
        alpha = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([(0, 0), (h, w)], 0, 360, fill=255, outline="white")
        npAlpha = np.array(alpha)
        npImage = np.dstack((npImage, npAlpha))
        ist = pytz.timezone('Asia/Kolkata')
        t = datetime.now(ist).strftime("%Y-%m-%d %H-%M")
        im = Image.fromarray(npImage)
        pic= im.resize((56,56))
        pic.save("static/uploads/" + str(t) +str(room_id) + '.png')
        imageFile = open("static/uploads/" + str(t) +str(room_id) + '.png', 'rb')
        z = base64.b64encode(imageFile.read())
        connection = MongoClient("mongodb+srv://PreethamGS:shettigar15@cluster0-3kawi.mongodb.net/test?retryWrites=true&w=majority")
        db = connection['ChatDB']
        collection = db['rooms']
        collection.update_one({'_id': room_id}, {"$push": {'Group_pic': z}})
        imageFile.close()
#         print("group pic done")

    else:    
        return redirect(request.url)


def profile_pic(email):
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
#         print('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(filename)
        imgss = filename
        imgs = Image.open(imgss).convert("RGB")
        img = imgs.resize((300,300))
        npImage = np.array(img)
        h, w = img.size
        alpha = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([(0,0), (h,w)], 0, 360,fill = 255, outline = "white")
        npAlpha = np.array(alpha)
        npImage = np.dstack((npImage, npAlpha))
        ist = pytz.timezone('Asia/Kolkata')
        t = datetime.now(ist).strftime("%Y-%m-%d %H-%M")
        im = Image.fromarray(npImage)
        prof=im.resize((56,56))
        prof.save("static/uploads/" + str(email) + '.png', optimize=True, quality=90)
        imageFile = open("static/uploads/" + str(email) + '.png', 'rb')
        z = base64.b64encode(imageFile.read())
        connection = MongoClient("mongodb+srv://PreethamGS:shettigar15@cluster0-3kawi.mongodb.net/test?retryWrites=true&w=majority")
        db = connection['ChatDB']
        collection = db['users']
        collection.update_one({"_id": email}, {"$push": {'Profile_pic': z}})
        imageFile.close()
#         print("profile pic done")
    else:
        return redirect(request.url)


def edit_pic(room_name):
    if 'file' not in request.files:
#         flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
#         print('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(filename)
        imgss = filename
        imgs = Image.open(imgss).convert("RGB")
        img = imgs.resize((300,300))
        npImage = np.array(img)
        h, w = img.size
        alpha = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([(0,0), (h,w)], 0, 360,fill = 255, outline = "white")
        npAlpha = np.array(alpha)
        npImage = np.dstack((npImage, npAlpha))
        ist = pytz.timezone('Asia/Kolkata')
        t = datetime.now(ist).strftime("%Y-%m-%d %H-%M")
        im = Image.fromarray(npImage)
        editpic=im.resize((56,56))
        editpic.save("static/uploads/" + str(t)+ str(room_name) + '.png')
        imageFile = open("static/uploads/" + str(t) + str(room_name) + '.png', 'rb')
        z = base64.b64encode(imageFile.read())
        connection = MongoClient("mongodb+srv://PreethamGS:shettigar15@cluster0-3kawi.mongodb.net/test?retryWrites=true&w=majority")
        db = connection['ChatDB']
        collection = db['rooms']
        roomid = get_group_id(room_name)
        collection.update_one({"_id": roomid}, {"$unset": {'Group_pic': 1}})
        collection.update_one({"_id": roomid}, {"$push": {'Group_pic': z}})
        imageFile.close()
#         print("updated group pic uploaded")
    else:
        return redirect(request.url)


@app.route('/')
def first():
    #if current_user.is_authenticated:
        #return redirect(url_for('home'))
    return redirect(url_for('login'))

def lis_img():
    a = []
    allimg = []
    rooms = []
    if current_user.is_authenticated:
        rooms = get_rooms_for_user(current_user.username)
        users = get_usernames()
        a = get_rooms_for_userpic(current_user.username)
        for ids in a:
            li = get_room(ids['_id']['room_id'])
            id = li['_id']
#             print(id)
            try:
                list = li['name']
                lis = li['Group_pic']
                def stringToRGB(base64_string):
                    imgdata = base64.b64decode(str(base64_string))
                    image = Image.open(io.BytesIO(imgdata))
                    return image
                a = lis[0]
                k = a.decode('utf-8')
                string = k
                arr = bytes(string, 'utf-8')
                base64.decodebytes(arr)
                pi = stringToRGB(string)
                g_nm = get_group_name(id)
                pi.save("static/" + str(id) + '.png')
                allimg.append(str(id) + '.png')
            except:
                allimg.append('grp_img.png')
#         print(allimg)
        return allimg,rooms,users

@app.route('/index', methods=['GET', 'POST'])
def home():
    funct = lis_img()
    allimg = funct[0]
    rooms = funct[1]
    users = funct[2]
    sol=zip(allimg,rooms)
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        usernames = request.form.getlist('members')
        if len(room_name) and len(usernames):
            members = []
            for username in usernames:
                user_id = get_user_id(username)
                members.append([user_id, username])
            room_id = save_room(room_name, current_user.username, members)
            try:
                upload_image(room_id)
            except:
                pass
            print('create room accessed')
            if current_user.username in usernames:
                usernames.remove(current_user.username)
            add_room_members(room_id, room_name, usernames, current_user.username)
            return redirect(url_for('view_room', room_id=room_id))
        else:
            return render_template('index.html',  user_id=current_user.username+current_user.user_id)
        
    connection = MongoClient('mongodb+srv://PreethamGS:shettigar15@cluster0-3kawi.mongodb.net/test?retryWrites=true&w=majority')
    db = connection['ChatDB']
    collection = db['users']
    usernames = current_user.username
    user_status_online(usernames)
    user_status_online2(usernames)
    collections = db['room_members']
    p = collections.find_one({"_id.username": usernames})
    try:
        q = p['is_online']
#         print(q)
    except:
        pass
    data = {'username': usernames}
    
    try:
        mail = get_mailid(current_user.username)
        y = collection.find_one({"_id": mail})
        x = y['Profile_pic']

        def stringToRGB(base64_string):
            imgdata = base64.b64decode(str(base64_string))
            image = Image.open(io.BytesIO(imgdata))
            return image

        a = x[0]
        k = a.decode('utf-8')
        string = k
        arr = bytes(string, 'utf-8')
        base64.decodebytes(arr)
        pi = stringToRGB(string)
        pi.save("static/uploads/" + str(mail) +'.png', optimize=True, quality=90)
        imgf = os.path.join(app.config['UPLOAD_FOLDER'], str(mail) +'.png')
#         print("profile pic displayed")
        try:
            return render_template('index.html', rooms=rooms, users=users, user_id=current_user.username+current_user.user_id, profilepic=imgf, allimg=allimg, x=q, mail=mail,data=data, imgroomlist=sol)
        except:
            return render_template('index.html', rooms=rooms, users=users, user_id=current_user.username+current_user.user_id, profilepic=imgf, allimg=allimg, imgroomlist=sol)
    except:
        imgef = os.path.join(app.config['UPLOAD_FOLDER'], 'user.png')
#         print("NO profile pic uploaded")
        try:
            return render_template('index.html', rooms=rooms, users=users, user_id=current_user.username+current_user.user_id, profilepic=imgef, allimg=allimg, x=q, mail=mail,data=data, imgroomlist=sol)
        except:
            return render_template('index.html', rooms=rooms, users=users, user_id=current_user.username+current_user.user_id, profilepic=imgef, allimg=allimg, imgroomlist=sol)
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    #if current_user.is_authenticated:
       #return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password_input = request.form.get('password')
        user = get_user(email)
        if user and user.check_password(password_input):
            login_user(user)
            user = current_user.username
            try:
                user_status_online(user)
                user_status_online2(user)
            except:
                print('logged in')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check mailID and password', 'danger')
    return render_template('login.html', title=login)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        user_id = request.form.get('user_id')
        check = check_ids(user_id)
        email = request.form.get('email')
        password = request.form.get('password')
        if get_username(username):
            flash('Username already used')
        elif check==email:
            try:
                save_user(username, user_id, email, password)
                profile_pic(email)
                flash('Sign in')
                return redirect(url_for('login'))
            except DuplicateKeyError:
                flash('User already exists!')
        else:
            flash('UserID and Email not matching')
    return render_template('signup.html')


@app.route("/logout/")
@login_required
def logout():    
    user = current_user.username
    user_status_offline(user)
    user_status_offline2(user)
    logout_user()
    return redirect(url_for('login'))


@app.route('/rooms/<room_id>',methods=['GET', 'POST'])
@login_required
def view_room(room_id):
    user_status_online2(current_user.username)
    funct = lis_img()
    allimg = funct[0]
    room = get_room(room_id)
    groups = get_rooms_for_user(current_user.username)
    # and is_room_admin(room_id, current_user.username)
    sol=zip(allimg,groups)
    if room and is_room_member(room_id, current_user.username):
#         print('get room accessed')
        messages = get_messages(room_id)
#         print('get messages accessed')
        existing_room_members = [member['_id']['username'] for member in get_room_members(room_id)]
        room_members_str = ",".join(existing_room_members)
        room_members = get_room_members(room_id)
        non_members = user_not_in_room(room_id)
        group_members = []
        group_members_list = []
        for member in room_members:
            username = member['_id']['username']
            group_members.append(username)
            user_id = get_user_id(username)
            user_key = username + user_id
            group_members_list.append(user_key)
            
        online_members_general = return_online_members()
        online_members_in_room = list(set(group_members) & set(online_members_general))
        online_count = len(online_members_in_room)
        
        if request.method == 'POST' and is_room_admin(room_id, current_user.username):
            room_name = request.form.get('room_name')
            room['name'] = room_name
            if room_name == '' and room_name == 'None':
                pass
            else:
                update_room(room_id, room_name)
            members_to_add = request.form.getlist('addmembers')
            members_to_remove = request.form.getlist('delmembers')
            try:
                edit_pic(room_name)
               
            except:
                pass

            if len(members_to_add):
                add_room_members(room_id, room_name, members_to_add, current_user.username)
                #message = 'Room edited successfully!'

            if len(members_to_remove):
                remove_room_members(room_id, members_to_remove)
                #message = 'Room edited successfully!'

            make_admin = request.form.getlist('adminmembers')
            if len(make_admin):
                if make_admin == current_user.username:
                    #message = 'You are already admin'
                    pass
                else:
                    make_room_admin(room_id, make_admin)

            delete_val = request.form.get('delete_room')
            if delete_val == 'delete_room':
                delete_room(room_id)
                return redirect(url_for('home'))
            return redirect(url_for('view_room',room_id=room_id))
        else:
            pass
        
        
        connection = MongoClient("mongodb+srv://PreethamGS:shettigar15@cluster0-3kawi.mongodb.net/test?retryWrites=true&w=majority")
        db = connection['ChatDB']        
        members_count = member_count_of_room(room_id)    
        usernames = current_user.username

        collections = db['room_members']
        p = collections.find_one({"_id.username": usernames})
        q = p['is_online']
        #print(x)
        try:
            collection = db['rooms']
            g_nm = get_group_name(room_id)
            roomid = get_group_id(g_nm)
            y = collection.find_one({"_id": roomid})
            x = y['Group_pic']

            def stringToRGB(base64_string):
                imgdata = base64.b64decode(str(base64_string))
                image = Image.open(io.BytesIO(imgdata))
                return image

            a = x[0]
            room_pic=[1]
            k = a.decode('utf-8')
            string = k
            arr = bytes(string, 'utf-8')
            base64.decodebytes(arr)
            pi = stringToRGB(string)
            pi.save("static/" + str(room_id)+'.png')
            del room_pic[0]
            room_pic.append(str(room_id) +'.png')
           
            return render_template('./view_room.html', room=room, room_members=room_members,username=current_user.username,
                                   user_id=current_user.user_id, message=messages, non_members=non_members,
                                   room_members_str=room_members_str, groups=groups, group_members_list=group_members_list, roompic=room_pic,allimg=allimg,x=q,li=members_count,on_co=online_count, online_members=online_members_in_room, imggrplist=sol, group_members=str(group_members))
#             except:
#                 print("error in render template")
#                 return redirect(url_for('view_room',room_id=room_id))
        except:
            def_room_pic=[1]
            del def_room_pic[0]
            def_room_pic.append('grp_img.png')
#             print("default group pic displayed")
            return render_template('./view_room.html', room=room, room_members=room_members, username=current_user.username,
                               user_id=current_user.user_id,message=messages, non_members=non_members,
                               room_members_str=room_members_str,groups=groups, group_members_list=group_members_list, roompic=def_room_pic,x=q,allimg=allimg,li=members_count,on_co=online_count, online_members=online_members_in_room, imggrplist=sol, group_members=str(group_members))
        
    else:
        return render_template("error_2.html")



@app.route('/rooms/<room_id>/messages/')
@login_required
def get_older_messages(room_id):
    room = get_room(room_id)
#     print('older messages accessed')
    if room and is_room_member(room_id, current_user.username):
        messages = get_messages(room_id)
        return dumps(messages)
    else:
        return render_template("error_2.html")


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent a message to the room {}: {}".format(data['username'], data['room'],
                                                                      data['message']))
    
    ist = pytz.timezone('Asia/Kolkata')
    data['created_at'] = datetime.now(ist).strftime("%d %b, %H:%M")
    user_id = get_user_id(data['username'])
#     print('real time msgs accessed')
    c=data['message']
    myEncryptedMessage = cryptocode.encrypt(c, "password123")
    
    save_message(data['room'],myEncryptedMessage, data['username'], user_id)
    socketio.emit('receive_message', data, room=data['room'], broadcast=True)


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
#     print('join room accessed')
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'], broadcast=True)


@login_manager.user_loader
def load_user(email):
    return get_user(email)
    #return User.get(username)
    
@app.route('/reset_password/<code>', methods=['GET', 'POST'])
def reset_password(code):
    user_mail = decode_token(code)['sub']
    print(user_mail)
    # user_mail = get_user_mail_from_object_id(code)
    if request.method == 'POST':
        password_1 = request.form.get('password_1')
        password_2 = request.form.get('password_2')
        if password_1 == password_2:            
            update_password_for_user(user_mail, password_1)            
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match')

    return render_template('reset_password.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form.get('email')
        url = request.host_url + 'reset_password'
        if get_email(email):
            with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login('athrvservices@gmail.com', 'Space@307#')

                #unique_code = get_object_id_from_email(email)
                expires = return_expiry_time()
                unique_code = create_access_token(str(email), expires_delta=expires)
                subject = 'Reset your Password for Athrv-Ed Chat App'
                body = f'To reset your password, click on the link below: \n {url}/{unique_code} \n\n This link will expire in 10 minutes!! \n\n click here to go to AthrvEd chat app:\n https://athrvedchattesting.herokuapp.com/'
                msg = f'Subject: {subject}\n\n {body}'
                smtp.sendmail('athrvservices@gmail.com', email, msg)
                flash('Mail has been Sent')
        else:
            flash('Enter a valid E-mail address')
    return render_template('forgot.html')

@app.route('/postmethodview', methods=['POST'])
def get_post_javascript():
    jsdata1 = request.form['javascript_data1']
#     print('value1', jsdata1)
    user = current_user.username
    if jsdata1 =='on':
        user_status_online2(user)
    else:
        user_status_offline2(user)
    return jsdata1


@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data']
#     print('value', jsdata)
    user = current_user.username
    if jsdata =='on':
        user_status_online2(user)
    else:
        user_status_offline2(user)
    return render_template('index.html')


@app.route('/postmethodload', methods=['POST'])
def get_post_javascript2():
    jsdata2 = request.form['javascript_data2']
#     print('value1', jsdata2)
    user = current_user.username
    if jsdata2 =='on':

        user_status_online2(user)
    else:

        user_status_offline2(user)
    return jsdata2


@app.route('/postmethodload2', methods=['POST'])
def get_post_javascript3():
    jsdata3 = request.form['javascript_data3']
#     print('value1', jsdata3)
    user = current_user.username
    if jsdata3 =='on':

        user_status_online2(user)

    return jsdata3

@app.route('/postmethodfaq', methods=['POST'])
def get_post_java():
    js2 = request.form['js_data2']

    user = current_user.username
    if js2 =='on':

        user_status_online2(user)
    else:

        user_status_offline2(user)
    return js2

@app.route('/postfaq', methods=['POST'])
def get_post():
    js1 = request.form['js_data1']
#     print('value1', jsdata1)
    user = current_user.username
    if js1 =='on':
        user_status_online2(user)
    else:
        user_status_offline2(user)
    return js1

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
