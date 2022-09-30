#!/usr/bin/python3

from flask import Flask, jsonify
from flask import session
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
import sqlite3

# module (__name__) as argument
app = Flask(__name__)
app.secret_key ="jfioefefjioawfnieofa"

conn = sqlite3.connect('grocerylist.db', check_same_thread=False)
print('Database connected')

#creates table to hold users
conn.execute('''CREATE TABLE IF NOT EXISTS USER
 (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
 USERNAME        TEXT    NOT NULL
 );''')

conn.execute('''CREATE TABLE IF NOT EXISTS GROCERIES
 (ID INTEGER  PRIMARY KEY  AUTOINCREMENT,
 USERNAME       TEXT    NOT NULL,
 ITEM           TEXT    NOT NULL,
 QUANTITY      INTEGER  NOT NULL
 );''')

#--------- INDEX PAGE ---------------------
@app.route("/home", methods=["GET", "POST"])
def index():
    username = session['username']
    
    if "username" in session:
        #--------- GET ALL ITEMS --------
        if request.method == "GET":
            cur = conn.cursor()
            # gets all items from database that match current user
            cur.execute("SELECT ITEM, QUANTITY FROM GROCERIES WHERE USERNAME=?", (username,)) 
            data = cur.fetchall()
            conn.commit()
            
            #updates page with results
            return render_template('grocerylist.html', name = session["username"], groceries= data)
        
        # --- ADD ITEM -----------
        elif request.method == "POST":
            item = request.form.get('groceryitem')
            quantity = request.form.get("quantity")
            conn.execute('INSERT INTO GROCERIES (USERNAME, ITEM, QUANTITY) VALUES (?, ?, ?)', (username, item, quantity))
            conn.commit()
            
            # returns back to list
            return redirect(url_for("index"))
    # returns user to login page if not logged in     
    else:
        return redirect(url_for("login"))  

#---------- DELETE ITEM ------------------          
@app.route("/delete", methods=["POST"])
def deleteItem():
    # gets item from from and deletes it from database
    item = request.form.get('item')
    cur = conn.cursor()
    cur.execute("DELETE FROM GROCERIES WHERE ITEM=?", (item,)) 
    conn.commit()
    return redirect(url_for("index"))

#--------- Users ------------------------
@app.route("/users")
def getAllUsers():
    cur = conn.cursor()
    # gets all users and returns in JSON object
    cur.execute("SELECT * FROM USER") 
    data = cur.fetchall()
    print(data)
    users =[]
    for user in data:
        item = {'id': user[0], 'username': user[1]}
        users.append(item)
    return jsonify(users)

#----------  LOGIN  ---------------------
@app.route("/", methods=["POST", "GET"])
def login():
    if "username" in session:
        username = session["username"]
        return redirect(url_for("index"))
    elif request.method == "POST":
        session["username"] = request.form.get("username")
        cur = conn.cursor()
        cur.execute("SELECT USERNAME FROM USER WHERE USERNAME=?", (session["username"],)) 
        data = cur.fetchall()
        # if user is not in database it adds the user
        if len(data) == 0:
            cur.execute("INSERT INTO USER (USERNAME) VALUES(?)", (session['username'],))
        
        conn.commit()
        
        return redirect(url_for("index"))
    else:
        return render_template('login.html')

#----------  LOGOUT  ---------------------
@app.route("/logout", methods=["GET"])
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

print("Operation done successfully")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2224) # runs the application
