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

Passenger = Query()
Trips = Query()
Routes = Query()

WIMT_TOKEN = wimt.getAccessToken()

if len(sys.argv)>1 and sys.argv[1] == "prod":
    HOST = '0.0.0.0'

@app.route('/')
def hello():
    return jsonify({"result" : "the server is up!"})

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
    dt = body['date']
    trips.insert({"route_id" : route_id, "datetime" : dt, "driver_name" : driver_name , "trip_id" : route_id + " " + dt})
    return jsonify({"result" : "done"})

@app.route('/activate_route', methods=['POST'])
def activate_route():
    # POST request with driverName, routeId
    # send notification to chatbot
    # response is the list of people taking this route 
    body = request.get_json()
    driver_name = body['driverName']
    # route_id = body['routeId']
    # res_trip = trips.search((Trips.driver_id == driver_name) & (Trips.route_id == route_id))
    res_trip = trips.search(Trips.driver_name == driver_name) # list of trips 
    res_trip = res_trip[0] # just pick one 
    trip_id = res_trip['trip_id']

    res = passengers.search(Passenger.trip_id == trip_id) # list of all passengers for this trip
    passenger_list = []
    for r in res:
        passenger_list.append({"id" : r['passenger_id'], "curr_loc" : {"latitude" : r['curr_loc']["latitude"], "longitude" : r['curr_loc']['longitude']}, "name" : r['name'], "photo" : r['profile_image'], "status" : r['status'] })
    '''
    Send notification to all the passengers subscribed to this one
    '''
    x = routes.search(Routes.id == res_trip['route_id'])
    coordinates = x[0]['coordinates']
    temp = {"passengers" : passenger_list, "coordinates" : coordinates}
    

    return jsonify(temp)

@app.route('/pickup', methods=['POST'])
def pickup():
    body = request.get_json()
    passenger_id = body['passenger_id']
    res = passengers.search(Passenger.passenger_id == passenger_id)
    res[0]['status'] = 1
    '''
    Notify this passenger
    '''
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

@app.route('/add_passenger', methods=['POST'])
def add_passenger():
    body = request.get_json()
    add_entry('passengers', body)
    return jsonify({"result" : "done"})

@app.route('/add_route', methods=['POST'])
def add_route():
    body = request.get_json()
    line = getLine(body['location'],body['destination'])
    routeJson = parseRoute(line)
    add_entry('routes', routeJson)
    return jsonify({"result" : "done"})

'''

Endpoints for the chat bots 

'''

'''
DB Functions
'''

'''
Schema for Passenger
name, user_id, profile_image, curr_loc [lng,lat], status, trip_id

Schema for Drivers
active_route, status (1 is active, 0 is inactive), capacity, curr_passengers, driver_name

Schema for Routes
id, name, coordinates 

Schema for Trips 
route_id, datetime, driver_id
'''

def select_table(table_name):
    if table_name == "drivers":
        return drivers
    if table_name == "passengers":
        return passengers
    if table_name == "routes":
        return routes
    if table_name == "trips":
        return trips

def add_entry(table_name, obj):
    tab = select_table(table_name)
    tab.insert(obj)

if __name__ == "__main__":
    # app.run(debug=True, port=43001, threaded=True, host=HOST, ssl_context=context)
    app.run(debug=True, port=43001, threaded=True, host=HOST)