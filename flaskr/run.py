from gevent import monkey
monkey.patch_all()

from flaskr import app
from geventwebsocket import WebSocketServer

host = '0.0.0.0'
port = 5000

if __name__ == "__main__":
    print("Server starting")
    http_server = WebSocketServer((host, port), app, debug=True)
    http_server.serve_forever()
    # app.run(threaded=True, host='localhost', port='5000', debug=True)
