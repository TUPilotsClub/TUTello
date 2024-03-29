# coding=utf-8
import logging
import socket
import time
import threading
import cv2
import sys
from threading import Thread
from .decorators import accepts


class Tello:
    """Python wrapper to interact with the Ryze Tello drone using the official Tello api.
    Tello API documentation:
    https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf
    """
    # Send and receive commands, client socket
    UDP_IP = '192.168.10.1'
    UDP_PORT = 8889
    RESPONSE_TIMEOUT = 7  # in seconds
    TIME_BTW_COMMANDS = 1  # in seconds
    TIME_BTW_RC_CONTROL_COMMANDS = 0.5  # in seconds
    RETRY_COUNT = 3
    last_received_command = time.time()

    HANDLER = logging.StreamHandler(sys.stdout)
    FORMATTER = logging.Formatter('%(filename)s - %(lineno)d - %(message)s')
    HANDLER.setFormatter(FORMATTER)

    LOGGER = logging.getLogger('drone')

    LOGGER.addHandler(HANDLER)
    LOGGER.setLevel(logging.INFO)
    # use logging.getLogger('drone').setLevel(logging.<LEVEL>) in YOUR CODE
    # to only receive logs of the desired level and higher

    # Video stream, server socket
    VS_UDP_IP = '0.0.0.0'
    VS_UDP_PORT = 11111

    STATE_UDP_PORT = 8890

    # VideoCapture object
    cap = None
    background_frame_read = None

    stream_on = False

    is_flying = False

    # Tello state
    pitch = -1
    roll = -1
    yaw = -1
    speed_x = -1
    speed_y = -1
    speed_z = -1
    temperature_lowest = -1
    temperature_highest = -1
    distance_tof = -1
    height = -1
    battery = -1
    barometer = -1.0
    flight_time = -1.0
    acceleration_x = -1.0
    acceleration_y = -1.0
    acceleration_z = -1.0
    attitude = {'pitch': -1, 'roll': -1, 'yaw': -1}

    def __init__(self,
                 host='192.168.10.1',
                 port=8889,
                 client_socket=None,
                 enable_exceptions=True,
                 retry_count=3):

        self.address = (host, port)
        self.response = None
        self.response_state = None  # to attain the response of the states
        self.stream_on = False
        self.enable_exceptions = enable_exceptions
        self.retry_count = retry_count

        if client_socket:
            self.clientSocket = client_socket
        else:
            self.clientSocket = socket.socket(socket.AF_INET,  # Internet
                                              socket.SOCK_DGRAM)  # UDP
            self.clientSocket.bind(('', self.UDP_PORT))  # For UDP response (receiving data)

        self.stateSocket = socket.socket(socket.AF_INET,
                                         socket.SOCK_DGRAM)
        self.stateSocket.bind(('', self.STATE_UDP_PORT))  # for accessing the states of Tello

        # Run tello udp receiver on background
        thread1 = threading.Thread(target=self.run_udp_receiver, args=())
        # Run state reciever on background
        thread2 = threading.Thread(target=self.get_states, args=())

        thread1.daemon = True
        thread2.daemon = True
        thread1.start()
        thread2.start()

    def run_udp_receiver(self):
        """Setup drone UDP receiver. This method listens for responses of Tello. Must be run from a background thread
        in order to not block the main thread."""
        while True:
            try:
                self.response, _ = self.clientSocket.recvfrom(1024)  # buffer size is 1024 bytes
            except Exception as e:
                self.LOGGER.error(e)
                break

    def get_states(self):
        """This runs on background to recieve the state of Tello"""
        while True:
            try:
                self.response_state, _ = self.stateSocket.recvfrom(256)
                #self.LOGGER.info(self.response_state)
                if self.response_state != 'ok':
                    self.response_state = self.response_state.decode('ASCII')
                    #list = self.response_state.replace(';', ':').split(':')
                    key_pairs = [expr.split(':') for expr in self.response_state.split(';')]
                    list = { pair[0] : pair[1] for pair in key_pairs if len(pair) == 2}
                    #self.LOGGER.info(list)
                    '''self.pitch = int(list[1])
                    self.roll = int(list[3])
                    self.yaw = int(list[5])
                    self.speed_x = int(list[7])
                    self.speed_y = int(list[9])
                    self.speed_z = int(list[11])
                    self.temperature_lowest = int(list[13])
                    self.temperature_highest = int(list[15])
                    self.distance_tof = int(list[17])
                    self.height = int(list[19])
                    self.battery = int(list[21])
                    self.barometer = float(list[23])
                    self.flight_time = float(list[25])
                    self.acceleration_x = float(list[27])
                    self.acceleration_y = float(list[29])
                    self.acceleration_z = float(list[31])
                    self.attitude = {'pitch': int(list[1]), 'roll': int(list[3]), 'yaw': int(list[5])}'''
                    self.pitch = list['pitch']
                    self.roll = list['roll']
                    self.yaw = list['yaw']
                    self.speed_x = list['vgx']
                    self.speed_y = list['vgy']
                    self.speed_z = list['vgz']
                    self.temperature_lowest = list['templ']
                    self.temperature_highest = list['temph']
                    self.distance_tof = list['tof']
                    self.height = list['h']
                    self.battery = list['bat']
                    self.barometer = list['baro']
                    self.flight_time = list['time']
                    self.acceleration_x = list['agx']
                    self.acceleration_y = list['agy']
                    self.acceleration_z = list['agz']
                    
            except Exception as e:
                self.LOGGER.error(e)
                self.LOGGER.error(f"Response was is {self.response_state}")
                break

    def get_udp_video_address(self):
        return 'udp://@' + self.VS_UDP_IP + ':' + str(self.VS_UDP_PORT)  # + '?overrun_nonfatal=1&fifo_size=5000'

    def get_video_capture(self):
        """Get the VideoCapture object from the camera drone
        Returns:
            VideoCapture
        """

        if self.cap is None:
            self.cap = cv2.VideoCapture(self.get_udp_video_address())

        if not self.cap.isOpened():
            self.cap.open(self.get_udp_video_address())

        return self.cap

    def get_frame_read(self):
        """Get the BackgroundFrameRead object from the camera drone. Then, you just need to call
        backgroundFrameRead.frame to get the actual frame received by the drone.
        Returns:
            BackgroundFrameRead
        """
        if self.background_frame_read is None:
            self.background_frame_read = BackgroundFrameRead(self, self.get_udp_video_address()).start()
        return self.background_frame_read

    def stop_video_capture(self):
        return self.streamoff()

    @accepts(command=str, printinfo=bool, timeout=int)
    def send_command_with_return(self, command, printinfo=True, timeout=RESPONSE_TIMEOUT):
        """Send command to Tello and wait for its response.
        Return:
            bool: True for successful, False for unsuccessful
        """
        # Commands very consecutive makes the drone not respond to them. So wait at least self.TIME_BTW_COMMANDS seconds
        diff = time.time() * 1000 - self.last_received_command
        if diff < self.TIME_BTW_COMMANDS:
            time.sleep(diff)

        if printinfo:
            self.LOGGER.info('Send command: ' + command)
        timestamp = int(time.time() * 1000)

        self.clientSocket.sendto(command.encode('utf-8'), self.address)

        while self.response is None:
            if (time.time() * 1000) - timestamp > timeout * 1000:
                self.LOGGER.warning('Timeout exceed on command ' + command)
                return False

        try:
            response = self.response.decode('utf-8').rstrip("\r\n")
        except UnicodeDecodeError as e:
            self.LOGGER.error(e)
            return None

        if printinfo:
            self.LOGGER.info(f'Response {command}: {response}')

        self.response = None

        self.last_received_command = time.time() * 1000

        return response

    @accepts(command=str)
    def send_command_without_return(self, command):
        """Send command to Tello without expecting a response. Use this method when you want to send a command
        continuously
            - go x y z speed: Tello fly to x y z in speed (cm/s)
                x: 20-500
                y: 20-500
                z: 20-500
                speed: 10-100
            - curve x1 y1 z1 x2 y2 z2 speed: Tello fly a curve defined by the current and two given coordinates with
                speed (cm/s). If the arc radius is not within the range of 0.5-10 meters, it responses false.
                x/y/z can’t be between -20 – 20 at the same time .
                x1, x2: 20-500
                y1, y2: 20-500
                z1, z2: 20-500
                speed: 10-60
            - rc a b c d: Send RC control via four channels.
                a: left/right (-100~100)
                b: forward/backward (-100~100)
                c: up/down (-100~100)
                d: yaw (-100~100)
        """
        # Commands very consecutive makes the drone not respond to them. So wait at least self.TIME_BTW_COMMANDS seconds

        self.LOGGER.info('Send command (no expect response): ' + command)
        self.clientSocket.sendto(command.encode('utf-8'), self.address)

    @accepts(command=str, timeout=int)
    def send_control_command(self, command, timeout=RESPONSE_TIMEOUT):
        """Send control command to Tello and wait for its response. Possible control commands:
            - command: entry SDK mode
            - takeoff: Tello auto takeoff
            - land: Tello auto land
            - streamon: Set video stream on
            - streamoff: Set video stream off
            - emergency: Stop all motors immediately
            - up x: Tello fly up with distance x cm. x: 20-500
            - down x: Tello fly down with distance x cm. x: 20-500
            - left x: Tello fly left with distance x cm. x: 20-500
            - right x: Tello fly right with distance x cm. x: 20-500
            - forward x: Tello fly forward with distance x cm. x: 20-500
            - back x: Tello fly back with distance x cm. x: 20-500
            - cw x: Tello rotate x degree clockwise x: 1-3600
            - ccw x: Tello rotate x degree counter- clockwise. x: 1-3600
            - flip x: Tello fly flip x
                l (left)
                r (right)
                f (forward)
                b (back)
            - speed x: set speed to x cm/s. x: 10-100
            - wifi ssid pass: Set Wi-Fi with SSID password

        Return:
            bool: True for successful, False for unsuccessful
        """
        response = None
        for i in range(0, self.retry_count):
            response = self.send_command_with_return(command, timeout=timeout)

            if response == 'OK' or response == 'ok':
                return True

        return self.return_error_on_send_command(command, response, self.enable_exceptions)

    @accepts(command=str, printinfo=bool)
    def send_read_command(self, command, printinfo=True):
        """Send set command to Tello and wait for its response. Possible set commands:
            - speed?: get current speed (cm/s): x: 1-100
            - battery?: get current battery percentage: x: 0-100
            - time?: get current fly time (s): time
            - height?: get height (cm): x: 0-3000
            - temp?: get temperature (°C): x: 0-90
            - attitude?: get IMU attitude data: pitch roll yaw
            - baro?: get barometer value (m): x
            - tof?: get distance value from TOF (cm): x: 30-1000
            - wifi?: get Wi-Fi SNR: snr

        Return:
            bool: The requested value for successful, False for unsuccessful
        """

        response = self.send_command_with_return(command, printinfo=printinfo)

        try:
            response = str(response)
        except TypeError as e:
            self.LOGGER.error(e)
            pass

        if ('error' not in response) and ('ERROR' not in response) and ('False' not in response):
            if response.isdigit():
                return int(response)
            else:
                try:
                    return float(response)  # isdigit() is False when the number is a float(barometer)
                except ValueError:
                    return response
        else:
            return self.return_error_on_send_command(command, response, self.enable_exceptions)

    def return_error_on_send_command(self, command, response, enable_exceptions):
        """Returns False and print an informative result code to show unsuccessful response"""
        msg = 'Command ' + command + ' was unsuccessful. Message: ' + str(response)
        if enable_exceptions:
            raise Exception(msg)
        else:
            self.LOGGER.error(msg)
            return False

    def connect(self):
        """Entry SDK mode
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("command")

    def takeoff(self):
        """Tello auto takeoff
        Returns:
            bool: True for successful, False for unsuccessful
            False: Unsuccessful
        """
        # Something it takes a looooot of time to take off and return a succesful take off. So we better wait. If not, is going to give us error on the following calls.
        if self.send_control_command("takeoff", timeout=20):
            self.is_flying = True
            return True
        else:
            return False

    def land(self):
        """Tello auto land
        Returns:
            bool: True for successful, False for unsuccessful
        """
        if self.send_control_command("land"):
            self.is_flying = False
            return True
        else:
            return False

    def streamon(self):
        """Set video stream on. If the response is 'Unknown command' means you have to update the Tello firmware. That
        can be done through the Tello app.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        result = self.send_control_command("streamon")
        if result is True:
            self.stream_on = True
        return result

    def streamoff(self):
        """Set video stream off
        Returns:
            bool: True for successful, False for unsuccessful
        """
        result = self.send_control_command("streamoff")
        if result is True:
            self.stream_on = False
        return result

    def emergency(self):
        """Stop all motors immediately
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("emergency")

    @accepts(direction=str, x=int)
    def move(self, direction, x):
        """Tello fly up, down, left, right, forward or back with distance x cm.
        Arguments:
            direction: up, down, left, right, forward or back
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command(direction + ' ' + str(x))

    @accepts(x=int)
    def move_up(self, x):
        """Tello fly up with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("up", x)

    @accepts(x=int)
    def move_down(self, x):
        """Tello fly down with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("down", x)

    @accepts(x=int)
    def move_left(self, x):
        """Tello fly left with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("left", x)

    @accepts(x=int)
    def move_right(self, x):
        """Tello fly right with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("right", x)

    @accepts(x=int)
    def move_forward(self, x):
        """Tello fly forward with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("forward", x)

    @accepts(x=int)
    def move_back(self, x):
        """Tello fly back with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("back", x)

    @accepts(x=int)
    def rotate_clockwise(self, x):
        """Tello rotate x degree clockwise.
        Arguments:
            x: 1-360

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("cw " + str(x))

    @accepts(x=int)
    def rotate_counter_clockwise(self, x):
        """Tello rotate x degree counter-clockwise.
        Arguments:
            x: 1-3600

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("ccw " + str(x))

    @accepts(x=str)
    def flip(self, direction):
        """Tello fly flip.
        Arguments:
            direction: l (left), r (right), f (forward) or b (back)

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("flip " + direction)

    def flip_left(self):
        """Tello fly flip left.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.flip("l")

    def flip_right(self):
        """Tello fly flip left.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.flip("r")

    def flip_forward(self):
        """Tello fly flip left.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.flip("f")

    def flip_back(self):
        """Tello fly flip left.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.flip("b")

    @accepts(x=int, y=int, z=int, speed=int)
    def go_xyz_speed(self, x, y, z, speed):
        """Tello fly to x y z in speed (cm/s)
        Arguments:
            x: 20-500
            y: 20-500
            z: 20-500
            speed: 10-100
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_command_without_return('go %s %s %s %s' % (x, y, z, speed))

    @accepts(x1=int, y1=int, z1=int, x2=int, y2=int, z2=int, speed=int)
    def curve_xyz_speed(self, x1, y1, z1, x2, y2, z2, speed):
        """Tello fly a curve defined by the current and two given coordinates with speed (cm/s).
            - If the arc radius is not within the range of 0.5-10 meters, it responses false.
            - x/y/z can’t be between -20 – 20 at the same time.
        Arguments:
            x1: 20-500
            x2: 20-500
            y1: 20-500
            y2: 20-500
            z1: 20-500
            z2: 20-500
            speed: 10-60
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_command_without_return('curve %s %s %s %s %s %s %s' % (x1, y1, z1, x2, y2, z2, speed))

    @accepts(x=int, y=int, z=int, speed=int, mid=int)
    def go_xyz_speed_mid(self, x, y, z, speed, mid):
        """Tello fly to x y z in speed (cm/s) relative to mission pad iwth id mid
        Arguments:
            x: -500-500
            y: -500-500
            z: -500-500
            speed: 10-100
            mid: 1-8
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command('go %s %s %s %s m%s' % (x, y, z, speed, mid))

    @accepts(x1=int, y1=int, z1=int, x2=int, y2=int, z2=int, speed=int, mid=int)
    def curve_xyz_speed_mid(self, x1, y1, z1, x2, y2, z2, speed, mid):
        """Tello fly to x2 y2 z2 over x1 y1 z1 in speed (cm/s) relative to mission pad with id mid
        Arguments:
            x1: -500-500
            y1: -500-500
            z1: -500-500
            x2: -500-500
            y2: -500-500
            z2: -500-500
            speed: 10-60
            mid: 1-8
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command('curve %s %s %s %s %s %s %s m%s' % (x1, y1, z1, x2, y2, z2, speed, mid))

    @accepts(x=int, y=int, z=int, speed=int, yaw=int, mid1=int, mid2=int)
    def go_xyz_speed_yaw_mid(self, x, y, z, speed, yaw, mid1, mid2):
        """Tello fly to x y z in speed (cm/s) relative to mid1
        Then fly to 0 0 z over mid2 and rotate to yaw relative to mid2's rotation
        Arguments:
            x: -500-500
            y: -500-500
            z: -500-500
            speed: 10-100
            yaw: -360-360
            mid1: 1-8
            mid2: 1-8
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command('jump %s %s %s %s %s m%s m%s' % (x, y, z, speed, yaw, mid1, mid2))

    def enable_mission_pads(self):
        return self.send_control_command("mon")

    def disable_mission_pads(self):
        return self.send_control_command("moff")

    def set_mission_pad_detection_direction(self, x):
        return self.send_control_command("mdirection " + str(x))

    @accepts(x=int)
    def set_speed(self, x):
        """Set speed to x cm/s.
        Arguments:
            x: 10-100

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("speed " + str(x))

    last_rc_control_sent = 0

    @accepts(left_right_velocity=int, forward_backward_velocity=int, up_down_velocity=int, yaw_velocity=int)
    def send_rc_control(self, left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity):
        """Send RC control via four channels. Command is sent every self.TIME_BTW_RC_CONTROL_COMMANDS seconds.
        Arguments:
            left_right_velocity: -100~100 (left/right)
            forward_backward_velocity: -100~100 (forward/backward)
            up_down_velocity: -100~100 (up/down)
            yaw_velocity: -100~100 (yaw)
        Returns:
            bool: True for successful, False for unsuccessful
        """
        if int(time.time() * 1000) - self.last_rc_control_sent < self.TIME_BTW_RC_CONTROL_COMMANDS:
            pass
        else:
            self.last_rc_control_sent = int(time.time() * 1000)
            return self.send_command_without_return('rc %s %s %s %s' % (self.round_to_100(left_right_velocity),
                                                                        self.round_to_100(forward_backward_velocity),
                                                                        self.round_to_100(up_down_velocity),
                                                                        self.round_to_100(yaw_velocity)))

    @accepts(x=int)
    def round_to_100(self, x):
        if x > 100:
            return 100
        elif x < -100:
            return -100
        else:
            return x

    def set_wifi_credentials(self, ssid, password):
        """Set the Wi-Fi SSID and password. The Tello will reboot afterwords.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command('wifi %s %s' % (ssid, password))

    def connect_to_wifi(self, ssid, password):
        """Connects to the Wi-Fi with SSID and password.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command('ap %s %s' % (ssid, password))

    def get_speed(self):
        """Get current speed (cm/s)
        Returns:
            False: Unsuccessful
            int: 1-100
        """
        return self.send_read_command('speed?')

    def get_battery(self):
        """Get current battery percentage
        Returns:
            False: Unsuccessful
            int: -100
        """
        return self.send_read_command('battery?')

    def get_flight_time(self):
        """Get current fly time (s)
        Returns:
            False: Unsuccessful
            int: Seconds elapsed during flight.
        """
        return self.send_read_command('time?')

    def get_height(self):
        """Get height (cm)
        Returns:
            False: Unsuccessful
            int: 0-3000
        """
        return self.send_read_command('height?')

    def get_temperature(self):
        """Get temperature (°C)
        Returns:
            False: Unsuccessful
            int: 0-90
        """
        return self.send_read_command('temp?')

    def get_attitude(self):
        """Get IMU attitude data
        Returns:
            False: Unsuccessful
            int: pitch roll yaw
        """
        r = self.send_read_command('attitude?').replace(';', ':').split(':')
        return dict(zip(r[::2], [int(i) for i in r[1::2]]))  # {'pitch': xxx, 'roll': xxx, 'yaw': xxx}

    def get_barometer(self):
        """Get barometer value (m)
        Returns:
            False: Unsuccessful
            int: 0-100
        """
        return self.send_read_command('baro?')

    def get_distance_tof(self):
        """Get distance value from TOF (cm)
        Returns:
            False: Unsuccessful
            int: 30-1000
        """
        return self.send_read_command('tof?')

    def get_wifi(self):
        """Get Wi-Fi SNR
        Returns:
            False: Unsuccessful
            str: snr
        """
        return self.send_read_command('wifi?')

    def get_sdk_version(self):
        """Get SDK Version
        Returns:
            False: Unsuccessful
            str: SDK Version
        """
        return self.send_read_command('sdk?')

    def get_serial_number(self):
        """Get Serial Number
        Returns:
            False: Unsuccessful
            str: Serial Number
        """
        return self.send_read_command('sn?')

    def end(self):
        """Call this method when you want to end the tello object"""
        if self.stream_on:
            print("stream off")
            self.streamoff()
        if self.is_flying:
            print("tello land")
            self.land()
        if self.background_frame_read is not None:
            self.background_frame_read.stop()
        if self.cap is not None:
            self.cap.release()

    def __del__(self):
        self.end()


class BackgroundFrameRead:
    """
    This class read frames from a VideoCapture in background. Then, just call backgroundFrameRead.frame to get the
    actual one.
    """

    def __init__(self, tello, address):
        print("bfr init")
        tello.cap = cv2.VideoCapture(address)
        self.cap = tello.cap

        print("cap read")
        if not self.cap.isOpened():
            self.cap.open(address)
            print("opened")
        self.grabbed, self.frame = self.cap.read()
        self.stopped = False
        print("bfr init done")

    def start(self):
        print("bfr start")
        thread = Thread(target=self.update_frame, args=())
        thread.Daemon = True
        thread.start()
        print("bfr start done")
        return self

    def update_frame(self):
        while not self.stopped:
            if not self.grabbed or not self.cap.isOpened():
                self.stop()
            else:
                (self.grabbed, self.frame) = self.cap.read()

    def stop(self):
        self.stopped = True
