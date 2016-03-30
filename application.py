from robot.world import *

from model.pythonresponsegridblock import PythonResponseGridBlock
from model.responsegrid import *
import threading
import time
import json
import StringIO
import numpy as np
import math

class Ultrasonic:
    def __init__(self, builder, block_res=64, block_side=4.0, directions=1):
        builder.buildVehicle(size=(0.5, 1.0), position=[0.0, 0.0], rotation=0.0)

        proto = PythonResponseGridBlock(block_res, directions)
        builder.buildGrid(ResponseGrid(block_side, proto))

        self.world = builder.finish()
        self.prevRange = [-1] * len(self.world.vehicle.sensors)

    def update(self, position, rotation):
        """
            Обновление карты по новой позиции и повороте (рад)
        """

        self.world.vehicle.rotation = rotation
        self.world.vehicle.position = position

        for i, sensor in enumerate(self.world.vehicle.sensors):
            self.prevRange[i] = sensor.lastRange

            r = sensor.measure()

            if r < sensor.maxRange:
                self.world.grid.update(self.world.vehicle.position, sensor.rotation + sensor.vehicle.rotation, r, sensor.angle, False)
            else:
                self.world.grid.update(self.world.vehicle.position, sensor.rotation + sensor.vehicle.rotation, r, sensor.angle, True)

        self.world.update()

    def state(self):
        """
            Возвращает состояние в виде словаря
        """

        sides = ['l', 'f', 'r', 'b']

        cur = {sides[i] : s.lastRange for i,s in enumerate(self.world.vehicle.sensors)}
        prev = {sides[i] : self.prevRange[i] for i,s in enumerate(self.world.vehicle.sensors)}

        for c in [cur, prev]:
            for s in sides:
                if not s in c.keys():
                    c[s] = -1

        return {
            'name' : 'Ультразвуковые дальномеры',
            'cur_range' : cur,
            'prev_range' : prev,
            'state' : 'ok'
        }

    def getmap(self):
        """
            Возвращает карту пространства в виде двумерного массива байтов numpy
        """

        dx = self.world.vehicle.position[0] / self.world.grid.blockSize
        dy = self.world.vehicle.position[1] / self.world.grid.blockSize
        sx = 1 if dx > 0 and modf(dx)[0] > 0.5 or dx < 0 and modf(abs(dx))[0] < 0.5 else -1
        sy = 1 if dy > 0 and modf(dy)[0] > 0.5 or dy < 0 and modf(abs(dy))[0] < 0.5 else -1

        pd = [
            (0, 0), (sx, 0),
            (0, sy), (sx, sy)
        ]

        black = np.zeros((self.world.grid.blockProto().side,)*2, dtype=np.uint8)

        opos = self.world.grid.blockPosAt(self.world.vehicle.position)
        images = []
        for p in pd:
            pos = (opos[0] + p[0], opos[1] + p[1])
            if pos in self.world.grid.blocks:
                images.append(np.require(self.world.grid.blocks[pos].poData() * 0xff, np.uint8, 'C'))
            else:
                images.append(black)

        if sy > 0:
            images[0],images[2] = images[2],images[0]
            images[1],images[3] = images[3],images[1]

        if sx < 0:
            images[0],images[1] = images[1],images[0]
            images[2],images[3] = images[3],images[2]

        array = np.hstack((
            np.vstack((images[2], images[0])),
            np.vstack((images[3], images[1]))
        ))

        return array


class UpdateThread(threading.Thread):
    """
        Тред для сервера
    """
    def __init__(self, freq, app):
        threading.Thread.__init__(self)
        self.done = threading.Event()
        self.freq = freq
        self.lock = threading.Lock()
        self.app = app

    def run(self):
        while not self.done.wait(1.0/self.freq):
            with self.lock:
                self.app.update([0, 0], 0)

from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse

class handler(BaseHTTPRequestHandler):
    html = '''
        <html>
        <head>
            <meta charset="utf-8" />
            <meta http-equiv="Cache-Control" content="no-cache">
            <title> {name} </title>
        </head>
        <body>

            <b>Текущие показания:</b> <br/>
                 left = <span id="rf_cur_left">{cur_range[l]}</span> м; <br/>
                 right = <span id="rf_cur_right">{cur_range[r]}</span> м; <br/>
                 front = <span id="rf_cur_front">{cur_range[f]}</span> м; <br/>
                 back = <span id="rf_cur_back">{cur_range[b]}</span> м; <br/>
            <br/> <br/>

            <b>Предыдущие показания:</b> <br/>
                 left = <span id="rf_prev_left">{prev_range[l]}</span> м; <br/>
                 right = <span id="rf_prev_right">{prev_range[r]}</span> м;<br/>
                 front = <span id="rf_prev_front">{prev_range[f]}</span> м; <br/>
                 back = <span id="rf_prev_back">{prev_range[b]}</span> м; <br/>
            <br/> <br/>

            <b>Статус: </b>
                <span id="rf_state"> {state} </span>
            <br />
            <div style="position: absolute; right: 50px; top: 20px;">
                <b>Карта: </b> <br />
                <img id="map" width="256" height="256" />
            </div>
            <script type='text/javascript'>

                function $(id) {{ return document.getElementById(id); }}
                function img() {{
                    $('map').src = '/?img' + Math.random();
                }}
                function update() {{
                    var xmlhttp = new XMLHttpRequest();
                    xmlhttp.open("GET", "/?state");
                    xmlhttp.onreadystatechange = function() {{
                            if (xmlhttp.readyState == 4) {{
                                    if (xmlhttp.status == 200) {{
                                        state = JSON.parse(xmlhttp.responseText);

                                        $('rf_cur_left').innerHTML =  state.cur_range.l.toFixed(2);
                                        $('rf_cur_right').innerHTML = state.cur_range.r.toFixed(2);
                                        $('rf_cur_front').innerHTML = state.cur_range.f.toFixed(2);
                                        $('rf_cur_back').innerHTML =  state.cur_range.b.toFixed(2);

                                        $('rf_prev_left').innerHTML =  state.prev_range.l.toFixed(2);
                                        $('rf_prev_right').innerHTML = state.prev_range.r.toFixed(2);
                                        $('rf_prev_front').innerHTML = state.prev_range.f.toFixed(2);
                                        $('rf_prev_back').innerHTML =  state.prev_range.b.toFixed(2);

                                        $('rf_state').innerHTML = state.state;
                                    }}
                            }}
                    }}
                    xmlhttp.send(null);
                }}
                window.setInterval("update();", 1000);
                window.setInterval('img();', 1500);
            </script>
        </body>
        </html>
    '''

    def do_GET(self):
        path = urlparse.urlparse(self.path)

        self.send_response(200)

        if path.query == 'state':
            self.end_headers()
            with thread.lock: self.wfile.write(json.dumps(thread.app.state()))
        elif path.query.startswith('img'):
            import scipy.misc

            fp = StringIO.StringIO()
            with thread.lock:
                data = thread.app.getmap()
                scipy.misc.imsave(fp, data, 'png')

            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length',len(fp.getvalue()))
            self.end_headers()
            self.wfile.write(fp.getvalue())
        else:
            self.end_headers()

            with thread.lock:
                self.wfile.write(self.html.format(**thread.app.state()))

        return

def server():
    builder = RobotWorldBuilder()

    builder.port = '/dev/ttyUSB0'

    builder.buildSensor([0.0, 0.5], pi/2)
    '''
    builder.buildSensor([0.0, -0.5], -pi/2)
    builder.buildSensor([0.25, 0], 0)
    builder.buildSensor([-0.25, 0], pi)
    '''

    app = Ultrasonic(builder)
    global thread

    thread = UpdateThread(10, app)
    thread.start()

    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('localhost', 8080), handler)

    try:
        server.serve_forever()
    finally:
        thread.done.set()

if __name__ == "__main__":
    server()
