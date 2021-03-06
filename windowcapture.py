import numpy as np
import win32gui, win32ui, win32con


class WindowCapture:

    # properties
    w = 0
    h = 0
    hwnd = None

    def __init__(self, window_name, window_offset_upandown=0,window_offset_rightandleft=0):
        # Find the handle for the window we want to capture
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))

        # Get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0] - window_offset_rightandleft
        self.h = window_rect[3] - window_rect[1] - window_offset_upandown

    def get_screenshot(self):

        # Get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (0,0), win32con.SRCCOPY)

        # Convert the raw data into a format opencv can read
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # Free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # Dropping alpha channel to avoid cv.matchTemplate() errors
        img = img[...,:3]

        # Removes tuples from img array to avoid errors
        img = np.ascontiguousarray(img)

        return img

    # Find the name of the window you're interested in.
    def list_window_names(self):
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)