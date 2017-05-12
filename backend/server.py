from flask import Flask, request
import sys, requests
from tinydb import TinyDB, Query

HOST = None
DB_ADDRESS = "db.json"

if len(sys.argv)>1 and sys.argv[1] == "prod":
    HOST = '0.0.0.0'

app = Flask(__name__)
db = TinyDB(DB_ADDRESS)

if __name__ == "__main__":
    app.run(debug=True, port=43001, threaded=True, host=HOST)