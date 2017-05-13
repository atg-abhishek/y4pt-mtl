from flask import Flask, request
import sys, requests, wimt
from tinydb import TinyDB, Query
# import ssl
# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# context.load_cert_chain('server.crt', 'server.key')

HOST = None
DB_ADDRESS = "db.json"

app = Flask(__name__)
db = TinyDB(DB_ADDRESS)

if len(sys.argv)>1 and sys.argv[1] == "prod":
    HOST = '0.0.0.0'

@app.route('/')
def hello():
    return "the server is up!"

@app.route('/test')
def test():
	Driver = Query()
	db.insert({'name':'John', 'age':22})
	return db.search(Driver.name == 'John')
    return "echo the endpoint is working"

if __name__ == "__main__":
    # app.run(debug=True, port=43001, threaded=True, host=HOST, ssl_context=context)
    app.run(debug=True, port=43001, threaded=True, host=HOST)