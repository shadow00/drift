# Requirements:
# llvmlite==0.43.0
# numba==0.60.0
# numpy==2.0.2
# numpy-quaternion==2024.0.3
# pygame==2.6.1
# PyOpenGL==3.1.7
# pyserial==3.5
# quaternionic==1.0.12
# scipy==1.14.1
# spherical==1.0.14
# spherical-functions==2022.4.5
# spinsfast==2022.4.6

import serial
import OpenGL.GL as gl
import OpenGL.GLU as glu
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # Hide pygame welcome message
import pygame
import numpy as np
import time


# Initialize serial communication
ser = serial.Serial('/dev/ttyUSB0', 115200)  # Replace with your serial port

last_position = np.array([0, 0, 0])

# Cube vertices
vertices = [
    [-1, -1, -1],
    [1, -1, -1],
    [1, 1, -1],
    [-1, 1, -1],
    [-1, -1, 1],
    [1, -1, 1],
    [1, 1, 1],
    [-1, 1, 1]
]

edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

# # Define axis colors
# AXIS_COLORS = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]

# # Axis endpoints
# AXIS_ENDPOINTS = [
#     (-1, -1, -1),
#     (1, -1, -1),
#     (1, 1, -1),
#     (-1, 1, -1),
#     (-1, -1, 1),
#     (1, -1, 1),
#     (1, 1, 1),
#     (-1, 1, 1)
# ]

axis_verts = (
    (-7.5, 0.0, 0.0),
    ( 7.5, 0.0, 0.0),
    ( 0.0,-7.5, 0.0),
    ( 0.0, 7.5, 0.0),
    ( 0.0, 0.0,-7.5),
    ( 0.0, 0.0, 7.5)
    )

axes = (
    (0,1),
    (2,3),
    (4,5)
    )

axis_colors = (
    (1.0,0.0,0.0), # Red
    (0.0,1.0,0.0), # Green
    (0.0,0.0,1.0)  # Blue
    )

def Axis():
    gl.glBegin(gl.GL_LINES)
    for color,axis in zip(axis_colors,axes):
        gl.glColor3fv(color)
        for point in axis:
            gl.glVertex3fv(axis_verts[point])
    gl.glEnd()

# # Cube vertices
# CUBE_VERTICES = [
#     [-1, -1, -1],
#     [1, -1, -1],
#     [1, 1, -1],
#     [-1, 1, -1],
#     [-1, -1, 1],
#     [1, -1, 1],
#     [1, 1, 1],
#     [-1, 1, 1]
# ]

def parse_data(data):
    values = data.split(',')

    # if len(values) != 20:
    if len(values) != 14:
        return None

    return np.array([
        float(values[0]),  # Timestamp
        float(values[1]), float(values[2]), float(values[3]),  # Acceleration
        # float(values[4]), float(values[5]), float(values[6]),  # Velocity
        # float(values[7]), float(values[8]), float(values[9]),  # Position
        # float(values[10]), float(values[11]), float(values[12]),  # Angular velocity
        # float(values[13]), float(values[14]), float(values[15]),   # Attitude
        # float(values[16]), float(values[17]),  # Quaternions w, x
        # float(values[18]), float(values[19])   # Quaternions y, z
        float(values[4]), float(values[5]), float(values[6]),  # Angular velocity
        float(values[7]), float(values[8]), float(values[9]),   # Attitude
        float(values[10]), float(values[11]),  # Quaternions w, x
        float(values[12]), float(values[13])   # Quaternions y, z
    ])

def euler_to_matrix(roll, pitch, yaw):
    cosd = lambda degrees: np.cos(np.deg2rad(degrees))
    sind = lambda degrees: np.sin(np.deg2rad(degrees))

    c, s = cosd, sind

    Rx = np.array([[1, 0, 0],
                   [0, c(roll), -s(roll)],
                   [0, s(roll), c(roll)]])

    Ry = np.array([[c(pitch), 0, s(pitch)],
                   [0, 1, 0],
                   [-s(pitch), 0, c(pitch)]])

    Rz = np.array([[c(yaw), -s(yaw), 0],
                   [s(yaw), c(yaw), 0],
                   [0, 0, 1]])

    # return Rz @ Ry @ Rx
    rotation_matrix_3x3 = Rz @ Ry @ Rx

    rotation_matrix_4x4 = np.eye(4)
    rotation_matrix_4x4[:3, :3] = rotation_matrix_3x3

    return rotation_matrix_4x4

def euler_to_quaternion(roll, pitch, yaw):
    # https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
    qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
    qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)

    return np.array([qw, qx, qy, qz])

def apply_roll_pitch_yaw_rotation(roll, pitch, yaw, translation_vector):
    # Create rotation matrix
    R = np.stack([
        [np.cos(yaw) * np.cos(pitch),
         np.sin(roll) * np.sin(pitch) * np.cos(yaw) - np.cos(roll) * np.sin(yaw),
         np.cos(roll) * np.sin(pitch) * np.cos(yaw) + np.sin(roll) * np.sin(yaw)],

        # [-np.cos(yaw) * np.sin(pitch),
        [np.cos(pitch) * np.sin(yaw),
         np.sin(roll) * np.sin(pitch) * np.sin(yaw) + np.cos(roll) * np.cos(yaw),
        #  -np.cos(roll) * np.sin(pitch) * np.sin(yaw) + np.sin(roll) * np.cos(yaw)],
         np.cos(roll) * np.sin(pitch) * np.sin(yaw) - np.sin(roll) * np.cos(yaw)],

        # [np.sin(yaw),
        [-np.sin(pitch),
         np.sin(roll) * np.cos(pitch),
        #  -np.cos(roll) * np.cos(pitch)]
         np.cos(roll) * np.cos(pitch)]
    ], axis=0)

    # Apply rotation to translation vector
    rotated_translation = np.dot(R, translation_vector)

    return rotated_translation


def mult_quat(q1, q2):
    # Quaternion multiplication

    q3 = np.copy(q1)
    q3[0] = q1[0]*q2[0] - q1[1]*q2[1] - q1[2]*q2[2] - q1[3]*q2[3]
    q3[1] = q1[0]*q2[1] + q1[1]*q2[0] + q1[2]*q2[3] - q1[3]*q2[2]
    q3[2] = q1[0]*q2[2] - q1[1]*q2[3] + q1[2]*q2[0] + q1[3]*q2[1]
    q3[3] = q1[0]*q2[3] + q1[1]*q2[2] - q1[2]*q2[1] + q1[3]*q2[0]
    return q3


def rotate_quat(quat, vect):
    # Rotate a vector with the rotation defined by a quaternion

    # Transfrom vect into an quaternion
    vect = np.append([0],vect)
    # Normalize it
    norm_vect = np.linalg.norm(vect)
    norm_quat = np.linalg.norm(quat)
    if norm_vect != 0:
        vect = vect/norm_vect
    if norm_quat != 0:
        quat = quat/norm_quat
    # Computes the conjugate of quat
    quat_ = np.append(quat[0],-quat[1:])
    # The result is given by: quat * vect * quat_
    res = mult_quat(quat, mult_quat(vect,quat_)) * norm_vect
    # res = mult_quat(quat_, mult_quat(vect,quat))
    # norm_res = np.linalg.norm(res)
    # if norm_res != 0:
    #     res = res/norm_res
    return res[1:]


def conjugate_quat(quat):
    # Computes the conjugate of quat
    return np.append(quat[0],-quat[1:])


def draw_cube():
    global last_position

    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    # Read serial data
    line = ser.readline().decode('utf-8').strip()
    if not line:
        return

    if line.startswith("[WARN]"):
        print(line)
        return

    # Parse data
    data = parse_data(line)
    if data is None:
        return

    # Update cube position based on parsed data
    ax, ay, az = data[1:4]  # Extract acceleration data
    # vx, vy, vz = data[1:4]  # Extract velocity data
    # x, y, z = data[7:10]  # Extract position data
    # roll, pitch, yaw = data[13:16]  # Extract attitude data
    # qw, qx, qy, qz = data[16:]  # Extract quaternion data
    roll, pitch, yaw = data[7:10]  # Extract attitude data
    qw, qx, qy, qz = data[10:]  # Extract quaternion data
    # rotation_quat = np.array([qw, qx, qy, qz])
    rotation_quat = np.array([qw, qx, qz, qy])
    # rotation_quat = np.array([qw, qy, qz, qx])
    # rotation_quat = euler_to_quaternion(roll, pitch, yaw)
    # rotation_quat = euler_to_quaternion(roll, yaw, pitch)
    # rotation_matrix = euler_to_matrix(roll, pitch, yaw)
    rotation_matrix = euler_to_matrix(roll, yaw, pitch)
    # new_position = np.array([-ax, az-1, -ay])
    # new_position = np.array([-ax, -az+1, -ay])
    new_position = np.array([-ax, -az+1, -ay])
    # new_position = np.array([-vx, vz, -vy])
    # new_position = np.array([-x, z, -y])
    new_position = rotate_quat(rotation_quat, new_position)
    # new_position = apply_roll_pitch_yaw_rotation(roll, yaw, pitch, new_position)
    translation_vector = new_position - last_position
    # translation_vector = rotate_quat(rotation_quat, translation_vector)
    # last_position = new_position
    # last_position = rotate_quat(conjugate_quat(rotation_quat), new_position)
    last_position = last_position + 0.99 * translation_vector

    # Update cube position
    # gl.glTranslatef(x, y, z)
    gl.glTranslatef(*translation_vector.tolist()) # Use position to represent acceleration

    # Update cube orientation using Euler angles
    # gl.glMatrixMode(gl.GL_MODELVIEW)
    # gl.glLoadIdentity()
    # gl.glRotatef(roll, 1, 0, 0)
    # gl.glRotatef(pitch, 0, 1, 0)
    # gl.glRotatef(yaw, 0, 0, 1)
    gl.glPushMatrix()
    gl.glMultMatrixf(rotation_matrix.T)

    # Draw edges
    gl.glBegin(gl.GL_LINES)
    gl.glColor3fv((1.0,1.0,1.0))
    for edge in edges:
        gl.glVertex3fv(vertices[edge[0]])
        gl.glVertex3fv(vertices[edge[1]])
    gl.glEnd()

    gl.glPopMatrix()

    # gl.glBegin(gl.GL_QUADS)
    # for face in [[0, 1, 2, 3], [4, 5, 6, 7], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]:
    #     for vertex in face:
    #         gl.glVertex3fv(CUBE_VERTICES[vertex])
    # gl.glEnd()

    pygame.display.flip()


def drawText(position, textString, size):
    font = pygame.font.SysFont("hacknerdfont", size, True)
    # textSurface = font.render(textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textSurface = font.render(textString, True, (0, 0, 0, 255), (255, 255, 255, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    gl.glRasterPos3d(*position)
    gl.glDrawPixels(textSurface.get_width(), textSurface.get_height(), gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, textData)


def main():
    # Initialize Pygame
    pygame.init()
    display = (800, 600)
    screen = pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Serial Data Visualization")

    # OpenGL setup
    glu.gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    # gl.glDepthFunc(gl.GL_LEQUAL)
    gl.glTranslatef(0.0, 0.0, -7.5)
    # gl.glTranslatef(0.0,0.0,-17.5)

    clock = pygame.time.Clock()
    running = True

    # Using depth test to make sure closer colors are shown over further ones
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)

    while running:
        event = pygame.event.poll()
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_cube()
        # gl.glMatrixMode(gl.GL_PROJECTION)
        # Axis()
        drawText((-2.6, 1.8, 2), f"FPS: {clock.get_fps():.0f}", 10)
        # print(f"FPS: {clock.get_fps():.0f}")
        clock.tick(300)  # Limit to 200 FPS

    ser.close()
    pygame.quit()

if __name__ == "__main__":
    main()
