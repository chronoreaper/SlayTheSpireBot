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
    x = wincap.offset_x + (int)(wincap.w / 2)
    y = wincap.offset_y + (int)((wincap.h)/ 2)
    win32api.SetCursorPos((x,y))

def MoveMouseOffScreen():
    win32api.SetCursorPos((0,0))

def FindImage(image, show = False, click = True, threshold = .6):
    screenshot = wincap.get_screenshot()
    image = cv2.imread('img/' + image + '.PNG')
    if len(image) <= 0:
        return False, (0, 0)
    h, w = image.shape[:-1]
    pos = (0, 0)

    res = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    if (len(loc[0]) > 0):
        for pt in zip(*loc[::-1]):  # Switch collumns and rows
            cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            pos = (pt[0] + 1 + (int)(w / 2) + wincap.offset_x - wincap.cropped_x, pt[1] + 4 + (int)(h) + wincap.offset_y - wincap.cropped_y)

    if (show):
        cv2.imshow('screen', screenshot)
        cv2.waitKey(0)

    if (len(loc[0]) > 0):    
        if (click):
            # Press twice in case
            Click(pos[0], pos[1])
            time.sleep(0.1)
            Click(pos[0], pos[1])
    return len(loc[0]) > 0, pos

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
    event = -1
    tries = 3
    while event == -1 and tries > 0:
        if FindImage("Map_Rest")[0]:
            print("Goto unknown")
            event = 4
        elif FindImage("Map_Merchant")[0]:
            print("Goto unknown")
            event = 3
        elif FindImage("Map_Unknown")[0]:
            print("Goto unknown")
            event = 1
        elif FindImage("Map_Enemy")[0]:
            print("Goto enemy")
            event = 0
        elif FindImage("Map_Chest")[0]:
            print("Goto unknown")
            event = 2
        time.sleep(0.2)
        tries -= 1
    time.sleep(1)
    return event

###############################
#     Combat                
#############################


CARD_NAMES = ["Shrug", "Clothsline", "Bash", "ThunderClap", "TwinStrike", "Strike", "Defend"]
KEYS = [ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE]
ENEMIES = ["Cultist", "SpikeSlimeS", "AcidSlimeM", "JawWorm", "Louse", "AcidSlimeS", "FatGremlin", "Slaver", "SneakyGremlin"]

def Combat():
    enemies = GetEnemies()

    # Main Combat loop
    while len(enemies) > 0:
        energy = 3
        # Main Turn loop
        while (energy > 0 and len(enemies) > 0):
            cardPlay = False
            hand = GetHand()
            time.sleep(0.3)
            for card in CARD_NAMES:
                if (card in hand):
                    PlayAttack(KEYS[hand.index(card)], enemies[0])
                    cardPlay = True
                    break
            if not cardPlay:
                energy = 0
            time.sleep(0.5)
            enemies = GetEnemies()
            
        pushKey(E)
        time.sleep(6)
    
    Rewards()

def GetHand():
    print("Cards in Hand")
    CenterMouse()
    cards = [''] * 10
    for i in range(len(cards)):
        pushKey(KEYS[i])
        time.sleep(0.5)
        for card in CARD_NAMES:
            if (FindImage("Combat_" + card, click=False)[0]):
                print(card)
                cards[i] = card
                break
        pushKey(KEYS[i])
    
    return cards

def GetEnemies():
    enemies = []
    for enemy in ENEMIES:
        exist, pos = FindImage("Enemy_" + enemy, click=False)
        if exist:
            enemies.append(Enemy(enemy, pos))
    return enemies

def PlayAttack(hotkey, enemy):
    print("Attacking " + enemy.name)
    pushKey(hotkey)
    time.sleep(1)
    # Just to be sure
    for _ in range(3):
        Click(enemy.pos[0], enemy.pos[1])
        time.sleep(0.1)

class Enemy:
    name = ""
    pos = (0,0)
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos

##########################################
#        Rewards
#######################################

CARD_REWARDS = ["IronWave", "Pummel", "Rage", "Shrug", "Headbut", "BloodforBlood", "Bloodletting", "TwinStrike", "ThunderStrike", "WildStrike"]

def Rewards():
    # Rewards
    print("pick up gold")
    FindImage("Reward_Gold")

    # Pick up card
    print("Pick up card")
    FindImage("Reward_Card")
    MoveMouseOffScreen()
    time.sleep(1)

    foundCard = False
    for card in CARD_REWARDS:
        if FindImage("Reward_Card_" + card)[0]:
            foundCard = True
            break
    if not foundCard:
    # Skip card
        print("Skip Card")
        FindImage("Reward_SkipCard")
        time.sleep(1)
        FindImage("Reward_SkipCard2")
    else:
        print("proceed")
        FindImage("Reward_Proceed")

    # print("Skip Rewards")
    # FindImage("Reward_Skip")

#####################################
#           Events
####################################

EVENTS = ["Heal", "Leave", "Attack"]

def Event():
    clicked = True
    while clicked:
        for event in EVENTS:
            clicked = FindImage("Event_" + event)[0]
            if clicked:
                break
        time.sleep(1)

#####################################
#              Shop
####################################

def Shop():
    FindImage("Shop_Skip")
    time.sleep(1)

######################################
#          Chest
##################################

def Chest():
    time.sleep(2)

    print("Skip chest")
    FindImage("Tresure_Skip")

######################################
#          Rest
##################################

def Rest():
    FindImage("Rest_Rest")
    time.sleep(2)
    FindImage("Shop_Proceed")


# Main loop
time.sleep(2)
#NavigateMainMenu()
# NavigateMap()
Combat()

isGameover = FindImage("End_Continue")[0]

while not isGameover:
    event = NavigateMap()
    if event == 0:
        Combat()
    elif event == 1:
        Event()
    elif event == 2:
        Rest()
    elif event == 3:
        Shop()
    elif event == 4:
        Chest()
    isGameover = FindImage("End_Continue")[0]

FindImage("End_MainMenu")
