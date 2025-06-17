from picamera2 import Picamera2


print("Hello world")
# Initialize the camera
picam2 = Picamera2()
picam2.start()

# Capture an image and save it
picam2.capture_file("/home/pi/Desktop/Python_Proj/captured_image.jpg")

# Stop the camera
picam2.stop()