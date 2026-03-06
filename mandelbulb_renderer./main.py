import pygame
from pygame.locals import *
from OpenGL.GL import *
import numpy as np
import math
import shader
import camera
import mandelbulb

# Simple vertex shader to render a quad over the whole screen
VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec2 aPos;
void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
}
"""

def main():
    pygame.init()
    # If the framerate is too low on your Retina display, change this to (400, 300)
    display = (800, 600)
    
    # 1. MAC OPENGL CORE PROFILE CONFIG
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    clock = pygame.time.Clock()
    
    # 2. CREATE VAO BEFORE SHADER COMPILATION (Crucial for MacOS)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Full screen quad vertices
    vertices = np.array([-1, -1,  1, -1,  1, 1,  -1, 1], dtype=np.float32)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    # 3. COMPILE SHADERS
    cam = camera.Camera()
    try:
        program = shader.create_shader(VERTEX_SHADER, mandelbulb.fragment_shader_source)
    except Exception as e:
        print(f"Shader Error: {e}")
        return

    glUseProgram(program)

    # Get locations for the variables we send to the GPU
    res_loc = glGetUniformLocation(program, "u_resolution")
    pwr_loc = glGetUniformLocation(program, "u_power")
    time_loc = glGetUniformLocation(program, "u_time")
    view_inv_loc = glGetUniformLocation(program, "u_view_inv")
    
    power = 8.0
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    running = True
    while running:
        # Get time in seconds for the color animation
        current_time = pygame.time.get_ticks() / 1000.0
        
        dt = clock.tick(60) 
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

        # --- INPUT HANDLING ---
        keys = pygame.key.get_pressed()
        
        # Calculate direction for movement relative to where you look
        dir_vec = pygame.math.Vector3(
            math.cos(math.radians(cam.yaw)) * math.cos(math.radians(cam.pitch)),
            math.sin(math.radians(cam.pitch)),
            math.sin(math.radians(cam.yaw)) * math.cos(math.radians(cam.pitch))
        ).normalize()
        right_vec = dir_vec.cross(pygame.math.Vector3(0, 1, 0)).normalize()

        if keys[K_w]: cam.pos += dir_vec * cam.speed
        if keys[K_s]: cam.pos -= dir_vec * cam.speed
        if keys[K_a]: cam.pos -= right_vec * cam.speed
        if keys[K_d]: cam.pos += right_vec * cam.speed
        if keys[K_UP]: power += 0.05
        if keys[K_DOWN]: power -= 0.05

        # Mouse look logic
        rel_x, rel_y = pygame.mouse.get_rel()
        cam.yaw += rel_x * cam.sensitivity
        cam.pitch -= rel_y * cam.sensitivity
        cam.pitch = max(-89, min(89, cam.pitch))

        # --- RENDERING ---
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        glUseProgram(program)
        
        # Update uniforms
        glUniform2f(res_loc, display[0], display[1])
        glUniform1f(pwr_loc, power)
        glUniform1f(time_loc, current_time) # Send time for rainbow colors
        
        # Matrix math: Invert the view matrix to generate rays
        view_mat = cam.get_view_matrix()
        inv_view = np.linalg.inv(view_mat)
        glUniformMatrix4fv(view_inv_loc, 1, GL_FALSE, inv_view)
        
        # Draw the fullscreen quad
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

        pygame.display.flip()
        pygame.display.set_caption(f"Mandelbulb 3D | Power: {power:.2f} | FPS: {int(clock.get_fps())}")

    pygame.quit()

if __name__ == "__main__":
    main()