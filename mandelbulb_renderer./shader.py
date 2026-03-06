from OpenGL.GL import *
import OpenGL.GL.shaders

def create_shader(vertex_src, fragment_src):
    # Compiles and links the shader program
    return OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(vertex_src, GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(fragment_src, GL_FRAGMENT_SHADER)
    )