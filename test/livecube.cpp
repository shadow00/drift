// g++ livecube.cpp -o livecube -lGL -lGLU -lGLEW -lglfw
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <chrono>
#include <cmath>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <thread>
#include <mutex>
#include <queue>
#include <condition_variable>

// Window dimensions, which will be updated on resize
int windowWidth = 800;
int windowHeight = 600;
GLFWwindow* window;
bool isFullscreen = false;
int windowedWidth = windowWidth, windowedHeight = windowHeight;

// Thread-safe queue for serial data
std::queue<std::string> dataQueue;
std::mutex queueMutex;
std::condition_variable dataCondition;
bool isRunning = true;

// Vertex data for the cube
double cubeVertices[] = {
    -0.5f, -0.5f, -0.5f,
     0.5f, -0.5f, -0.5f,
     0.5f,  0.5f, -0.5f,
    -0.5f,  0.5f, -0.5f,
    -0.5f, -0.5f,  0.5f,
     0.5f, -0.5f,  0.5f,
     0.5f,  0.5f,  0.5f,
    -0.5f,  0.5f,  0.5f,
};

// Color data for the cube (one color per face)
double cubeColors[] = {
    1.0f, 0.0f, 0.0f, // Red - Face 1
    0.0f, 1.0f, 0.0f, // Green - Face 2
    0.0f, 0.0f, 1.0f, // Blue - Face 3
    1.0f, 1.0f, 0.0f, // Yellow - Face 4
    1.0f, 0.0f, 1.0f, // Magenta - Face 5
    0.0f, 1.0f, 1.0f, // Cyan - Face 6
};

// Index data for the cube's faces
unsigned int cubeIndices[] = {
    0, 1, 2, 2, 3, 0,
    4, 5, 6, 6, 7, 4,
    0, 1, 5, 5, 4, 0,
    2, 3, 7, 7, 6, 2,
    0, 3, 7, 7, 4, 0,
    1, 2, 6, 6, 5, 1
};

// Function to normalize a quaternion
// void normalizeQuaternion(float& w, float& x, float& y, float& z) {
void normalizeQuaternion(double (&orientation)[4]) {
    double w = orientation[0];
    double x = orientation[1];
    double y = orientation[2];
    double z = orientation[3];
    double norm = sqrt(w * w + x * x + y * y + z * z);
    if (norm > 0.0d) {
        w /= norm;
        x /= norm;
        y /= norm;
        z /= norm;
    }
}

struct Cube {
    double position[3];
    double orientation[4]; // Quaternion (w, x, y, z)

    void update(double x, double y, double z, double w, double qx, double qy, double qz) {
        position[0] = x;
        position[1] = y;
        position[2] = -z;
        orientation[0] = w;
        orientation[1] = qx;
        orientation[2] = qy;
        orientation[3] = qz;
    }

    void draw() {
        glPushMatrix();
        glTranslatef(position[0], position[1], position[2]);
        // Apply quaternion rotation
        glRotatef(2 * std::acos(orientation[0]) * 180.0 / 3.14159265358979323846, orientation[1], orientation[2], orientation[3]);

        glBegin(GL_TRIANGLES);
        // for (unsigned int i = 0; i < 36; i++) {
        //     glVertex3f(cubeVertices[cubeIndices[i] * 3],
        //                cubeVertices[cubeIndices[i] * 3 + 1],
        //                cubeVertices[cubeIndices[i] * 3 + 2]);
        // }
        for (unsigned int i = 0; i < 36; i++) {
            // Set color for each vertex based on its index
            int colorIndex = (i / 6); // Each face has 6 vertices
            glColor3f(cubeColors[colorIndex * 3], cubeColors[colorIndex * 3 + 1], cubeColors[colorIndex * 3 + 2]);
            glVertex3f(cubeVertices[cubeIndices[i] * 3],
                       cubeVertices[cubeIndices[i] * 3 + 1],
                       cubeVertices[cubeIndices[i] * 3 + 2]);
        }
        glEnd();
        glPopMatrix();
    }
};

// Set up perspective projection with the current aspect ratio
void setupPerspective() {
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(45.0f, static_cast<float>(windowWidth) / static_cast<float>(windowHeight), 0.1f, 100.0f);
    glMatrixMode(GL_MODELVIEW);
}

void setupCamera() {
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    // Position the camera at (eyeX, eyeY, eyeZ), looking towards (centerX, centerY, centerZ)
    // and setting the "up" vector to (upX, upY, upZ).
    // Adjust the eye and up vectors as needed to correct the view orientation.
    gluLookAt(
        0.0f, 5.0f, 0.0f,   // Camera position (eyeX, eyeY, eyeZ)
        0.0f, 0.0f, 0.0f,   // Look-at point (centerX, centerY, centerZ)
        0.0f, 0.0f, 1.0f    // Up vector (upX, upY, upZ)
    );
}

// Callback function to handle window resizing
void framebuffer_size_callback(GLFWwindow* window, int width, int height) {
    windowWidth = width;
    windowHeight = height;

    // Adjust the viewport and reset the perspective projection
    glViewport(0, 0, width, height);
    setupPerspective();
}

// Toggle between fullscreen and windowed mode
void toggleFullscreen() {
    isFullscreen = !isFullscreen;

    if (isFullscreen) {
        // Get the primary monitor and its video mode for fullscreen resolution
        const GLFWvidmode* mode = glfwGetVideoMode(glfwGetPrimaryMonitor());
        glfwSetWindowMonitor(window, glfwGetPrimaryMonitor(), 0, 0, mode->width, mode->height, GLFW_DONT_CARE);
    } else {
        // Switch back to windowed mode at the original window dimensions
        glfwSetWindowMonitor(window, nullptr, 100, 100, windowedWidth, windowedHeight, GLFW_DONT_CARE);
    }
}

void processInput(Cube& cube, const std::string& data) {
    std::istringstream stream(data);
    std::string token;
    std::vector<double> values;

    while (std::getline(stream, token, ',')) {
        // Trim whitespace from the token
        token.erase(0, token.find_first_not_of(" \t\n\r")); // LTrim
        token.erase(token.find_last_not_of(" \t\n\r") + 1); // RTrim

        // Skip empty tokens
        if (token.empty()) {
            continue; // Ignore empty tokens
        }

        try {
            values.push_back(std::stod(token));
        } catch (const std::invalid_argument& e) {
            std::cerr << "Invalid argument: " << token << " cannot be converted to double." << std::endl;
            return; // Exit if there's a parsing error
        } catch (const std::out_of_range& e) {
            std::cerr << "Out of range: " << token << " is out of double range." << std::endl;
            return; // Exit if there's a parsing error
        }
    }

    if (values.size() == 14) { // Ensure enough values are present
        // std::cout << data << std::endl;
        cube.update(values[1], values[2], values[3], values[10], values[11], values[12], values[13]);
        std::cout << values[1] << ',' << values[2] << ',' << values[3] << ',' << values[10] << ',' << values[11] << ',' << values[12] << ',' << values[13] << std::endl;
    }
    // else
    //     std::cout << "Error: parsed " << values.size() << " values from " << data << std::endl;
}

void setupOpenGL() {
    glEnable(GL_DEPTH_TEST);
    glEnableClientState(GL_VERTEX_ARRAY);
    glVertexPointer(3, GL_DOUBLE, 0, cubeVertices);
}

// Serial port setup
int setupSerial(const char* portName) {
    int serialPort = open(portName, O_RDWR | O_NOCTTY | O_NDELAY);
    if (serialPort == -1) {
        std::cerr << "Error opening serial port." << std::endl;
        return -1;
    }

    struct termios options;
    tcgetattr(serialPort, &options);
    options.c_cflag = B115200 | CS8 | CLOCAL | CREAD; // Set baud rate and config
    options.c_iflag = IGNPAR; // Ignore framing errors
    options.c_oflag = 0;      // Raw output
    options.c_lflag = 0;      // Raw input

    tcflush(serialPort, TCIFLUSH);
    tcsetattr(serialPort, TCSANOW, &options);

    return serialPort;
}

// Thread function to read from the serial port
void serialReaderThread(int serialPort) {
    std::string accumulatedData; // To store incoming serial data
    char buffer[4096]; // Buffer for reading data

    while (isRunning) {
        // Read data from the serial port
        int bytesRead = read(serialPort, buffer, sizeof(buffer) - 1);

        if (bytesRead < 0) {
            // std::cerr << "Error reading from serial port." << std::endl;
            continue; // Handle read error
        }

        if (bytesRead == 0) {
            continue; // No more data
        }

        buffer[bytesRead] = '\0'; // Null-terminate the buffer
        accumulatedData += buffer; // Append read data to accumulatedData

        // Process complete lines
        size_t pos;
        while ((pos = accumulatedData.find('\n')) != std::string::npos) {
            std::string line = accumulatedData.substr(0, pos); // Extract the complete line
            accumulatedData.erase(0, pos + 1); // Remove the processed line from the buffer

            // Push the complete line into the queue for processing
            {
                std::lock_guard<std::mutex> lock(queueMutex);
                dataQueue.push(line);
                // std::cout << line << std::endl;
            }
            dataCondition.notify_one(); // Notify main loop of new data
        }
    }
}

int main() {
    if (!glfwInit()) return -1;

    window = glfwCreateWindow(800, 600, "3D Cube", nullptr, nullptr);
    if (!window) {
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);

    // Initialize GLEW
    if (glewInit() != GLEW_OK) {
        std::cerr << "Failed to initialize GLEW\n";
        return -1;
    }

    setupOpenGL();
    setupPerspective(); // Set up perspective projection
    glfwSwapInterval(0); // disable V-Sync, so fps aren't limited to 60

    // Set viewport and enable depth test
    glViewport(0, 0, windowWidth, windowHeight);
    glEnable(GL_DEPTH_TEST);

    // Set callback functions
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);

    Cube cube;
    std::string accumulatedData; // To store incomplete lines
    const char* serialPortName = "/dev/ttyUSB0"; // Adjust to your serial port
    int serialPort = setupSerial(serialPortName);
    if (serialPort == -1) {
        return -1;
    }

    // Start the serial reading thread
    std::thread serialThread(serialReaderThread, serialPort);

    auto lastTime = std::chrono::high_resolution_clock::now();
    int frameCount = 0;

    // Variables to track F key state
    int fKeyState = GLFW_RELEASE; // Current state of the F key
    int lastFKeyState = GLFW_RELEASE; // Previous state of the F key

    while (!glfwWindowShouldClose(window)) {
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        setupCamera(); // Set up the camera every frame

        // Process the incoming data from the serial reader thread
        std::unique_lock<std::mutex> lock(queueMutex);
        dataCondition.wait(lock, [] { return !dataQueue.empty() || !isRunning; }); // Wait for new data

        while (!dataQueue.empty()) {
            std::string inputLine = dataQueue.front();
            dataQueue.pop();
            lock.unlock(); // Unlock the mutex while processing the data
            processInput(cube, inputLine);
            lock.lock(); // Lock again for the next iteration
        }

        cube.draw();

        // Calculate FPS
        frameCount++;
        auto currentTime = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = currentTime - lastTime;

        if (elapsed.count() >= 1.0) { // Update FPS every second
            std::stringstream title;
            title << "3D Cube - FPS: " << frameCount;
            glfwSetWindowTitle(window, title.str().c_str());
            frameCount = 0;
            lastTime = currentTime;
        }

        glfwSwapBuffers(window);
        glfwPollEvents();

        // Toggle fullscreen only when F key is released after being pressed
        fKeyState = glfwGetKey(window, GLFW_KEY_F);
        if (fKeyState == GLFW_RELEASE && lastFKeyState == GLFW_PRESS) {
            toggleFullscreen();
        }
        lastFKeyState = fKeyState;

        // Exit on Esc or Q key press
        if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS || glfwGetKey(window, GLFW_KEY_Q) == GLFW_PRESS) {
            glfwSetWindowShouldClose(window, true);  // Signals to close the window
        }
    }

    isRunning = false; // Stop the serial reading thread
    dataCondition.notify_all(); // Notify the thread to wake up and exit
    serialThread.join(); // Wait for the thread to finish

    close(serialPort);
    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
