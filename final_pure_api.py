#!/usr/bin/python3

from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

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

#--------- API: GET ALL GROCERIES FOR USER, ADD ITEM, SEARCH -----------
@app.route("/groceries", methods=["GET", "POST"])
def groceries():
    if request.method == "GET":
        username = request.args.get('username')
        search = request.args.get('search')
        if not username:
            return jsonify({"error": "username is required"}), 400
        cur = conn.cursor()
        if search:
            cur.execute("SELECT ITEM, QUANTITY FROM GROCERIES WHERE USERNAME=? AND LOWER(ITEM) LIKE ?", (username, f"%{search.lower()}%"))
        else:
            cur.execute("SELECT ITEM, QUANTITY FROM GROCERIES WHERE USERNAME=?", (username,))
        data = cur.fetchall()
        groceries = [{"item": row[0], "quantity": row[1]} for row in data]
        return jsonify(groceries)
    elif request.method == "POST":
        data = request.get_json()
        username = data.get("username")
        item = data.get("item")
        quantity = data.get("quantity")
        if not all([username, item, quantity]):
            return jsonify({"error": "username, item, and quantity are required"}), 400
        conn.execute('INSERT INTO GROCERIES (USERNAME, ITEM, QUANTITY) VALUES (?, ?, ?)', (username, item, quantity))
        conn.commit()
        return jsonify({"message": "Item added"}), 201

#--------- API: UPDATE ITEM -----------
@app.route("/groceries/update", methods=["PUT"])
def update_grocery():
    data = request.get_json()
    username = data.get("username")
    old_item = data.get("old_item")
    new_item = data.get("new_item")
    new_quantity = data.get("new_quantity")
    if not all([username, old_item, new_item, new_quantity]):
        return jsonify({"error": "username, old_item, new_item, and new_quantity are required"}), 400
    cur = conn.cursor()
    cur.execute("UPDATE GROCERIES SET ITEM=?, QUANTITY=? WHERE ITEM=? AND USERNAME=?", (new_item, new_quantity, old_item, username))
    conn.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Item not found or not updated"}), 404
    return jsonify({"message": "Item updated"})

#--------- API: DELETE ITEM -----------
@app.route("/groceries/delete", methods=["DELETE"])
def delete_grocery():
    data = request.get_json()
    username = data.get("username")
    item = data.get("item")
    if not all([username, item]):
        return jsonify({"error": "username and item are required"}), 400
    cur = conn.cursor()
    cur.execute("DELETE FROM GROCERIES WHERE ITEM=? AND USERNAME=?", (item, username))
    conn.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Item not found or not deleted"}), 404
    return jsonify({"message": "Item deleted"})

#--------- API: GET ALL USERS -----------
@app.route("/users", methods=["GET"])
def get_all_users():
    cur = conn.cursor()
    cur.execute("SELECT * FROM USER")
    data = cur.fetchall()
    users = [{'id': user[0], 'username': user[1]} for user in data]
    return jsonify(users)

#--------- API: REGISTER USER -----------
@app.route("/users/register", methods=["POST"])
def register_user():
    data = request.get_json()
    username = data.get("username")
    if not username:
        return jsonify({"error": "username is required"}), 400
    cur = conn.cursor()
    cur.execute("SELECT USERNAME FROM USER WHERE USERNAME=?", (username,))
    if cur.fetchone():
        return jsonify({"error": "username already exists"}), 409
    cur.execute("INSERT INTO USER (USERNAME) VALUES(?)", (username,))
    conn.commit()
    return jsonify({"message": "User registered"}), 201
{
  "username": "john",
  "item": "apple",
  "quantity": 5
}
print("Operation done successfully")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2224)