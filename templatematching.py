import cv2 as opencv
from windowcapture import WindowCapture

# Compare ball locations to define direction it is going
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
    blue = (255,0,0)
    green = (0,255,0)
    red = (0,0,255)
    choices = {'up':green,'left':red,'right':blue}
    return choices.get(direction)


template = opencv.imread('assets/ball.jpg')
height, width, channels = template.shape

# Template Matching Algorithms available, the best one in tests was 4 and 5 
methods = [opencv.TM_CCOEFF, opencv.TM_CCOEFF_NORMED, opencv.TM_CCORR,
            opencv.TM_CCORR_NORMED, opencv.TM_SQDIFF, opencv.TM_SQDIFF_NORMED]

# WindowCapture is optimized to get Screenshot from Windows Applications
wincap = WindowCapture('3D Pinball for Windows - Space Cadet')



# Ball initial position
last_location = [325,415]
while(True):
    img = wincap.get_screenshot()
    img2 = img.copy()

    #Matches the template image against Screenshot img
    result = opencv.matchTemplate(img2, template, methods[3])
    min_val, max_val, min_loc, max_loc = opencv.minMaxLoc(result)
    if methods in [opencv.TM_SQDIFF, opencv.TM_SQDIFF_NORMED]:
        location = min_loc
    else:
        location = max_loc

    

    bottom_right = (location[0] + width, location[1] + height)
    direction = compare_locations(last_location,location)
    rect_color = get_rectangle_color(direction)
    opencv.rectangle(img2, location, bottom_right, rect_color, 5)
    last_location = location

    # Display the resulting frame
    opencv.imshow('Frame ',img2)

    # Press Q on keyboard to finish the program
    if opencv.waitKey(25) & 0xFF == ord('q'):
      break 

# Closes all the frames
opencv.destroyAllWindows()

print('Done.')