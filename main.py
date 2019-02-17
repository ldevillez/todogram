import time
import telepot
from telepot.loop import MessageLoop
import schedule
import sqlite3
import sys
import subprocess
from conf import token


con = sqlite3.connect('todo.db')
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS chans
            (id integer primary key, chan integer)""")
cur.execute("""CREATE TABLE IF NOT EXISTS todos
    (id integer primary key, chan integer, todo text, finish boolean)""")

con.commit()


bot = telepot.Bot(token)


def get_todo(id):
  con = sqlite3.connect('todo.db')
  cur = con.cursor()
  cur.execute("SELECT * FROM todos WHERE chan=" + str(id) + " AND finish=0")
  Todos = cur.fetchall()
  if len(Todos) < 1:
    return None
  else:
    msg = ''
    i = 1
    for (id, chan, todo, finish) in Todos:
      msg += str(i) + ": " + todo + '\n'
      i += 1
    return msg

def pingAll():
  con = sqlite3.connect('todo.db')
  cur = con.cursor()
  cur.execute("SELECT * FROM chans")
  data = cur.fetchall()
  if data is not None:
    for (id,chanId) in data:
      msg = get_todo(id)
      if msg is not None:
        msg = "*Liste des chose à faire*\n" + msg
        bot.sendMessage(chanId,msg)

def handle(msg):
  if 'text' in msg:
    if '/help' in msg['text'] or '/help@wesToDoBot' in msg['text']:
      msgToSend = """LISTE HERE YOU LITTLE SHIT
      *-/start*: init le bot sur un chan
      *-/help*: GNEU
      *-/add text*: ajoute text dans la liste des todos
      *-/finish num*: retire le todo correspondant au numéro num
      """
      bot.sendMessage(msg['from']['id'],msgToSend,parse_mode = 'Markdown')
    elif '/start' in msg['text'] or '/start@wesToDoBot' in msg['text']: 
      con = sqlite3.connect('todo.db')
      cur = con.cursor()
      cur.execute("SELECT * FROM chans WHERE chan=" + str(msg['chat']['id']))
      data = cur.fetchone()
      if data is None:
        cur.execute("INSERT INTO chans (chan) VALUES ("+str(msg['chat']['id'])+")")
        con.commit()
    elif '/add' in msg['text'] or '/add@wesToDoBot' in msg['text']:
      con = sqlite3.connect('todo.db')
      cur = con.cursor()
      cur.execute("SELECT * FROM chans WHERE chan=" + str(msg['chat']['id']))
      data = cur.fetchone()
      if data is not None:
        query = "INSERT INTO todos (chan,finish,todo) VALUES (" + str(data[0])  + ",0,\"" + msg['text'].split(' ',1)[1] + "\")"
        print(query)
        cur.execute(query)
        con.commit()
    elif '/get' in msg['text'] or '/get@wesToDoBot' in msg['text']:
      con = sqlite3.connect('todo.db')
      cur = con.cursor()
      cur.execute("SELECT * FROM chans WHERE chan=" + str(msg['chat']['id']))
      data = cur.fetchone()
      if data is not None:
        msg = get_todo(data[0])
        bot.sendMessage(data[1], msg)
    elif '/finish' in msg['text'] or '/finish@wesToDoBot' in msg['text']:
      con = sqlite3.connect('todo.db')
      cur = con.cursor()
      cur.execute("SELECT * FROM chans WHERE chan=" + str(msg['chat']['id']))
      data = cur.fetchone()
      if data is not None:
        cur.execute("SELECT * FROM todos WHERE chan=" + str(data[0]) + " AND finish=0")
        Todos = cur.fetchall()
        id = Todos[int(msg['text'].split(' ')[1])-1]
        query = "UPDATE todos SET finish=1 WHERE id =" +str(id[0])
        cur.execute(query)
        con.commit()
        msg = get_todo(data[0])
        bot.sendMessage(data[1], msg)
MessageLoop(bot, handle).run_as_thread()
schedule.every().day.at("08:00").do(pingAll)

while True:
  schedule.run_pending()
  time.sleep(1)


