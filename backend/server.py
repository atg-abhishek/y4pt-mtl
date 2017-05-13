from flask import Flask, request
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
users = db.table('users')
routes = db.table('routes')

if len(sys.argv)>1 and sys.argv[1] == "prod":
    HOST = '0.0.0.0'

@app.route('/')
def hello():
    return "the server is up!"

@app.route('/test')
def test():
    return "echo the endpoint is working"

@app.route('/add_driver')
def add_driver():
    body = request.get_json()
    add_entry('drivers', body)
    return "done"

@app.route('/plan_route', methods=['POST'])
def plan_route():
    body = request.get_json()
    pprint(body)
    # POST request 
    # send me the route id , date , time 
    return "planned route"

@app.route('/activate_route')
def activate_route():
    # POST request with route id 
    # send notification to chatbot
    # response is the list of people taking this route 
    return "activated route"

# optional for now 
@app.route('/cancel_route')
def cancel_route():
    # POST request with route id 
    # send notification to chatbot 
    return "route cancelled"

'''
DB Functions
'''

'''
Schema for User
name, userid, profile_image, curr_loc [lat,lng], status

Schema for Drivers
active route, status, capacity, curr_passengers

Schema for Routes
start, stop (each in lat, lng)
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