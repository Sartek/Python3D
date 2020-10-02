"""XINPUT wrapper for windows

This module provides support for accessing xinput devices by both event and state on windows.
This module is normally used in the following way

import xinput
xinputmanager = XInputManager()
events = xinputmanager.get_events()

other examples can be found at the bottom of this file
"""

__version__ = '0.1'
__author__ = 'Andrew Richards'

import time
import queue

import ctypes

import mmtimer

class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ('buttons', ctypes.c_ushort),       # wButtons
        ('left_trigger', ctypes.c_ubyte),   # bLeftTrigger
        ('right_trigger', ctypes.c_ubyte),  # bRightTrigger
        ('l_thumb_x', ctypes.c_short),      # sThumbLX
        ('l_thumb_y', ctypes.c_short),      # sThumbLY
        ('r_thumb_x', ctypes.c_short),      # sThumbRx
        ('r_thumb_y', ctypes.c_short),      # sThumbRy
    ]


class XINPUT_STATE(ctypes.Structure):
    _fields_ = [
        ('packet_number', ctypes.c_ulong),  # dwPacketNumber
        ('gamepad', XINPUT_GAMEPAD),        # Gamepad
    ]


class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [
                ('wLeftMotorSpeed', ctypes.c_ushort),
                ('wRightMotorSpeed', ctypes.c_ushort)
    ]

class XINPUT_BATTERY_INFORMATION(ctypes.Structure):
    _fields_ = [
                ('BatteryType', ctypes.c_ubyte),
                ('BatteryLevel', ctypes.c_ubyte)
    ]

class UnpluggedError(RuntimeError):
    """The device requested is not plugged in."""
    pass

class XINPUTDLLNOTFOUND(RuntimeError):
    """Could not find an xinput dll"""
    pass

ERROR_DEVICE_NOT_CONNECTED = 1167
ERROR_SUCCESS = 0

XINPUT_DLL_NAMES = (
    #'XInputUap.dll',
    'XInput1_4.dll',
    'XInput9_1_0.dll',
    'XInput1_3.dll',
    'XInput1_2.dll',
    'XInput1_1.dll'
)

XINPUT_BITMASKS = {
    'XINPUT_GAMEPAD_DPAD_UP':       0x0001,
    'XINPUT_GAMEPAD_DPAD_DOWN':     0x0002,
    'XINPUT_GAMEPAD_DPAD_LEFT':     0x0004,
    'XINPUT_GAMEPAD_DPAD_RIGHT':    0x0008,
    'XINPUT_GAMEPAD_START':         0x0010,
    'XINPUT_GAMEPAD_BACK':          0x0020,
    'XINPUT_GAMEPAD_LEFT_THUMB':    0x0040,
    'XINPUT_GAMEPAD_RIGHT_THUMB':   0x0080,
    'XINPUT_GAMEPAD_LEFT_SHOULDER': 0x0100,
    'XINPUT_GAMEPAD_RIGHT_SHOULDER':0x0200,
    'XINPUT_GAMEPAD_A':             0x1000,
    'XINPUT_GAMEPAD_B':             0x2000,
    'XINPUT_GAMEPAD_X':             0x4000,
    'XINPUT_GAMEPAD_Y':             0x8000
}

XINPUT_GENERIC_NAMES = {
    'XINPUT_GAMEPAD_DPAD_UP':       'ABS_HAT0Y',
    'XINPUT_GAMEPAD_DPAD_DOWN':     'ABS_HAT0Y',
    'XINPUT_GAMEPAD_DPAD_LEFT':     'ABS_HAT0X',
    'XINPUT_GAMEPAD_DPAD_RIGHT':    'ABS_HAT0X',
    'XINPUT_GAMEPAD_START':         'ABS_START',
    'XINPUT_GAMEPAD_BACK':          'ABS_SELECT',
    'XINPUT_GAMEPAD_LEFT_THUMB':    'BTN_THUMBL',
    'XINPUT_GAMEPAD_RIGHT_THUMB':   'BTN_THUMBR',
    'XINPUT_GAMEPAD_LEFT_SHOULDER': 'BTN_TL',
    'XINPUT_GAMEPAD_RIGHT_SHOULDER':'BTN_TR',
    'XINPUT_GAMEPAD_A':             'BTN_SOUTH',
    'XINPUT_GAMEPAD_B':             'BTN_EAST',
    'XINPUT_GAMEPAD_X':             'BTN_WEST',
    'XINPUT_GAMEPAD_Y':             'BTN_NORTH'
}


XINPUT_DLL = None
XINPUT = None

for dll in XINPUT_DLL_NAMES:
    try:
        XINPUT = getattr(ctypes.windll, dll)
    except OSError:
        pass
    else:
        # We found an xinput driver
        XINPUT_DLL = dll
        break
else:
    # We didn't find an xinput library
    raise XINPUTDLLNOTFOUND("we couldn't find xinput dll")
        
class InputEvent():
    """Class representing an input event"""
    def __init__ (self, code, timestamp, ev_type, value, device):
        self.code = code
        self.timestamp = timestamp
        self.ev_type = ev_type
        self.state = value
        self.device = 'xinput_%d' % device
        
def toButtons(state):
    """Converts an xinput states packed buttons into a dict of seperate values"""
    data = {}
    for key in XINPUT_BITMASKS:
        data[key] = int(
            (state.gamepad.buttons & XINPUT_BITMASKS[key])
            / XINPUT_BITMASKS[key])
    return data
def toSimpleState(state):
    """Converts a ctypes controller state into a dict"""
    data = {}
    buttons = toButtons(state)
    for button in buttons:
        data[button[7:]] = buttons[button]
    data['GAMEPAD_LEFT_TRIGGER'] = state.gamepad.left_trigger
    data['GAMEPAD_RIGHT_TRIGGER'] = state.gamepad.right_trigger
    data['GAMEPAD_LEFT_X'] = state.gamepad.l_thumb_x
    data['GAMEPAD_LEFT_Y'] = state.gamepad.l_thumb_y
    data['GAMEPAD_RIGHT_X'] = state.gamepad.r_thumb_x
    data['GAMEPAD_RIGHT_Y'] = state.gamepad.r_thumb_y
    return data

def addToQueue(eventQueue, data):
    """adds an event to the queue - called by the update thread"""
    if eventQueue.full():
        #print('Event queue is full!!!')
        eventQueue.get()
        eventQueue.task_done()
    eventQueue.put(data)

def stateToEvents(device, state, laststate, timestamp, eventQueue):
    """Turns a ctypes controller state and its last state into events"""
    buttons = toButtons(state)
    last_buttons = toButtons(laststate)
    events = []
    for key in buttons:
        event = None
        if key == 'XINPUT_GAMEPAD_DPAD_UP':
            if buttons[key] != last_buttons[key]:
                event = InputEvent(
                    XINPUT_GENERIC_NAMES[key], timestamp,
                    'Absolute', -buttons[key], device)
        elif key == 'XINPUT_GAMEPAD_DPAD_DOWN':
            if buttons[key] != last_buttons[key]:
                event = InputEvent(
                    XINPUT_GENERIC_NAMES[key], timestamp,
                    'Absolute', buttons[key], device)
        elif key == 'XINPUT_GAMEPAD_DPAD_LEFT':
            if buttons[key] != last_buttons[key]:
                event = InputEvent(
                    XINPUT_GENERIC_NAMES[key], timestamp,
                    'Absolute', -buttons[key], device)
        elif key == 'XINPUT_GAMEPAD_DPAD_RIGHT':
            if buttons[key] != last_buttons[key]:
                event = InputEvent(
                    XINPUT_GENERIC_NAMES[key], timestamp,
                    'Absolute', buttons[key], device)
        else:
            if buttons[key] != last_buttons[key]:
                event = InputEvent(
                    XINPUT_GENERIC_NAMES[key], timestamp,
                    'Key', buttons[key], device)
        if event != None:
            events.append(event)
    
    if state.gamepad.left_trigger != laststate.gamepad.left_trigger:
        event = InputEvent(
            'ABS_Z', timestamp,
            'Absolute', state.gamepad.left_trigger, device)
        events.append(event)
    if state.gamepad.right_trigger != laststate.gamepad.right_trigger:
        event = InputEvent(
            'ABS_RZ', timestamp,
            'Absolute', state.gamepad.right_trigger, device)
        events.append(event)
    if state.gamepad.l_thumb_x != laststate.gamepad.l_thumb_x:
        event = InputEvent(
            'ABS_X', timestamp,
            'Absolute', state.gamepad.l_thumb_x, device)
        events.append(event)
    if state.gamepad.l_thumb_y != laststate.gamepad.l_thumb_y:
        event = InputEvent(
            'ABS_Y', timestamp,
            'Absolute', state.gamepad.l_thumb_y, device)
        events.append(event)
    if state.gamepad.r_thumb_x != laststate.gamepad.r_thumb_x:
        event = InputEvent(
            'ABS_RX', timestamp,
            'Absolute', state.gamepad.r_thumb_x, device)
        events.append(event)
    if state.gamepad.r_thumb_y != laststate.gamepad.r_thumb_y:
        event = InputEvent(
            'ABS_RY', timestamp,
            'Absolute', state.gamepad.r_thumb_y, device)
        events.append(event)
    if events:
        addToQueue(
            eventQueue, InputEvent(
                'SYN_REPORT', timestamp, 'Sync', 0, device))
        for event in events:
            addToQueue(eventQueue, event)

class PreciseTimestamp():
    """Precise time"""
    def __init__(self):
        self.start_time = time.time() 
        self.execution_time = 0
        self.update()
    def update(self):
        """Updates the timestamp"""
        self.execution_time = time.perf_counter()
        self.time = self.start_time + self.execution_time
        
C_ULONG_MAX = 4294967295 # Maximum value used for the first packet number.

class XInputJoystick():
    """Stores data relating to an individual xinput device"""
    def __init__(self, device_number):
        self.device_number = device_number
        self.received_packets = 0
        self.missed_packets = 0
        self._last_state = XINPUT_STATE()
        self._last_state.packet_number = C_ULONG_MAX
        self.callback = self.__empty_func
        
    def __empty_func(self, joystick, state):
        return None
        
    def get_state(self):
        """Get the state of the controller represented by this object"""
        state = XINPUT_STATE()
        res = XINPUT.XInputGetState(self.device_number, ctypes.byref(state))
        if res == ERROR_SUCCESS:
            return state
        if res == ERROR_DEVICE_NOT_CONNECTED:
            raise UnpluggedError('Controller is disconnected')
        if res != ERROR_DEVICE_NOT_CONNECTED:
            raise RuntimeError(
                'Unknown error %d attempting to get state of device %d'
                % (res, self.device_number))
    def update_state(self, timestamp, eventqueue):
        """Updates the state of the controller, processes events and calls the callback function"""
        try:
            state = self.get_state()
        except(UnpluggedError):
            state = self._last_state
        if state.packet_number != self._last_state.packet_number:
            self.received_packets = self.received_packets + 1
            if state.packet_number > (self._last_state.packet_number + 1):
                self.missed_packets = (
                    self.missed_packets
                    + (state.packet_number
                        - self._last_state.packet_number
                        - 1))
            self.callback(self, state)
            stateToEvents(
                self.device_number, state, self._last_state,
                timestamp, eventqueue)
            self._last_state = state
            
class XInputManager():
    """Manages xinput devices"""
    def __init__(self, callback_function=None):
        # Polling rate in milliseconds max of 1ms.
        # Suggested minimum of 2ms to minimize missed packets.
        # 8ms might be usable but lots of device state changes will be missed.
        self.poll_rate = int(1000 / 500)# 1000 / poll_rate in ms
        self.update_thread = mmtimer.mmtimer(
            self.poll_rate, self._update, periodic=True)
        self.timestamp = PreciseTimestamp()
        self.max_devices = 4
        self.max_queuesize = (
            700)# 21 possible events 
                # * 4 possible devices
                # * 125 updates a second 
                # / 60 fps
                # * 4 to allow for a delay of ~60ms
                # = 700
                #  The theoritical worst case maximum amount of events
                #  that could be added before a program can react.
        self.eventqueue = queue.Queue(self.max_queuesize)
        self.joysticks = []
        for device in range(self.max_devices):
            self.joysticks.append(XInputJoystick(device))
            if callback_function != None:
                self.joysticks[device].callback = callback_function
        self.update_thread.start()
    def _update (self):
        """Is called by the update_thread"""
        self.timestamp.update()
        for device in self.joysticks:
            device.update_state(self.timestamp.time, self.eventqueue)
    def isConnected(self, device_number=0):
        """returns if an xinput device is connected on the provided port"""
        try:
            self.get_state(device_number)
            return True
        except(UnpluggedError):
            return False
    def get_events(self):
        """returns all events in the eventqueue and clears it"""
        events = []
        while not self.eventqueue.empty():
            events.append(self.eventqueue.get())
            self.eventqueue.task_done()
        return events
    def get_state(self, device_number=0):
        data = {}
        state = self.joysticks[device_number].get_state()
        if state != None:
            data = toSimpleState(state)
            return data
        return data
            
if __name__ == '__main__':
    # Optional callback function example not required.
    # This is run in a seperate thread.
    def callback(joystick,state):
        #previousState = toSimpleState(joystick._last_state)
        joystickNumber = joystick.device_number
        #currentState = toSimpleState(state)
        # Do special stuff here.
        print('xinput %d has found a new packet' % joystickNumber)
        return None
        

    print(XINPUT)
    # A function can be passed as a parameter
    # this will be called on every new packet found
    # this is optional and done in the polling thread
    # the function will be passed the joystick class
    # as well as the newest state for that joystick.
    xinputmanager = XInputManager(callback)
    
    runProgram = True
    while runProgram:
        try:
            # Get devices individually by state.
            for device in range(xinputmanager.max_devices):
                try:
                    state = xinputmanager.get_state(device)
                except(UnpluggedError):
                    state = None
                    print('there is no xinput device available at %d' % device )
                if state:
                    print('xinput available at %d' % device)
                    print(state)

            # Get devices by events.
            events = xinputmanager.get_events()
            if events:
                for event in events:
                    print(vars(event))
            print('XINPUT Device Connected at 0:', xinputmanager.isConnected(0))
            print('XINPUT Device Connected at 1:', xinputmanager.isConnected(1))
            print('XINPUT Device Connected at 2:', xinputmanager.isConnected(2))
            print('XINPUT Device Connected at 3:', xinputmanager.isConnected(3))
            # Event queue should be pretty much empty.
            #time.sleep(0.001)
            time.sleep(1/60)  # Typical use case of 60 fps.
            # Event queue is likely to become full and start deleting the oldest events.
            #time.sleep(10)
        except(KeyboardInterrupt):
            # Possibly optional.
            # Windows probably removes the periodic function call on program close.
            xinputmanager.update_thread.stop()
            runProgram = False
            