import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
from math import sin, cos, pi, radians, degrees

# Window dimensions
width, height = 800, 600
window = None # GLFW window object

# Camera parameters
camera_yaw = 0.0 
camera_pitch = 20.0 # Initial pitch to look down slightly
camera_distance = 15.0
last_x, last_y = width / 2, height / 2
first_mouse = True
mouse_dragging = False

# Clipping plane variables
clipping_enabled = False
clip_plane_d_offset = -2.0  # Initial D value for the plane equation Z + D = 0. Positive D moves plane in -Z.

def init_gl():
    glClearColor(0.8, 0.9, 1.0, 1.0)  # Sky blue background
    glEnable(GL_DEPTH_TEST)

    # Set global ambient light (makes the whole scene a bit brighter, uniformly)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.3, 0.3, 0.3, 1.0])

    # Setup light 0 properties
    light_pos = [10.0, 10.0, 10.0, 1.0]  # Positional light
    light_ambient = [0.2, 0.2, 0.2, 1.0]
    light_diffuse = [0.7, 0.7, 0.7, 1.0]  # Slightly reduced diffuse
    light_specular = [0.5, 0.5, 0.5, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    glEnable(GL_LIGHTING)  # Enable lighting calculations
    glEnable(GL_LIGHT0)    # Enable light source 0

    # Material properties
    # Tells OpenGL to use glColor values for AMBIENT and DIFFUSE material properties
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Set a default specular material color and shininess for objects
    # This will make objects capable of showing specular highlights from the light source
    default_specular_material = [0.8, 0.8, 0.8, 1.0] # Brighter specular reflection
    default_shininess = 32.0 # Moderate shininess
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, default_specular_material)
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, default_shininess)

    # Normalize normals if scaling is used (good practice)
    glEnable(GL_NORMALIZE)


def framebuffer_size_callback(window, w, h):
    global width, height
    width, height = w, h
    if h == 0: h = 1 # prevent division by zero
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(w)/h if h > 0 else 0, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def key_callback(window_handle, key, scancode, action, mods):
    global camera_distance, clipping_enabled, clip_plane_d_offset

    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window_handle, True)
    if (key == glfw.KEY_EQUAL or key == glfw.KEY_KP_ADD) and (action == glfw.PRESS or action == glfw.REPEAT):
        camera_distance = max(1.0, camera_distance - 0.5)
    if (key == glfw.KEY_MINUS or key == glfw.KEY_KP_SUBTRACT) and (action == glfw.PRESS or action == glfw.REPEAT):
        camera_distance = min(50.0, camera_distance + 0.5)

    if key == glfw.KEY_C and action == glfw.PRESS:
        clipping_enabled = not clipping_enabled
        print(f"Clipping plane {'enabled' if clipping_enabled else 'disabled'}")
    if key == glfw.KEY_J and (action == glfw.PRESS or action == glfw.REPEAT):
        clip_plane_d_offset -= 0.1
        print(f"Clip plane D offset: {clip_plane_d_offset:.2f}")
    if key == glfw.KEY_K and (action == glfw.PRESS or action == glfw.REPEAT):
        clip_plane_d_offset += 0.1
        print(f"Clip plane D offset: {clip_plane_d_offset:.2f}")

def mouse_button_callback(window_handle, button, action, mods):
    global mouse_dragging, first_mouse
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            mouse_dragging = True
            first_mouse = True # Reset first_mouse on new drag
            glfw.set_input_mode(window_handle, glfw.CURSOR, glfw.CURSOR_DISABLED)
        elif action == glfw.RELEASE:
            mouse_dragging = False
            glfw.set_input_mode(window_handle, glfw.CURSOR, glfw.CURSOR_NORMAL)

def cursor_pos_callback(window_handle, xpos, ypos):
    global last_x, last_y, camera_yaw, camera_pitch, first_mouse, mouse_dragging

    if not mouse_dragging:
        return

    if first_mouse:
        last_x = xpos
        last_y = ypos
        first_mouse = False

    xoffset = xpos - last_x
    yoffset = last_y - ypos # reversed since y-coordinates go from top to bottom
    last_x = xpos
    last_y = ypos

    sensitivity = 0.1
    xoffset *= sensitivity
    yoffset *= sensitivity

    camera_yaw += xoffset
    camera_pitch += yoffset

    if camera_pitch > 89.0:
        camera_pitch = 89.0
    if camera_pitch < -89.0:
        camera_pitch = -89.0

def draw_cube(size=1.0):
    s = size / 2.0
    # Using glBegin/glEnd is deprecated but simple for this example.
    # For more complex scenes, vertex arrays/VBOs are preferred.
    glBegin(GL_QUADS)
    # Front face
    glNormal3f(0,0,1)
    glVertex3f(-s, -s,  s)
    glVertex3f( s, -s,  s)
    glVertex3f( s,  s,  s)
    glVertex3f(-s,  s,  s)
    # Back face
    glNormal3f(0,0,-1)
    glVertex3f(-s, -s, -s)
    glVertex3f(-s,  s, -s)
    glVertex3f( s,  s, -s)
    glVertex3f( s, -s, -s)
    # Top face
    glNormal3f(0,1,0)
    glVertex3f(-s,  s, -s)
    glVertex3f(-s,  s,  s)
    glVertex3f( s,  s,  s)
    glVertex3f( s,  s, -s)
    # Bottom face
    glNormal3f(0,-1,0)
    glVertex3f(-s, -s, -s)
    glVertex3f( s, -s, -s)
    glVertex3f( s, -s,  s)
    glVertex3f(-s, -s,  s)
    # Right face
    glNormal3f(1,0,0)
    glVertex3f( s, -s, -s)
    glVertex3f( s,  s, -s)
    glVertex3f( s,  s,  s)
    glVertex3f( s, -s,  s)
    # Left face
    glNormal3f(-1,0,0)
    glVertex3f(-s, -s, -s)
    glVertex3f(-s, -s,  s)
    glVertex3f(-s,  s,  s)
    glVertex3f(-s,  s, -s)
    glEnd()

def draw_classroom():
    # Floor
    glColor3f(0.7, 0.7, 0.7) # Grey
    glPushMatrix()
    glTranslatef(0, -0.1, 0) 
    glScalef(10, 0.2, 8)
    draw_cube(1)
    glPopMatrix()

    # Walls
    glColor3f(0.9, 0.9, 0.8) # Light beige
    # Back wall
    glPushMatrix()
    glTranslatef(0, 2.5, -4)
    glScalef(10, 5, 0.2)
    draw_cube(1)
    glPopMatrix()
    # Left wall
    glPushMatrix()
    glTranslatef(-5, 2.5, 0)
    glScalef(0.2, 5, 8)
    draw_cube(1)
    glPopMatrix()
    # Right wall
    glPushMatrix()
    glTranslatef(5, 2.5, 0)
    glScalef(0.2, 5, 8)
    draw_cube(1)
    glPopMatrix()

    # Board
    glColor3f(0.1, 0.3, 0.1) # Dark green
    glPushMatrix()
    glTranslatef(0, 2.5, -3.85) # Adjusted Y to be on the wall, Z slightly forward
    glScalef(4, 2.5, 0.1) 
    draw_cube(1)
    glPopMatrix()

    # Desks
    desk_color = [0.6, 0.4, 0.2] # Brown
    for i in range(-1, 2): # 3 desks in a row
        for j in range(2): # 2 rows of desks
            glColor3fv(desk_color)
            glPushMatrix()
            glTranslatef(i * 2.5, 0.5, j * 2.5 - 0.5) # x, height, z
            glScalef(1.0, 0.4, 0.6) # width, height, depth
            draw_cube(1)
            glPopMatrix()
            # Chair (simple cube)
            glColor3fv([c*0.8 for c in desk_color]) # Darker brown for chair
            glPushMatrix()
            glTranslatef(i * 2.5, 0.3, j * 2.5) # Behind desk
            glScalef(0.4, 0.6, 0.4)
            draw_cube(1)
            glPopMatrix()

    # Teacher desk
    glColor3fv(desk_color)
    glPushMatrix()
    glTranslatef(0, 0.7, -2.8) # Slightly higher and more forward
    glScalef(1.5, 0.5, 0.7)
    draw_cube(1)
    glPopMatrix()
    # Teacher chair
    glColor3fv([c*0.8 for c in desk_color])
    glPushMatrix()
    glTranslatef(0, 0.4, -2.2) 
    glScalef(0.5, 0.8, 0.5)
    draw_cube(1)
    glPopMatrix()

    # Avatars (simple cubes)
    student_avatar_color = [0.2, 0.5, 0.8] # Blueish
    teacher_avatar_color = [0.8, 0.3, 0.3] # Reddish

    for i in range(-1, 2):
        for j in range(2):
            glColor3fv(student_avatar_color)
            glPushMatrix()
            # Position on chair
            glTranslatef(i * 2.5, 0.3 + 0.3 + 0.25, j * 2.5) # x, on chair + half height, z
            glScalef(0.3, 0.5, 0.3)
            draw_cube(1)
            glPopMatrix()

    glColor3fv(teacher_avatar_color)
    glPushMatrix()
    glTranslatef(0, 0.4 + 0.4 + 0.3, -2.2) # On teacher chair
    glScalef(0.35, 0.6, 0.35)
    draw_cube(1)
    glPopMatrix()

def main():
    global window 

    if not glfw.init():
        print("Failed to initialize GLFW")
        sys.exit(1)

    # Request an OpenGL 3.2 core profile, for example, if you want to use modern OpenGL later
    # glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    # glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
    # glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE) # For MacOS

    window = glfw.create_window(width, height, "Virtual Classroom - GLFW", None, None)
    if not window:
        glfw.terminate()
        print("Failed to create GLFW window")
        sys.exit(1)

    glfw.make_context_current(window)

    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    init_gl()
    framebuffer_size_callback(window, width, height) # Initial call to set projection

    print("Controls:")
    print("  Mouse Drag: Orbit camera")
    print("  +/- or Numpad +/-: Zoom in/out")
    print("  C: Toggle clipping plane")
    print("  J/K: Move clipping plane (when enabled)")
    print("  Esc: Quit")

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity() 

        eye_x = camera_distance * -sin(radians(camera_yaw)) * cos(radians(camera_pitch))
        eye_y = camera_distance * sin(radians(camera_pitch))
        eye_z = camera_distance * cos(radians(camera_yaw)) * cos(radians(camera_pitch)) # Adjusted from -cos to cos for standard orbit

        gluLookAt(eye_x, eye_y, eye_z, 0, 0, 0, 0, 1, 0)

        # Setup clipping plane if enabled
        if clipping_enabled:
            # Plane equation: Ax + By + Cz + D = 0. We'll use 0x + 0y + 1z + clip_plane_d_offset = 0
            # This plane is parallel to XY, cutting along Z.
            # Positive D moves the plane in the -Z direction relative to its normal (0,0,1)
            clip_plane_equation = [0.0, 0.0, 1.0, clip_plane_d_offset]
            glClipPlane(GL_CLIP_PLANE0, clip_plane_equation)
            glEnable(GL_CLIP_PLANE0)
        else:
            glDisable(GL_CLIP_PLANE0)

        draw_classroom()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
