from flask import Flask ,jsonify ,request
from db_connect import get_db_connection
from flask_jwt_extended  import create_access_token ,get_jwt_identity,jwt_required, JWTManager
import os
import json



app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)



@app.route('/')
def index():
   conn = get_db_connection()
   print(conn)
   return 'it works'

@app.route("/api/courts")

def court_list():
   conn = get_db_connection()
   cur = conn.cursor()
   cur.execute("select * from courts")
   res = cur.fetchall()
   data = []
   for i in res:
      cur.execute("select * from check_ins where court_id = "+ str(i[0]))
      current = len(cur.fetchall())
      obj = {"id":i[0],"name":i[1],"indoor":i[2],"hoops":i[3],"photo":i[4],"current_players":current,"lat":i[5],"lon":i[6]}

      data.append(obj)
   return data   

@app.route("/api/courts/<id>")
def court_id(id):
   conn = get_db_connection()
   cur = conn.cursor()
   cur.execute("select * from courts where id = " + id)
   res = cur.fetchall()
   return res   

@app.route("/api/login",methods=["POST"])
def login():
   username = request.json["username"]
   password = request.json["password"]

   conn = get_db_connection()
   cur = conn.cursor()
   cur.execute("SELECT count(id) FROM users WHERE username = '" + str(username) + "' and password ='"+ str(password)+"'")
   res = cur.fetchone()

   if res[0] == 0:
      print("User not found")
      return {"msg":"User not found"}
   else:
      access_token = create_access_token(identity=username)
      return {"msg":"Logged in","access_token":access_token}


@app.route("/api/user/<id>",)
@jwt_required()
def get_user(id):
   conn = get_db_connection()
   cur = conn.cursor()
   cur.execute("select * from users where id = " + id)

   res = cur.fetchall()
   if len(res) == 0:
      return {"msg":"User not found"}
   return res 


@app.route("/api/check_in",methods=["POST"])
@jwt_required()
def check_in():
   current_user = get_jwt_identity()
   user_id = request.json["user_id"]
   court_id = request.json["court_id"]
   conn = get_db_connection()
   cur = conn.cursor()
   cur.execute("select * from users where username = '" + current_user+"'")
   res = cur.fetchone()
   print(res[0])
   if res[0] == user_id:
      cur.execute("select * from courts where id = " + str(court_id))
      res = cur.fetchall()
      if len(res) == 0:
         return {"msg": "court doesnt exist"}
      else:
         cur.execute('insert into check_ins ("user_id","court_id")'+" values ('{}','{}')".format(user_id,court_id))
         conn.commit()
         return {"msg":"checked in"}
   else: return "nahh"

@app.route("/api/check_out",methods=["POST"])
@jwt_required()
def check_out():
   current_user = get_jwt_identity()
   user_id = request.json["user_id"]
   court_id = request.json["court_id"]
   conn = get_db_connection()
   cur = conn.cursor()
   cur.execute("select * from users where username = '" + current_user+"'")
   res = cur.fetchone()
   print(res[0])
   if res[0] == user_id:
      cur.execute("select * from courts where id = " + str(court_id))
      res = cur.fetchall()
      if len(res) == 0:
         return {"msg": "court doesnt exist"}
      else:
         cur.execute('delete from check_ins where user_id = {} and court_id = {}'.format(user_id,court_id))
         conn.commit()
         return {"msg":"checked out"}
   else: return "nahh"


if __name__ == "__main__":
   app.run(debug=True,port=8080)
