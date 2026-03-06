import numpy as np
from pygame.math import Vector3
import math

class Camera:
    def __init__(self):
    # Moving to (0, 0, 5) puts us safely outside the Mandelbulb radius (which is 2.0)
       self.pos = Vector3(0, 0, 5) 
       self.yaw = -90.0
       self.pitch = 0.0
       self.speed = 0.1 # Increased speed to help you navigate faster
       self.sensitivity = 0.2

    def get_view_matrix(self):
        # Calculate direction vectors
        front = Vector3(
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        ).normalize()
        
        right = front.cross(Vector3(0, 1, 0)).normalize()
        up = right.cross(front).normalize()
        
        # Build the View Matrix
        res = np.identity(4, dtype=np.float32)
        res[0, :3] = right
        res[1, :3] = up
        res[2, :3] = -front
        res[3, 0:3] = -np.array([self.pos.dot(right), self.pos.dot(up), self.pos.dot(-front)])
        return res