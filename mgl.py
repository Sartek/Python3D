import math

import moderngl
import glm
import numpy as np
from PIL import Image

from camera import Camera

class Graphics:
    def __init__(self):
        self.ctx = moderngl.create_context()
        
        self.vs_file = open("shader.vs", "r")
        self.vs = self.vs_file.read()
        self.vs_file.close()
        
        self.fs_file = open("shader.fs", "r")
        self.fs = self.fs_file.read()
        self.fs_file.close()
        
        self.prog = self.ctx.program(vertex_shader=self.vs, fragment_shader=self.fs)
        for value in self.prog:
            print(value)
            
        self.camera = Camera()
            
        self.vertices = np.array([
            [-0.5, -0.5, -0.5, 1.0, 0.0, 0.0],
            [ 0.5, -0.5, -0.5, 1.0, 1.0, 0.0],
            [ 0.5,  0.5, -0.5, 1.0, 1.0, 1.0],
            [ 0.5,  0.5, -0.5, 1.0, 1.0, 1.0],
            [-0.5,  0.5, -0.5, 1.0, 0.0, 1.0],
            [-0.5, -0.5, -0.5, 1.0, 0.0, 0.0],
            [-0.5, -0.5,  0.5, 1.0, 0.0, 0.0],
            [ 0.5, -0.5,  0.5, 1.0, 1.0, 0.0],
            [ 0.5,  0.5,  0.5, 1.0, 1.0, 1.0],
            [ 0.5,  0.5,  0.5, 1.0, 1.0, 1.0],
            [-0.5,  0.5,  0.5, 1.0, 0.0, 1.0],
            [-0.5, -0.5,  0.5, 1.0, 0.0, 0.0],
            [-0.5,  0.5,  0.5, 1.0, 1.0, 0.0],
            [-0.5,  0.5, -0.5, 1.0, 1.0, 1.0],
            [-0.5, -0.5, -0.5, 1.0, 0.0, 1.0],
            [-0.5, -0.5, -0.5, 1.0, 0.0, 1.0],
            [-0.5, -0.5,  0.5, 1.0, 0.0, 0.0],
            [-0.5,  0.5,  0.5, 1.0, 1.0, 0.0],
            [ 0.5,  0.5,  0.5, 1.0, 1.0, 0.0],
            [ 0.5,  0.5, -0.5, 1.0, 1.0, 1.0],
            [ 0.5, -0.5, -0.5, 1.0, 0.0, 1.0],
            [ 0.5, -0.5, -0.5, 1.0, 0.0, 1.0],
            [ 0.5, -0.5,  0.5, 1.0, 0.0, 0.0],
            [ 0.5,  0.5,  0.5, 1.0, 1.0, 0.0],
            [-0.5, -0.5, -0.5, 1.0, 0.0, 1.0],
            [ 0.5, -0.5, -0.5, 1.0, 1.0, 1.0],
            [ 0.5, -0.5,  0.5, 1.0, 1.0, 0.0],
            [ 0.5, -0.5,  0.5, 1.0, 1.0, 0.0],
            [-0.5, -0.5,  0.5, 1.0, 0.0, 0.0],
            [-0.5, -0.5, -0.5, 1.0, 0.0, 1.0],
            [-0.5,  0.5, -0.5, 1.0, 0.0, 1.0],
            [ 0.5,  0.5, -0.5, 1.0, 1.0, 1.0],
            [ 0.5,  0.5,  0.5, 1.0, 1.0, 0.0],
            [ 0.5,  0.5,  0.5, 1.0, 1.0, 0.0],
            [-0.5,  0.5,  0.5, 1.0, 0.0, 0.0],
            [-0.5,  0.5, -0.5, 1.0, 0.0, 1.0]
            ], np.float32)          
                                    
        
        
        self.aColor = self.prog['aColor']
        self.aColor.value = (0.9, 0.9, 0.9)
        
        self.view = self.prog['view']
        self.projection = self.prog['projection']
        self.model = self.prog['model']
        
        self.worldPosition = [
            (  0.0,  0.0,  0.0),
            (  2.0,  5.0,  -15),
            ( -1.5, -2.2, -2.5),  
            ( -3.8, -2.0, -12 ),  
            ( -1.7,  3.0, -7.5),  
            (  1.3, -2.0, -2.5),  
            (  1.5,  2.0, -2.5), 
            (  1.5,  0.2, -1.5), 
            ( -1.3,  1.0, -1.5)  
            ]
         
        self.img1 = Image.open('container.png').transpose(Image.FLIP_TOP_BOTTOM).convert('RGB')
        self.texture1 = self.ctx.texture(self.img1.size, 3, self.img1.tobytes())
        self.texture1.build_mipmaps()
        self.texture1.repeat_x = False
        self.texture1.repeat_y = False
        self.prog['texture1'].value = 0
        
        self.img2 = Image.open('awesomeface.png').transpose(Image.FLIP_TOP_BOTTOM)
        self.texture2 = self.ctx.texture(self.img2.size, 4, self.img2.tobytes())
        self.texture2.build_mipmaps()
        self.texture2.repeat_x = False
        self.texture2.repeat_y = False
        self.prog['texture2'].value = 1
        
        self.ctx.enable(moderngl.BLEND)
        self.ctx.enable(moderngl.DEPTH_TEST)
        #self.ctx.enable(moderngl.CULL_FACE)
        
        self.vbo = self.ctx.buffer(self.vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'vertices', 'aTexCoord')
        
    def toTuple(self, data):
        l = []
        for row in data:
            for value in row:
                l.append(value)
        return tuple(l)
        
        
    def updateCamera(self, newPosition, newDirection):
        #radius = 10
        #self.camera.position['x'] = math.sin(self.seconds) * radius + (5 * self.gameController.getValue('ABS_RX'))
        #self.camera.position['y'] = 0.0 + (5 * self.gameController.getValue('ABS_RY'))#todo
        #self.camera.position['z'] = math.cos(self.seconds) * radius
        
        #self.camera.position['x'] = 0.0 + (5 * self.gameController.getValue('ABS_RX'))
        #self.camera.position['y'] = 0.0 + (5 * self.gameController.getValue('ABS_RY'))
        #self.camera.position['z'] = 0.0#0.0

        #boxPosition = glm.vec3(self.worldPosition[1][0],self.worldPosition[1][1],self.worldPosition[1][2])
        #self.camera.position['x'] = self.camera.position['x'] + boxPosition.x
        #self.camera.position['y'] = self.camera.position['y'] + boxPosition.y
        #self.camera.position['z'] = self.camera.position['z'] + boxPosition.z
        
        #boxPosition = (boxPosition.x, boxPosition.y, boxPosition.z)
        #self.camera.lookAt(boxPosition)


        self.camera.position.x = newPosition.x
        self.camera.position.y = newPosition.y
        self.camera.position.z = newPosition.z

        #self.camera.direction['x'] = newDirection['x']
        #self.camera.direction['y'] = newDirection['y']
        #self.camera.direction['z'] = newDirection['z']
        self.camera.direction.x = newDirection.x
        self.camera.direction.y = newDirection.y
        self.camera.direction.z = newDirection.z

        self.camera.update()
        
        self.view.value = self.camera.viewMatrix
        self.projection.value = self.camera.projectionMatrix
        
    def render(self, renderData):
        self.ctx.clear()
        
        self.updateCamera(renderData['cameraPosition'],renderData['cameraDirection'])
        
        #self.ctx.wireframe = True
        self.texture1.use(0)
        self.texture2.use(1)
        for position in self.worldPosition:
            self.model.value = (
                1,0,0,0,
                0,1,0,0,
                0,0,1,0,
                position[0],position[1],position[2],1
                )
            self.vao.render(moderngl.TRIANGLES)