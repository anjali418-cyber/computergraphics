# Implementation Details: 3D Virtual Classroom

## 1. Initial Setup and Technology Stack

- **Programming Language**: Python 3.x
- **Graphics API**: OpenGL (via PyOpenGL)
- **Initial Windowing/Input Library**: FreeGLUT (via PyOpenGL_accelerate)
- **Revised Windowing/Input Library**: GLFW

## 2. Transition from FreeGLUT to GLFW

The project initially started with FreeGLUT for window creation and input handling. However, persistent issues were encountered with loading the `freeglut.dll` library, specifically `OpenGL.error.NullFunctionError: Attempt to call an undefined function glutInit` (often associated with `WinError 193` indicating an architecture mismatch between Python and the DLL).

Despite attempts to resolve this by:
- Verifying DLL placement and architecture (32-bit vs 64-bit).
- Ensuring Visual C++ Redistributables were installed.

A decision was made to switch to **GLFW** as a more modern and robust alternative for windowing and input management with OpenGL. This resolved the DLL dependency issues and allowed development to proceed smoothly.

## 3. GLFW-based Implementation

### 3.1. Window and Context Management

- GLFW was used to initialize the windowing system, create an OpenGL context, and manage the application window.
- Key GLFW functions used: `glfw.init()`, `glfw.create_window()`, `glfw.make_context_current()`, `glfw.swap_buffers()`, `glfw.poll_events()`.

### 3.2. Input Handling

- **Keyboard**: Callbacks (`glfw.set_key_callback`) were set up for:
    - `Esc` key: Close the application.
    - `+` / `-` keys (and Numpad `+` / `-`): Zoom in/out.
- **Mouse**: Callbacks (`glfw.set_cursor_pos_callback`, `glfw.set_mouse_button_callback`) were set up for:
    - Left Mouse Button Drag: Orbit the camera around the scene's center.

### 3.3. Rendering Primitives

- Since GLFW does not provide built-in shape drawing functions like FreeGLUT's `glutSolidCube`, a custom `draw_cube(size)` function was implemented using immediate mode OpenGL (`glBegin(GL_QUADS)`, `glVertex3f`, `glNormal3f`, `glEnd`).
- This `draw_cube` function is used to render all cuboidal elements in the scene (walls, floor, desks, chairs, board, avatars).

### 3.4. Scene Composition

The `draw_classroom()` function orchestrates the rendering of the scene:
- **Floor**: A large, thin grey cube.
- **Walls**: Three tall, thin light-beige cubes (back, left, right).
- **Chalkboard**: A dark green, thin cube on the back wall.
- **Desks and Chairs**: Brown cubes, scaled and positioned appropriately. Student desks are smaller and arranged in rows. A larger teacher's desk is at the front.
- **Avatars**: Simple cubes representing students (blueish) and a teacher (reddish), positioned on chairs.

Colors for objects are set using `glColor3fv()` before calling `draw_cube()`.

### 3.5. Camera System

- **Projection**: A perspective projection is set up using `gluPerspective()` in the `reshape()` function (called initially and on window resize).
- **View Transformation**: The camera's view is controlled by `gluLookAt()`.
    - **Orbiting**: Mouse drag input modifies `camera_angle_x` and `camera_angle_y`. The camera's position is calculated trigonometrically based on these angles and the `camera_distance` (zoom level) to orbit around the point `(0, 1, 0)`.
    - **Zooming**: Keyboard input modifies `camera_distance`.

### 3.6. Lighting

- Basic lighting is enabled to give depth to the scene:
    - `glEnable(GL_LIGHTING)` and `glEnable(GL_LIGHT0)`.
    - A single positional light (`GL_LIGHT0`) is defined with ambient, diffuse, and specular components.
    - `glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ...)` sets a global ambient light level.
    - `glEnable(GL_COLOR_MATERIAL)` with `glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)` allows `glColor()` calls to define the ambient and diffuse material properties of objects.
    - Default specular material properties and shininess are set using `glMaterialfv()` and `glMaterialf()`.
    - `glEnable(GL_DEPTH_TEST)` ensures correct depth perception.
    - `glEnable(GL_NORMALIZE)` ensures normal vectors are correctly scaled for lighting calculations.

## 4. Clipping (Planned)

Demonstration of 3D clipping is a key project requirement. This will be implemented by introducing one or more user-controlled clipping planes (`glClipPlane()`, `glEnable(GL_CLIP_PLANEi)`). Keyboard controls will be added to enable/disable and manipulate the position/orientation of these planes to visually cut through the classroom scene.
