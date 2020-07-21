from gevent import monkey
monkey.patch_all()

from geventwebsocket import WebSocketServer

host = '0.0.0.0'
port = 5000


if __name__ == "__main__":
    import flaskr
    print("Server starting")
    http_server = WebSocketServer((host, port), flaskr.app, debug=True)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        flaskr.cleanup()
        http_server.stop()
    # app.run(threaded=True, host='localhost', port='5000', debug=True)


