from flask import Flask, request, jsonify
import sys, requests, wimt
from tinydb import TinyDB, Query
from pprint import pprint
# import ssl
# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# context.load_cert_chain('server.crt', 'server.key')

HOST = None
DB_ADDRESS = "db.json"

app = Flask(__name__)
db = TinyDB(DB_ADDRESS)
drivers = db.table('drivers')
passengers = db.table('passengers')
routes = db.table('routes')
trips = db.table('trips')

if len(sys.argv)>1 and sys.argv[1] == "prod":
    HOST = '0.0.0.0'

@app.route('/')
def hello():
    return "the server is up!"

@app.route('/test')
def test():
    return "echo the endpoint is working"

@app.route('/get_routes')
def get_routes():
    tab = select_table("routes")
    return jsonify({"route_list":tab.all()})

@app.route('/plan_route', methods=['POST'])
def plan_route():
    body = request.get_json()
    driver_name = body['driverName']
    route_id = body['routeId']
    date = body['date']
    
    return jsonify({"result" : "done"})

@app.route('/activate_route', methods=['POST'])
def activate_route():
    # POST request with route id 
    # send notification to chatbot
    # response is the list of people taking this route 
    return jsonify({"result" : "activated route"})

@app.route('/pickup')
def pickup():
    return jsonify({"result" : "picked up"})

# optional for now 
@app.route('/cancel_route', methods=['POST'])
def cancel_route():
    # POST request with route id 
    # send notification to chatbot 
    return jsonify({"result" : "cancelled route"})

'''
Populate the DB functions 

'''

@app.route('/add_driver', methods=['POST'])
def add_driver():
    body = request.get_json()
    add_entry('drivers', body)
    return jsonify({"result" : "done"})

@app.route('/add_user', methods=['POST'])
def add_user():
    body = request.get_json()
    add_entry('users', body)
    return jsonify({"result" : "done"})

@app.route('/add_route', methods=['POST'])
def add_route():
    body = request.get_json()
    add_entry('routes', body)
    return jsonify({"result" : "done"})

'''
DB Functions
'''

'''
Schema for User
name, userid, profile_image, curr_loc [lat,lng], status

Schema for Drivers

active_route, status (1 is active, 0 is inactive), capacity, curr_passengers, driver_name

Schema for Routes
id, name, coordinates 

Schema for Trips 

'''

def select_table(table_name):
    if table_name == "drivers":
        return drivers
    if table_name == "users":
        return users
    if table_name == "routes":
        return routes

def add_entry(table_name, obj):
    tab = select_table(table_name)
    tab.insert(obj)

if __name__ == "__main__":
    # app.run(debug=True, port=43001, threaded=True, host=HOST, ssl_context=context)
    app.run(debug=True, port=43001, threaded=True, host=HOST)