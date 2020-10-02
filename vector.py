class Vec3:
    def __init__(self, xyz=(0.0, 0.0, 0.0)):
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]
    def getTuple(self):
        return (self.x,self.y,self.z)
class Vec4:
    def __init__(self, xyz=(0.0, 0.0, 0.0),w=0):
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]
        self.w = w
    def getTupleXYZ(self):
        return (self.x, self.y, self.z)
    def getTuple(self):
        return(self.x, self.y, self.z, self.w)