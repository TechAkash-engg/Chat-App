from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash
from user import User
import pytz
import cryptocode

client = MongoClient('mongodb+srv://PreethamGS:shettigar15@cluster0-3kawi.mongodb.net/test?retryWrites=true&w=majority')   #MongoDb cluster url

chat_db = client.get_database('ChatDB')
users_collection = chat_db.get_collection('users')
rooms_collection = chat_db.get_collection('rooms')
room_members_collection = chat_db.get_collection('room_members')
messages_collection = chat_db.get_collection('messages')
user_mail_collection = chat_db.get_collection('user_mail')
ist = pytz.timezone('Asia/Kolkata')


def check_ids(user_id):   #get mail from userid
    usrid = user_mail_collection.find_one({'user_id':{'$eq':user_id}})
    return usrid['mail']

def save_user(username, user_id, email, password):  #create user document on signup
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id': email, 'username': username, 'user_id': user_id, 'password': password_hash})

def get_user(email): #return user data by taking email
    user_data = users_collection.find_one({'_id': email})
    return User(user_data['username'], user_data['user_id'], user_data['_id'], user_data['password']) if user_data else None

def save_room(room_name, created_by, participants): #create a document on new room creation 
    creator_id = get_user_id(created_by)
    room_id = rooms_collection.insert_one({'name': room_name,
                                           'creator_data': {'created_by': created_by, 'creator_id': creator_id},
                                           'participants': {'members': participants}, 'created_at': datetime.now(ist)}).inserted_id
    add_room_member(room_id, room_name, created_by, created_by, is_room_admin=True)
    return room_id

def update_room(room_id, room_name): #update room and room members based on changes in edit room
    rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'name': room_name}})
    room_members_collection.update_many({'_id.room_id': ObjectId(room_id)}, {'$set': {'room_name': room_name}})

def get_room(room_id): #return room data from room_id
    return rooms_collection.find_one({'_id': ObjectId(room_id)})

def add_room_member(room_id, room_name, username, added_by, is_room_admin= False): #add the room creator data into room_members collection
    adder_id = get_user_id(added_by)
    room_members_collection.insert_one({'_id': {'room_id': ObjectId(room_id), 'username': username},
                                        'room_name': room_name,
                                        'adder_data': {'adder_name': added_by, 'adder_id': adder_id},
                                        'added_at': datetime.now(ist), 'is_room_admin': is_room_admin,'is_online':True,'is_online2':True})

def add_room_members(room_id, room_name, usernames, added_by): #add data of selected people into room_members_collection
    adder_id = get_user_id(added_by)
    room_members_collection.insert_many([{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name,
                                        'adder_data': {'adder_name': added_by, 'adder_id': adder_id},
                                        'added_at': datetime.now(ist), 'is_room_admin': False,'is_online':False,'is_online2':False} for username in usernames])

def remove_room_members(room_id, usernames): #delete member data on removal from group
    room_members_collection.delete_many({'_id':{'$in': [{'room_id': ObjectId(room_id), 'username': username} for username in usernames]}})

def make_room_admin(room_id, usernames): #make admin status true for selected members
    for username in usernames :
        if is_room_member(room_id, username):
            room_members_collection.update_many({'_id.room_id': ObjectId(room_id), '_id.username': username},
                                           {'$set': {'is_room_admin': True}})

def get_room_members(room_id):  #return list of usernames in a room from the room_id
    return list(room_members_collection.find({'_id.room_id': ObjectId(room_id)})) #

def get_rooms_for_user(username):  #return list of all rooms in which the user is there
    return list(room_members_collection.find({'_id.username': username}))

def is_room_member(room_id, username): #check if a particular user is room of a room using username and room_id
    return room_members_collection.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}})

def is_room_admin(room_id, username):  #check if a person is room admin to give him access to edit rooms
    return room_members_collection.count_documents(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'is_room_admin': True})

def save_message(room_id, text, sender, sender_id): #save all messages sent in messages_collection
    messages_collection.insert_one({'room_id': room_id, 'text': text, 'sender': sender, 'sender_id': sender_id,
                                    'created_at': datetime.now(ist)})

def get_messages(room_id): #get all messages of a particular group in order of recent text first
    messages = list(messages_collection.find({'room_id': room_id}).sort('_id', DESCENDING))
    for message in messages:
        d = message['text']
        myDecryptedMessage = cryptocode.decrypt(d, "password123")
        message['text'] = myDecryptedMessage
        message['created_at'] = message['created_at'].strftime('%d %b, %H:%M')
    return messages[::-1]

def get_group_id(room_name):  #get room_id from group name
    r_id=rooms_collection.find_one({'name': room_name})
    return r_id['_id']

def get_group_name(room_id):  #get room name from room_id
    r_nm = rooms_collection.find_one({'_id': ObjectId(room_id)})
    return r_nm['name']

def get_rooms_for_userpic(username):  #get group pictures of a particular user
    return list(room_members_collection.find({'_id.username': username},{'_id.room_id':1}))

def get_mailid(username): #get mail id from username
    mid=users_collection.find_one({'username': username})
    return mid['_id']

def get_user_id(username): #get user id from username
    name = users_collection.find_one({'username': username})
    return name['user_id']

def delete_room(room_id): #delete all details of a particular room when admin clicks delete room
    rooms_collection.delete_one({'_id': ObjectId(room_id)})
    room_members_collection.delete_many({'_id.room_id': ObjectId(room_id)})
    messages_collection.delete_many({'room_id': room_id})

def get_username(username): #check for same username in users collection
    return users_collection.count_documents({'username': username})

def get_username_count(username):  
    return users_collection.count_documents({'username': username})

def get_email(email): #check for same email id in users collection
    return users_collection.count_documents({'_id':email})

def get_usernames(): 
    return users_collection.distinct('username')

def user_not_in_room(room_id): #return list of users who have registered but not in a particular group, used in add participant menu
    all_users = get_usernames()
    room_users = get_room_members(room_id)
    room_list = []
    for member in room_users:
        name=member['_id']['username']
        room_list.append(name)
    users_not_in_room = [i  for i in all_users if i not in room_list]
    return users_not_in_room

def get_object_id_from_email(email):  
    name = user_mail_collection.find_one({'mail': email})
    return name['_id']

def get_user_mail_from_object_id(object_id):
    user_detail = user_mail_collection.find_one({'_id': ObjectId(object_id)})
    return user_detail['mail']

def update_password_for_user(user_mail, password): #update password of user in his document
    password_hash = generate_password_hash(password)
    users_collection.update_one({'_id': user_mail}, {'$set': {'password': password_hash}})
    
def user_status_offline(username):
    room_members_collection.update_many({'_id.username': username}, {'$set': {'is_online': False}})

def user_status_online(username):
    room_members_collection.update_many({'_id.username': username}, {'$set': {'is_online': True}})

def user_status_offline2(username):
    room_members_collection.update_many({'_id.username': username}, {'$set': {'is_online2': False}})

def user_status_online2(username):
    #room_members_collection.update_many({'_id.username': username}, {'$unset': {'is_online2': 1}})
    room_members_collection.update_many({'_id.username': username}, {'$set': {'is_online2': True}})

def member_count_of_room(room_id):  #count total number of people in a room
    sq = room_members_collection.count_documents({'_id.room_id': ObjectId(room_id)})
    return sq

def return_online_members(): #return list of all memebers who are using chat app 
    final_list = set()
    mem = room_members_collection.find({'is_online2': True})
    for m in mem:
        online_list = m['_id']['username']
        final_list.add(online_list)

    member_online_list = list(final_list)
    return member_online_list
