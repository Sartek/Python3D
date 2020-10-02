import glm
import math
import vector
from gamecontroller import GameController
from camera import Camera

#mat4 rotate_x(float theta)
#{
#    return mat4(
#        vec4(1.0,         0.0,         0.0, 0.0),
#        vec4(0.0,  cos(theta),  sin(theta), 0.0),
#        vec4(0.0, -sin(theta),  cos(theta), 0.0),
#        vec4(0.0,         0.0,         0.0, 1.0)
#    );
#}

#mat4 rotate_y(float theta)
#{
#    return mat4(
#        vec4( cos(theta), 0.0, sin(theta), 0.0),
#        vec4(        0.0, 1.0,        0.0, 0.0),
#        vec4(-sin(theta), 0.0, cos(theta), 0.0),
#        vec4(        0.0, 0.0,        0.0, 1.0)
#    );
#}

#mat4 rotate_z(float theta)
#{
#    return mat4(
#        vec4(cos(theta), -sin(theta), 0.0, 0.0),
#        vec4(sin(theta),  cos(theta), 0.0, 0.0),
#        vec4(       0.0,         0.0, 1.0, 0.0),
#        vec4(       0.0,         0.0, 0.0, 1.0)
#        );
#}

def rotate_x(angle):
    radians = math.radians(angle)
    a = math.cos(radians)
    b = math.sin(radians)
    c = -(math.sin(radians))
    d = math.cos(radians)

    mat = glm.mat4(
        [1,0,0,0],
        [0,a,b,0],
        [0,c,d,0],
        [0,0,0,1]
    )

    return mat

def rotate_y(angle):
    radians = math.radians(angle)
    a = math.cos(radians)
    b = math.sin(radians)
    c = -(math.sin(radians))
    d = math.cos(radians)

    mat = glm.mat4(
        [a,0,b,0],
        [0,1,0,0],
        [c,0,d,0],
        [0,0,0,1]
    )

    return mat

def rotate_z(angle):
    radians = math.radians(angle)
    a = math.cos(radians)
    b = -(math.sin(radians))
    c = math.sin(radians)
    d = math.cos(radians)

    mat = glm.mat4(
        [a,b,0,0],
        [c,d,0,0],
        [0,0,1,0],
        [0,0,0,1]
    )

    return mat

def rotate(x,y,z):
    matX = rotate_x(x)
    matY = rotate_y(y)
    matZ = rotate_z(z)
    return (matZ * matY * matX)

def mat_x_vec(mat, vec):
    vector = glm.vec4(vec,0)
    print(vector)
    vector = mat * vector
    return vector

class UpdateLogic():
    def __init__(self):
        self.gameController = GameController()
        self.camera = Camera((0.0, 0.0, 5.0))
        #self.cameraPosition = {'x': 0.0, 'y': 0.0, 'z': 5.0}
        #self.cameraDirection = {'x':0.0, 'y': 0.0, 'z': -1.0}
        self.cameraMovementSpeed = 3.0
        self.cameraRotationSpeed = 1
        self._renderData = {}
    def update(self, dt):

        tmpz = self.camera.direction.z
        if self.gameController.getValue('BTN_SOUTH','pressed') > 0:
            tmpz = tmpz *-1
        
        direction = glm.vec3(self.gameController.getValue('ABS_RX'),self.gameController.getValue('ABS_RY'),tmpz)
        direction = glm.normalize(direction) 
        self.camera.direction.x = direction[0]
        self.camera.direction.y = direction[1]
        self.camera.direction.z = direction[2]
        self.camera.direction.w = 0

        m = rotate(15,30,0)
        tmp = m * glm.vec4(self.camera.direction.getTuple())
        self.camera.direction = vector.Vec4((tmp.x,tmp.y,tmp.z),tmp.w)

        #Move forward/backward
        self.camera.position = vector.Vec3(
            glm.vec3(self.camera.position.getTuple())
            + (self.cameraMovementSpeed * self.gameController.getValue('ABS_Y') * dt)
                * glm.vec3(self.camera.forward()))

        #Move left/right
        right = glm.vec3(self.camera.right())
        self.camera.position = vector.Vec3(
            glm.vec3(self.camera.position.getTuple())
            + (self.cameraMovementSpeed * self.gameController.getValue('ABS_X') * dt)
                * right)
        #self.camera.position.y = self.camera.position.y# + (self.cameraMovementSpeed['y'] * self.gameController.getValue('ABS_RY') * dt)
        #self.camera.position.z = self.camera.position.z - (self.cameraMovementSpeed * self.gameController.getValue('ABS_Y') * dt)

        #self.camera.position.x = self.camera.position.x + (self.cameraMovementSpeed['x'] * self.gameController.getValue('ABS_X') * dt)
        #self.camera.position.y = self.camera.position.y# + (self.cameraMovementSpeed['y'] * self.gameController.getValue('ABS_RY') * dt)
        #self.camera.position.z = self.camera.position.z - (self.cameraMovementSpeed['z'] * self.gameController.getValue('ABS_Y') * dt)

    def getRenderData(self):
        self._renderData = {}
        self._renderData['cameraPosition'] = self.camera.position
        self._renderData['cameraDirection'] = self.camera.direction
        return self._renderData