import xinput
import time
import struct
inputs = xinput.XInputManager()

class GameController:
    def __init__(self):
        self.data = {}
        self.data["ABS_RX"] = {'type': 'analog', 'min': -32768, 'max': 32767, 'deadzone': 0.05, 'total': 0, 'value': 0}
        self.data["ABS_RY"] = {'type': 'analog', 'min': -32768, 'max': 32767, 'deadzone': 0.05, 'total': 0, 'value': 0}
        self.data["ABS_X"] = {'type': 'analog', 'min': -32768, 'max': 32767, 'deadzone': 0.05, 'total': 0, 'value': 0}
        self.data["ABS_Y"] = {'type': 'analog', 'min': -32768, 'max': 32767, 'deadzone': 0.05, 'total': 0, 'value': 0}
        
        self.data["ABS_RZ"] = {'type': 'analog', 'min': 0, 'max': 255, 'total': 0, 'value': 0}#add trigger pressed/release/trigger
        self.data["ABS_Z"] = {'type': 'analog', 'min': 0, 'max': 255, 'total': 0, 'value': 0}#TODO
        
        #self.data["BTN_SOUTH"] = {'type': 'button', 'total': 0, 'value': 0, 'pressed': 0, 'released': 0}
        self.data["ABS_HAT0X"] = {'type': 'hat', 'total': 0, 'value' : 0, '+pressed': 0, '-pressed': 0, 'released': 0}
        self.data["ABS_HAT0Y"] = {'type': 'hat', 'total': 0, 'value' : 0, '+pressed': 0, '-pressed': 0, 'released': 0}
        
    def update(self):
        events = []
        
        
        events = inputs.get_events()
        if not inputs.isConnected():
            for key in self.data:
                self.data[key]['total'] = 0
                if 'total' in self.data[key]:
                    self.data[key]['total'] = 0
                if 'value' in self.data[key]:
                    self.data[key]['value'] = 0
                if 'pressed' in self.data[key].keys():
                    self.data[key]['pressed'] = 0
                if 'released' in self.data[key].keys():
                    self.data[key]['released'] = 0
                if '+pressed' in self.data[key].keys():
                    self.data[key]['+pressed'] = 0
                if '-pressed' in self.data[key].keys():
                    self.data[key]['-pressed'] = 0
        for event in events:
            if event.ev_type == "Sync":
                if event.code == "SYN_REPORT":
                    pass
                else:
                    print(event.ev_type, event.code, event.state)
            elif event.ev_type == "Absolute":
                if event.code == "ABS_X":
                    self.analogValue(event.code, event.state)
                elif event.code == "ABS_Y":
                    self.analogValue(event.code, event.state)
                elif event.code == "ABS_RX":
                    self.analogValue(event.code, event.state)
                elif event.code == "ABS_RY":
                    self.analogValue(event.code, event.state)
                elif event.code == "ABS_Z":
                    self.analogValue(event.code, event.state)
                elif event.code == "ABS_RZ":
                    self.analogValue(event.code, event.state)
                elif event.code == "ABS_HAT0X":
                    self.hatValue(event.code, event.state)
                elif event.code == "ABS_HAT0Y":
                    self.hatValue(event.code, event.state)
                else:
                    print(event.ev_type, event.code, event.state)
            elif event.ev_type == "Key":
                if event.code == "BTN_NORTH":
                    self.buttonValue(event.code, event.state)
                elif event.code == "BTN_EAST":
                    self.buttonValue(event.code, event.state)
                elif event.code == "BTN_SOUTH":
                    self.buttonValue(event.code, event.state)
                elif event.code == "BTN_WEST":
                    self.buttonValue(event.code, event.state)
                else:
                    self.buttonValue(event.code, event.state)
                    #print(event.ev_type, event.code, event.state)
            else:
                print(event.ev_type, event.code, event.state)
                
        #print(self.data)
        for key in self.data:
            if self.data[key]['type'] == 'analog':
                if self.data[key]['total'] > 0:
                    self.data[key]['value'] = self.data[key]['value'] / self.data[key]['total']
                    self.data[key]['total'] = 0
            if self.data[key]['type'] == 'button':
                #print(self.data[key]['value'])
                if self.data[key]['total'] > 0:
                    self.data[key]['total'] = 0
                else:
                    self.data[key]['pressed'] = 0
                    self.data[key]['released'] = 0
            if self.data[key]['type'] == 'hat':
                if self.data[key]['total'] > 0:
                    self.data[key]['total'] = 0
                else:
                    self.data[key]['+pressed'] = 0
                    self.data[key]['-pressed'] = 0
                    self.data[key]['released'] = 0
            #print(self.data[key]['value'])
            
    def getValue(self, value, element='value'):
        if value in self.data.keys():
            return self.data[value][element]
        else:
            return 0
            
    def hatValue(self, code, value):
        if not(code in self.data.keys()):
            self.data[code] = {'type': 'hat', 'value': 0, '+pressed': 0, '-pressed': 0, 'released': 0, 'total': 0}
        if not 'type' in self.data[code].keys():
             self.data[code]['type'] = 'hat'
        if not '+pressed' in self.data[code].keys():
            self.data[code]['+pressed'] = 0
        if not '-pressed' in self.data[code].keys():
            self.data[code]['-pressed'] = 0
        if not 'released' in self.data[code].keys():
            self.data[code]['released'] = 0
        if not 'total' in self.data[code].keys():
            self.data[code]['total'] = 0
        if not 'value' in self.data[code].keys():
            self.data[code]['value'] = 0
            
        if self.data[code]['total'] == 0:
            self.data[code]['released'] = 0
            self.data[code]['+pressed'] = 0
            self.data[code]['-pressed'] = 0
        if value == 0:
            self.data[code]['released'] = self.data[code]['released'] + 1#hat released
        if value == 1:
            self.data[code]['+pressed'] = self.data[code]['+pressed'] + 1#positive hat pressed
        if value == -1:
            self.data[code]['-pressed'] = self.data[code]['-pressed'] + 1#negative hat pressed
            
        newValue = value
        self.data[code]['total'] = self.data[code]['total'] + 1
        self.data[code]['value'] = newValue
        return newValue
            
    def buttonValue(self, code, value):
        if not(code in self.data.keys()):
            self.data[code] = {'type': 'button', 'value': 0, 'pressed': 0, 'released': 0, 'total': 0}
        if not 'type' in self.data[code].keys():
            self.data[code]['type'] = 'button'
        if not 'pressed' in self.data[code].keys():
            self.data[code]['pressed'] = 0
        if not 'released' in self.data[code].keys():
            self.data[code]['released'] = 0
        if not 'total' in self.data[code].keys():
            self.data[code]['total'] = 0
        if not 'value' in self.data[code].keys():
            self.data[code]['value'] = 0
            
            
        if self.data[code]['total'] == 0:
            self.data[code]['released'] = 0
            self.data[code]['pressed'] = 0
        if value == 0:
            self.data[code]['released'] = self.data[code]['released'] + 1#button released
        if value == 1:
            self.data[code]['pressed'] = self.data[code]['pressed'] + 1#button pressed
        newValue = value
        self.data[code]['total'] = self.data[code]['total'] + 1
        self.data[code]['value'] = newValue
        return newValue
                
    def analogValue(self, code, value):
        if not(code in self.data.keys()):
            self.data[code] = {'type': 'analog', 'min': 0, 'max': 0, 'total': 0, 'value': 0}
        if not 'type' in self.data[code].keys():
            self.data[code]['type'] = 'analog'
        if not 'min' in self.data[code].keys():
            self.data[code]['min'] = 0
        if not 'max' in self.data[code].keys():
            self.data[code]['max'] = 0
        if not 'total' in self.data[code].keys():
            self.data[code]['total'] = 0
        if not 'value' in self.data[code].keys():
            self.data[code]['value'] = 0
            
            
        if value > self.data[code]['max']:
            self.data[code]['max'] = value
        elif value < self.data[code]['min']:
            self.data[code]['min'] = value
        if 'deadzone' in self.data[code]:
            deadzone = self.data[code]['deadzone']
            max = self.data[code]['max']
            min = self.data[code]['min']
            if value > (max * deadzone):
                self.data[code]['total'] = self.data[code]['total'] + 1
                newValue = self.normalize(value,max * deadzone, max, 0, 1)
            elif value < (min * deadzone):
                self.data[code]['total'] = self.data[code]['total'] + 1
                newValue = self.normalize(value,min, min  * deadzone, -1, 0)
            else:
                if self.data[code]['total'] == 0:
                    self.data[code]['value'] = 0
                newValue = 0#should do nothing
        else:
            self.data[code]['total'] = self.data[code]['total'] + 1
            if not (self.data[code]['min'] == 0):
                newValue = self.normalize(value, self.data[code]['min'], self.data[code]['max'], -1, 1)
            else:
                newValue = self.normalize(value, self.data[code]['min'], self.data[code]['max'], 0, 1)
            
            
        if self.data[code]['total'] == 1:
            self.data[code]['value'] = 0
        self.data[code]['value'] = self.data[code]['value'] + newValue
        #print(self.data[code]['value'])
        
        return newValue
                
    def normalize(self, value, min, max, newMin, newMax):
        oldRange = (max - min)
        newRange = (newMax - newMin)
        newValue = (((value - min) * newRange) / oldRange) + newMin
        return newValue

    
if __name__ == "__main__":
    runProgram = True
    
    
    gameController = GameController()
    
    while runProgram:
        try:
            gameController.update()
            print(gameController.data)
            time.sleep(0.01)
        except(KeyboardInterrupt):
            runProgram = False