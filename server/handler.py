from http.server import BaseHTTPRequestHandler
import re
import mimetypes
import os
import json
from io import BytesIO
import scipy.misc


__all__ = ["RequestHandler"]


def route(pattern, method='GET'):
    def wrap(f):
        f.route = (pattern, method)
        return f
    return wrap


class RequestHandler(BaseHTTPRequestHandler):
    data_path = 'server/data'

    @route('/api/get_distances')
    def get_state(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        dists = self.server.update_thread.ultrasonic.get_distances()
        text = json.dumps(dists)

        self.wfile.write(text.encode('utf-8'))

    @route('/api/get_obstacles')
    def get_obstacles(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        with self.server.update_thread.lock:
            obstacles = self.server.update_thread.ultrasonic.get_obstacles()

        text = json.dumps(obstacles)

        self.wfile.write(text.encode('utf-8'))

    @route('/api/get_range_log')
    def get_range_log(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        with self.server.update_thread.lock:
            range_log = self.server.update_thread.ultrasonic.get_range_log()

        text = json.dumps(range_log)

        self.wfile.write(text.encode('utf-8'))

    @route('/api/get_objects')
    def get_objects(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write('hello'.encode('utf-8'))

    @route('/api/camera_scan', method='POST')
    def camera_scan(self):
        length = int(self.headers.get('Content-Length'))
        text = self.rfile.read(length).decode('utf-8')

        try:
            obj = json.loads(text)
        except json.JSONDecodeError as error:
            self.send_error_json(400, 'JSON parsing error: {0} {1},{2}'.format(error.msg, error.lineno, error.colno))
            return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write('hello'.encode('utf-8'))

    @route('/api/get_grid/[0-9\.]+')
    def get_grid(self):
        """
            Возвращает карту окружающего пространства

            :return: png картинка с картой
        """

        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()

        fp = BytesIO()
        with self.server.update_thread.lock:
            grid = self.server.update_thread.ultrasonic.get_grid()
            scipy.misc.imsave(fp, grid['grid'], 'png')

        self.wfile.write(fp.getvalue())

    @route('/api/get_grid_info')
    def get_grid_info(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        with self.server.update_thread.lock:
            grid = self.server.update_thread.ultrasonic.get_grid()

        grid.pop('grid')
        text = json.dumps(grid)

        self.wfile.write(text.encode('utf-8'))

    @route('/[^/]*')
    def static(self):
        """
            Обработка статических вайлов (html, css, js, etc)
            в директории 'data/'
        """

        path = self.path

        if path == '/':
            path = '/index.html'

        file_path = self.data_path + path

        if not os.path.exists(file_path):
            self.send_error(404, 'No such path: {0}'.format(path))
            return

        self.send_response(200)
        mime, _ = mimetypes.guess_type(os.path.abspath(file_path))
        self.send_header('Content-type', mime)
        self.end_headers()

        with open(file_path, 'rb') as file:
            self.wfile.write(file.read())

    def send_error_json(self, code, msg, data=dict()):
        self.send_response(code)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

        error = data.copy()
        error['message'] = msg

        text = dict(error=error)

        self.wfile.write(json.dumps(text).encode('utf-8'))

    def handle_request(self, method):
        for k, v in type(self).__dict__.items():
            is_routed_method = callable(v) and hasattr(v, 'route') and v.route[1] == method

            if is_routed_method and re.fullmatch(v.route[0], self.path) is not None:
                v(self)

                return

        self.send_error(404, 'No such path: {0}'.format(self.path))

    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')
