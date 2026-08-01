import json
from http.server import HTTPServer, BaseHTTPRequestHandler

USERS_LIST = [
    {
        "id": 1,
        "username": "theUser",
        "firstName": "John",
        "lastName": "James",
        "email": "john@email.com",
        "password": "12345",
    }
]


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_response(self, status_code=200, body=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body if body else {}).encode('utf-8'))

    def _pars_body(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        return json.loads(self.rfile.read(content_length).decode('utf-8'))  # <--- Gets the data itself

    def do_GET(self):
        global USERS_LIST
        if self.path == "/reset":
            USERS_LIST = [
                {
                    "id": 1,
                    "username": "theUser",
                    "firstName": "John",
                    "lastName": "James",
                    "email": "john@email.com",
                    "password": "12345",
                }
            ]
            self._set_response(200, USERS_LIST)

        elif self.path == "/users":
            self._set_response(200, USERS_LIST)

        elif self.path.startswith("/user/"):
            username = self.path.split("/")[-1]
            user = next((u for u in USERS_LIST if u["username"] == username), None)
            if user:
                self._set_response(200, user)
            else:
                self._set_response(400, {"error": "User not found"})


    def do_POST(self):
        global USERS_LIST
        try:
            data = self._pars_body()
        except:
            return self._set_response(400, {})

        def valid_user(u):
            return all(k in u for k in ["id","username","firstName","lastName","email","password"])

        if self.path == "/user":
        # один користувач
            if not isinstance(data, dict) or not valid_user(data):
                return self._set_response(400, {})
            if any(u["id"] == data["id"] for u in USERS_LIST):
                return self._set_response(400, {})
            USERS_LIST.append(data)
            return self._set_response(201, data)

        elif self.path == "/user/createWithList":
        # список користувачів
            if not isinstance(data, list) or not all(valid_user(u) for u in data):
                return self._set_response(400, {})
            if any(u["id"] in [x["id"] for x in USERS_LIST] for u in data):
                return self._set_response(400, {})
            USERS_LIST.extend(data)
            return self._set_response(201, data)

        else:
            return self._set_response(404, {"error": "Not found"})

    

    def do_PUT(self):
        global USERS_LIST
        if not self.path.startswith("/user/"):
            return self._set_response(400, {"error": "not valid request data"})

        try:
            user_id = int(self.path.split("/")[-1])
        except:
            return self._set_response(400, {"error": "not valid request data"})

        try:
            data = self._pars_body()
        except:
            return self._set_response(400, {"error": "not valid request data"})

        required = ["username", "firstName", "lastName", "email", "password"]
        if not all(k in data for k in required):
            return self._set_response(400, {"error": "not valid request data"})

        user = next((u for u in USERS_LIST if u["id"] == user_id), None)
        if not user:
            return self._set_response(404, {"error": "User not found"})

        user.update(data)
        return self._set_response(200, user)


    def do_DELETE(self):
        global USERS_LIST
        if not self.path.startswith("/user/"):
            return self._set_response(404, {"error": "User not found"})

        try:
            user_id = int(self.path.split("/")[-1])
        except:
            return self._set_response(404, {"error": "User not found"})

        for i, u in enumerate(USERS_LIST):
            if u["id"] == user_id:
                USERS_LIST.pop(i)
                return self._set_response(200, {})
        return self._set_response(404, {"error": "User not found"})



def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, host='localhost', port=8000):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
