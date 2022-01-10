import cv2
import numpy as np
import os
from time import time
from windowcapture import WindowCapture
from vision import Vision

import win32api, win32con
from KeyboardTest import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# initialize the WindowCapture class
wincap = WindowCapture('Slay the Spire')

# load an empty Vision class
vision_limestone = Vision(None)


def Click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def FindImage():
    img_rgb = cv2.imread('mario.png')
    template = cv2.imread('mario_coin.png')
    w, h = template.shape[:-1]

    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

    cv2.imwrite('result.png', img_rgb)