import datetime
import json
import struct
import serial

need_to_exit = False

Status = dict(
    state='normal op',
    port=None,
    errors=0,
    packets=0,
)

D4C = dict(
    signature=15,
    C=0.0, T=0.0, R=0.0,
    C0 = 0, T0 = 0, R0 = 0,
    t=datetime.datetime.now().__str__()
)

D70 = dict(
    signature=55, # (55, 112)
    ask="AAAA08407014000000C0A6",
    C=0.0, T=0.0, R=0.0,
    C0 = 0, T0 = 0, R0 = 0,
    Ax=0.0, Ay=0.0, Az=0.0,
    Wx=0.0, Wy=0.0, Wz=0.0,
    t=datetime.datetime.now().__str__()
)

D72 = D4C

def open_bins_port():
    global BINSport
    try:
        BINSport = serial.Serial(
            port=json.load(open('/home/mismp/.bins.json.conf'))['port'],
            baudrate=460800,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=5,
        )
        Status['port'] = BINSport.port
    except (FileNotFoundError, serial.serialutil.SerialException) as e:
        BINSport = None
        Status['port'] = BINSport
        Status['state'] = str(e)

from filter import DriftFilter, Filter
import math
import time
course_filter = DriftFilter(5.0, 2000)
initial_time = time.time()
last_log_time = initial_time
open("/tmp/log_c", "w").close()
open("/tmp/log_t", "w").close()
open("/tmp/log_r", "w").close()
open("/tmp/log_Wy", "w").close()

def set_zero():
    D4C["C0"] = D4C["C"]
    D4C["T0"] = D4C["T"]
    D4C["R0"] = D4C["R"]

def read4c_packet():
    global last_log_time


    crc = ord(BINSport.read())

    current_time = time.time()
    object_moves = current_time - initial_time > 5.0
    
    raw_course = struct.unpack('<f', BINSport.read(4))[0]
    raw_course = math.radians(raw_course)

    course = \
        course_filter.clean_angle(
            angle            = raw_course,
            time             = current_time,
            is_object_moving = not object_moves
        )
    course = math.degrees(course) - D4C["C0"]

    D4C['C'] = course
    D4C['T'] = struct.unpack('<f', BINSport.read(4))[0] - D4C["T0"]
    D4C['R'] = struct.unpack('<f', BINSport.read(4))[0] - D4C["R0"]
    D4C['t'] = datetime.datetime.now().__str__()
    
    if current_time - last_log_time > 0.05:
        with open("/tmp/log_c", "a") as f:
            f.write("%s, %s, %s\n" % (
                current_time - initial_time,
                math.degrees(raw_course) - D4C["C0"],
                D4C['C']
            ))
            
        with open("/tmp/log_t", "a") as f:
            f.write("%s, %s\n" % (
                current_time - initial_time,
                D4C['T']
            ))
            
        with open("/tmp/log_r", "a") as f:
            f.write("%s, %s\n" % (
                current_time - initial_time,
                D4C['R']
            ))
            
        last_log_time = current_time

def update_status(err=False, pkt=False, tmo=False, state=None):
    global Status

    if err:
        Status['errors'] += 1
        if Status['errors'] >= 65535: Status['errors'] = 0
    elif pkt:
        Status['packets'] += 1
        if Status['packets'] >= 65535: Status['packets'] = 0
    elif tmo:
        state = 'timeout'

    if state is not None:
        Status['state'] = state
    else:
        Status['state'] = 'normal op'


course_filter_70 = DriftFilter(5.0, 2000)
Wy_filter = Filter(5.0, 2000)
Wy_last_time = time.time()
Wy_log_time = Wy_last_time
def read70packet():
    global Wy_last_time, Wy_log_time


    crc = ord(BINSport.read())

    BINSport.read(4)

    D70['Ax'] = struct.unpack('<f', BINSport.read(4))[0]
    D70['Ay'] = struct.unpack('<f', BINSport.read(4))[0]
    D70['Az'] = struct.unpack('<f', BINSport.read(4))[0]

    D70['Wx'] = struct.unpack('<f', BINSport.read(4))[0]
    D70['Wy'] = struct.unpack('<f', BINSport.read(4))[0]
    D70['Wz'] = struct.unpack('<f', BINSport.read(4))[0]
    current_time = time.time()
    Wy_filter.push_value(D70['Wx'], current_time - Wy_last_time)
    Wy_last_time = current_time
    if current_time - Wy_log_time > 1:
        with open("/tmp/log_Wy", "a") as log:
            log.write(
                "%s %s %s\n" % \
                    (current_time - initial_time,
                        D70['Wx'],
                        Wy_filter.get_filtered_value())
            )
        Wy_log_time = current_time

    current_time = time.time()
    object_moves = True #current_time - initial_time > 5.0

    raw_course = struct.unpack('<f', BINSport.read(4))[0]
    raw_course = math.radians(raw_course)

    course = \
        course_filter_70.clean_angle(
            angle            = raw_course,
            time             = current_time,
            is_object_moving = not object_moves
        )
    course = math.degrees(course) - D70["C0"]

    D70['C'] = course
    D70['T'] = struct.unpack('<f', BINSport.read(4))[0] - D70["T0"]
    D70['R'] = struct.unpack('<f', BINSport.read(4))[0] - D70["R0"]
    D70['t'] = datetime.datetime.now().__str__()

    BINSport.read(12)


def ask_packet(packet_id):
    if packet_id == "70":
        BINSport.write(bytes.fromhex(D70["ask"]))

def read_packet(echo = False):
    global Status
    sync = 170  # AAh
    while not need_to_exit:
        T0 = datetime.datetime.now()
        try:
            while 1:
                if ord(BINSport.read()) == sync:
                    if ord(BINSport.read()) == sync:
                        break
            test_byte = ord(BINSport.read())
            if test_byte == D4C['signature']:  # (ord(BINSport.read()),ord(BINSport.read()))
                read4c_packet()
                if echo:
                    print(D4C)
                update_status(pkt=True)
                if echo:
                    print(Status)
            elif test_byte == D70['signature']: #(ord(BINSport.read()),ord(BINSport.read())) == D70.signature:
                # print(1, ord(BINSport.read()))
                read70packet()
                #        if (ord(BINSport.read()),ord(BINSport.read())) == D72.signature:
                #        	read72packet()
                if echo:
                    print(D70)
                update_status(pkt=True)
                if echo:
                    print(Status)
            else:
                # print(2, ord(BINSport.read()))
                update_status(err=True)
                if echo:
                    print(Status)
        except Exception as e:
            print(e)
            update_status(err=True, state=str(e))
            if echo:
                print(Status)

        if (datetime.datetime.now() - T0).microseconds > 4000:
            update_status(tmo=True)
            if echo:
                print(Status)
            
if __name__ == "__main__":
    open_bins_port()
    ask_packet("70")
    while True:
        read_packet(True)
        
