import time
import cProfile
import pyglet

import mgl
import update


class ProgramWindow(pyglet.window.Window):
    def __init__(self, width, height, config, vsync):
        super().__init__(width=width, height=height, config=config, vsync=vsync)
        self.seconds = time.perf_counter()
        self.runProgram = True
        self.core = update.UpdateLogic()
        self.mgl = mgl.Graphics()
        self.mgl.camera.aspectRatio = width / height
        self.deltaTime = 0.0
        self.deltaTimeRemainder = 0.0
        self.tickRate = 120
        self.minUpdateTime = 1 / self.tickRate
    def on_draw(self):
        renderData = self.core.getRenderData()
        self.mgl.render(renderData)
    def on_close(self):
        self.runProgram = False
    def update_timer(self):
        self.seconds = time.perf_counter()
        self.mgl.seconds = self.seconds
    def update(self):
        dt = self.deltaTime + self.deltaTimeRemainder
        if dt > self.minUpdateTime:
            self.core.gameController.update()
        while dt > self.minUpdateTime:
            dt -= self.minUpdateTime
            self.core.update(self.minUpdateTime)
        self.deltaTimeRemainder = dt
    
#if __name__ == '__main__':

def main():
    config = pyglet.gl.Config(double_buffer=False, depth_size=24)
    window = ProgramWindow(width=2540, height=1440, config=config, vsync=False)
    #depreciated???
    #pyglet.clock.set_fps_limit(300)
    while (window.runProgram):
        try:
            window.update_timer()
            #dt = pyglet.clock.tick(True)
            dt = pyglet.clock.tick(False)
            window.deltaTime = dt
            window.update()
            #print(pyglet.clock.get_fps())
            
            for window in pyglet.app.windows:
                window.switch_to()
                window.dispatch_events()
                window.dispatch_event('on_draw')
                window.flip()
            #time.sleep(0.0001)
        except(KeyboardInterrupt):
            window.close()
            window.runProgram = False
if __name__ == '__main__':     
    main()
    #cProfile.run('main()', 'restats')