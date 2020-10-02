import glm
import vector

class Camera:
    def __init__(self, xyz=(0.0,0.0,5.0), direction=(0.0,0.0,-1.0)):
        self.position = vector.Vec3(xyz)
        #FIX THIS
        self.direction = vector.Vec4(direction,0)
        #self.direction = vector.Vec3(direction)
        #self.right = (1.0, 0.0, 0.0)
        #self.forward = (0.0, 0.0, -1.0)
        self.fov = 45.0
        self.near = 0.1
        self.far = 100.0
        self.aspectRatio = 800.0 / 600.0
        
        self.viewMatrix = (
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0
            )
        self.projectionMatrix = (
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0
            )
    def up(self):
        return (0.0,1.0,0.0)
    def right(self):
        direction = glm.vec3(self.direction.getTuple())#getTupleVec3())
        return glm.cross(direction, self.up())
    def forward(self):
        return self.direction.getTuple()#getTupleVec3()
    def update(self):
        position = glm.vec3(self.position.getTuple())
        direction = glm.vec3(self.direction.getTuple())#getTupleVec3())
        self.viewMatrix = self.toTuple(glm.lookAt(position, position + direction, self.up()))
        self.projectionMatrix = self.toTuple(glm.perspective(glm.radians(self.fov), self.aspectRatio, self.near, self.far))
        
    def lookAt(self, xyz):
        position = glm.vec3(self.position.getTuple())
        direction = glm.normalize(glm.vec3(xyz) - glm.vec3(position))
        self.direction = vector.Vec4(direction)
        
    def toTuple(self, data):
        l = []
        for row in data:
            for value in row:
                l.append(value)
        return tuple(l)