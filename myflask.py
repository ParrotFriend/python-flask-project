#!/usr/bin/python3

from flask import Flask, jsonify, session, render_template, redirect, url_for, request
import sqlite3

app = Flask(__name__)
app.secret_key = "jfioefefjioawfnieofa"

# establishes connection to sqlite database
conn = sqlite3.connect('grocerylist.db', check_same_thread=False)
print('Database connected')

# creates table to hold users
conn.execute('''CREATE TABLE IF NOT EXISTS USER
 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
 USERNAME TEXT NOT NULL
 );''')

# creates table to hold grocery items
conn.execute('''CREATE TABLE IF NOT EXISTS GROCERIES
 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
 USERNAME TEXT NOT NULL,
 ITEM TEXT NOT NULL,
 QUANTITY INTEGER NOT NULL
 );''')

#--------- INDEX PAGE ---------------------
@app.route("/home", methods=["GET", "POST"])
def index():
    if "username" in session:
        username = session['username']
        if request.method == "GET":
            cur = conn.cursor()
            search = request.args.get('search')
            if search:
                # Filter items by search term (case-insensitive)
                cur.execute("SELECT ITEM, QUANTITY FROM GROCERIES WHERE USERNAME=? AND LOWER(ITEM) LIKE ?", (username, f"%{search.lower()}%"))
            else:
                cur.execute("SELECT ITEM, QUANTITY FROM GROCERIES WHERE USERNAME=?", (username,))
            data = cur.fetchall()
            return render_template('grocerylist.html', name=username, groceries=data)
        elif request.method == "POST":
            item = request.form.get('groceryitem')
            quantity = request.form.get("quantity")
            if item and quantity:
                conn.execute('INSERT INTO GROCERIES (USERNAME, ITEM, QUANTITY) VALUES (?, ?, ?)', (username, item, quantity))
                conn.commit()
            return redirect(url_for("index"))
    else:
        return redirect(url_for("login"))

#---------- UPDATE ITEM ------------------          
@app.route("/update", methods=["POST"])
def updateItem():
    old_item = request.form.get('old_item')
    new_item = request.form.get('new_item')
    new_quantity = request.form.get('new_quantity')
    username = session.get('username')
    if old_item and new_item and new_quantity and username:
        cur = conn.cursor()
        cur.execute("UPDATE GROCERIES SET ITEM=?, QUANTITY=? WHERE ITEM=? AND USERNAME=?", (new_item, new_quantity, old_item, username))
        conn.commit()
    return redirect(url_for("index"))

#---------- DELETE ITEM ------------------          
@app.route("/delete", methods=["POST"])
def deleteItem():
    item = request.form.get('item')
    username = session.get('username')
    if item and username:
        cur = conn.cursor()
        cur.execute("DELETE FROM GROCERIES WHERE ITEM=? AND USERNAME=?", (item, username)) 
        conn.commit()
    return redirect(url_for("index"))

#--------- Users ------------------------
@app.route("/users")
def getAllUsers():
    cur = conn.cursor()
    cur.execute("SELECT * FROM USER") 
    data = cur.fetchall()
    users = []
    for user in data:
        item = {'id': user[0], 'username': user[1]}
        users.append(item)
    return jsonify(users)

#----------  LOGIN  ---------------------
@app.route("/", methods=["POST", "GET"])
def login():
    if "username" in session:
        return redirect(url_for("index"))
    elif request.method == "POST":
        session["username"] = request.form.get("username")
        cur = conn.cursor()
        cur.execute("SELECT USERNAME FROM USER WHERE USERNAME=?", (session["username"],)) 
        data = cur.fetchall()
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
    app.run(host="0.0.0.0", port=2224)