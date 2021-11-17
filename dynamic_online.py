from pymongo import MongoClient

import threading
client = MongoClient('mongodb+srv://PreethamGS:shettigar15@cluster0-3kawi.mongodb.net/test?retryWrites=true&w=majority')

chat_db = client.get_database('ChatDB')
users_collection = chat_db.get_collection('users')
rooms_collection = chat_db.get_collection('rooms')
room_members_collection = chat_db.get_collection('room_members')


def printit():
  threading.Timer(5.0, printit).start()

  final_list = set()
  mem = room_members_collection.find({'is_online2': True})
  for m in mem:
      online_list = m['_id']['username']
      final_list.add(online_list)

  member_online_list = list(final_list)


  res = str(member_online_list)[1:-1]
  file = open('static/memb.txt', 'w')
  file.write(str(res))

  file.close()


printit()
