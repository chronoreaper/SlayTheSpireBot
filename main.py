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

def Click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def CenterMouse():
    x = wincap.cropped_x + (int)(wincap.w / 2)
    y = wincap.cropped_y + (int)(wincap.h / 2)
    win32api.SetCursorPos((x,y))


def FindImage(image, show = False, click = True, threshold = .8):
    screenshot = wincap.get_screenshot()
    image = cv2.imread('img/' + image + '.PNG')
    h, w = image.shape[:-1]

    res = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    if (len(loc[0]) > 0):
        pos = (0, 0)
        for pt in zip(*loc[::-1]):  # Switch collumns and rows
            cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            pos = (pt[0] + 1 + (int)(w / 2), pt[1] + 4 + (int)(h))

    if (show):
        cv2.imshow('screen', screenshot)
        cv2.waitKey(0)

    if (len(loc[0]) > 0):    
        if (click):
            Click(pos[0], pos[1])
    return len(loc[0]) > 0

def NavigateMainMenu():
    print("Press Play")
    FindImage("Menu_Play")
    time.sleep(1)
    print("Press Standard")
    FindImage("Menu_Standard")
    time.sleep(1)
    print("Press IronClad")
    FindImage("Menu_Iron")
    time.sleep(1)
    print("Press Embark")
    FindImage("Menu_Embark")
    time.sleep(3)
    print("Press Talk")
    FindImage("Menu_Talk")
    time.sleep(1)
    print("Press 7 Max HP")
    FindImage("Menu_7Max")
    time.sleep(1)
    print("Press Leave")
    FindImage("Menu_Leave")
    time.sleep(1)

def NavigateMap():
    FindImage("Map_Enemy")
    time.sleep(1)

###############################
#     Combat                
#############################


CARD_NAMES = ["Strike", "Defend"]
KEYS = [ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE]

def Combat():
    energy = 3
    hand = GetHand()
    if ("Strike" in hand):
        PlayAttack(hand.index("Strike"))

def GetHand():
    CenterMouse()
    cards = [''] * 10
    for i in len(KEYS):
        pressKey(KEYS[i])
        time.sleep(0.2)
        releaseKey(KEYS[i])
        time.sleep(1)
        for card in CARD_NAMES:
            if (FindImage("Combat_" + card, click=False)):
                cards[i] = card
                break
    
    return cards

def PlayAttack(hotkey):
    #ToDo
    print("Play Attack")


# Main loop
time.sleep(2)
NavigateMainMenu()
NavigateMap()
Combat()