import cv2 as opencv
import numpy as np
import pyautogui
from windowcapture import WindowCapture
from time import time, sleep

application_name = '3D Pinball for Windows - Space Cadet'
ball_initial_locations = [(323,415),(322,415)]
left_corner_near_flippler = []
BGR_BLUE = (255,0,0)
BGR_GREEN = (0,255,0)
BGR_RED = (0,0,255)
BGR_YELLOW = (0,255,255)

# These values were gathered using template matching also
hard_left_corner_rectangle = { "location":(66,321),"bottom_right":(187,438)}
hard_right_corner_rectangle = { "location":(186,321),"bottom_right":(296,438)}

def check_rect1_inside_rect2(rect1_upleft,rect1_bottomright,rect2_upleft,rect2_bottomright):    
    if rect1_upleft[0] > rect2_upleft[0] and rect1_upleft[1] > rect2_upleft[1] and rect1_bottomright[0] < rect2_bottomright[0] and rect1_bottomright[1] < rect2_bottomright[1]:
        return True
    return False

def compare_locations(last_location,location):
    # Check if its going up or down:
    if last_location[1] > location[1]:
        return "up"
    else: 
        #If is going down then Check direction 
        if location[0] > last_location[0]:
            return "right" 
        else:
            return "left"

# Select diferent colors depending on the direction the ball is heading
def get_rectangle_color(direction):
# Directions are colored(following BGR) to identified which action autogui should do
    choices = {'up':BGR_GREEN,'left':BGR_RED,'right':BGR_BLUE}
    return choices.get(direction)

def activate_flipper(direction):
    if direction == 'left':
        pyautogui.keyDown("Z")
        pyautogui.keyUp("Z")
    elif direction == 'right':
        pyautogui.keyDown("v")
        pyautogui.keyUp("v")

# Reading the template that will be matched
template = opencv.imread('assets/ball.jpg')
height, width, channels = template.shape

# Template Matching Algorithms available, the best one in tests was 4 and 5 
methods = [opencv.TM_CCOEFF, opencv.TM_CCOEFF_NORMED, opencv.TM_CCORR,
            opencv.TM_CCORR_NORMED, opencv.TM_SQDIFF, opencv.TM_SQDIFF_NORMED]

# WindowCapture is optimized to get Screenshot from Windows Applications
wincap = WindowCapture(application_name,window_offset_upandown=120,window_offset_rightandleft=160)
img_height, img_width, img_channels = wincap.get_screenshot().shape

# To Record a video out of our gameplay 
fourcc = opencv.VideoWriter_fourcc(*'mp4v')
out = opencv.VideoWriter('output.mp4',fourcc, 20.0, (2*img_width,img_height))

# Initializes last seen location with ball's initial position
last_location = list(ball_initial_locations[0])

loop_time = time()
while(True):
    img = wincap.get_screenshot()
    img2 = img.copy()

    # Check with which FPS we can take window screenshots 
    # print('FPS = {}'.format(1 / (time()-loop_time)))
    # loop_time = time()

    #Matches the template image against Screenshot img
    result = opencv.matchTemplate(img2, template, methods[3])
    min_val, max_val, min_loc, max_loc = opencv.minMaxLoc(result)

    if methods in [opencv.TM_SQDIFF, opencv.TM_SQDIFF_NORMED]:
        location = min_loc
    else:
        location = max_loc

    # Rectangles in opencv are drawn by two points one uperleft and other bottom right
    bottom_right = (location[0] + width, location[1] + height)

    # Compare ball locations to define direction it is going
    direction = compare_locations(last_location,location)
    
    # Draw rectangle around the ball according to direction color coding 
    rect_color = get_rectangle_color(direction)
    opencv.rectangle(img2, location, bottom_right, rect_color, 5)
    
    last_location = location

    # Heuristics 
    if location in ball_initial_locations:
        with pyautogui.hold('space'):  # Press the Shift key down and hold it.
            pyautogui.press(['up', 'up'],interval=2)
    
    # Press buttons to activate Left or Right Flippler 
    if check_rect1_inside_rect2(location,bottom_right,hard_left_corner_rectangle["location"],hard_left_corner_rectangle["bottom_right"]):
        pyautogui.keyDown("z")
        pyautogui.keyUp("z")

    if check_rect1_inside_rect2(location,bottom_right,hard_right_corner_rectangle["location"],hard_right_corner_rectangle["bottom_right"]):
        pyautogui.keyDown("v")
        pyautogui.keyUp("v")

    # Save frames from simulation and from the actual game on the video file
    numpy_horizontal_concat = np.concatenate((img, img2), axis=1)
    out.write(numpy_horizontal_concat)

    # Display the resulting frame
    opencv.imshow('Frame ',img2)

    # Press Q on keyboard to finish the program
    if opencv.waitKey(1) & 0xFF == ord('q'):
      break 

# When everything done, release the video capture object and the VideoWriter object
out.release()

# Closes all the frames
opencv.destroyAllWindows()

print('Done.')