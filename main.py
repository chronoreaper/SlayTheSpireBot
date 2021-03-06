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
    win32api.SetCursorPos((wincap.offset_x ,wincap.offset_y))
    time.sleep(0.2)

def FindImage(image, show = False, click = True, threshold = 0.8, tries = 1):
    screenshot = wincap.get_screenshot()
    image = cv2.imread('img/' + image + '.PNG')
    if image is None:
        return False, (0, 0)
    h, w = image.shape[:-1]
    pos = (0, 0)

    loc = [[]]
    while tries > 0 and len(loc[0]) == 0:
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
        if (tries > 1):
            time.sleep(0.1)
        tries -= 1

    return len(loc[0]) > 0, pos

def NavigateMainMenu():
    print("Press Play")
    FindImage("Menu_Play", tries = 5)
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
    MoveMouseOffScreen()
    print("Press Leave")
    FindImage("Menu_Leave", tries=3)
    time.sleep(1)

MAP_COMBAT = ["Enemy", "Elite", "SuperElite", "Boss1"]

def NavigateMap():
    print("Navigate Map")
    event = -1
    tries = 99
    while event == -1 and tries > 0:
        if FindImage("Map_Rest")[0]:
            print("Goto Rest")
            event = 4
        elif FindImage("Map_Merchant")[0]:
            print("Goto Merchant")
            event = 3
        elif FindImage("Map_Unknown")[0]:
            print("Goto unknown")
            event = 1
        elif FindImage("Map_Chest")[0]:
            print("Goto Chest")
            event = 2

        for enemy in MAP_COMBAT:
            if FindImage("Map_" + enemy)[0]:
                print("Go to " + enemy)
                event = 0
        time.sleep(0.1)
        tries -= 1
    time.sleep(1)
    return event

###############################
#     Combat                
#############################


CARD_NAMES = ["Bash", "ThunderClap", "PerfectedStrike", "Shrug", "IronWave", "Clothsline", "Cleave", "TwinStrike", "WildStrike", "Strike", "Defend", "Bloodletting", "Anger"]
KEYS = [ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE]
ENEMIES = ["GremlinWizard", "ShieldGremlin", "Cultist", "SpikeSlimeS", "AcidSlimeM", "JawWorm", "Louse", "Louse2", "Louse3", "AcidSlimeS", "FatGremlin", "Slaver", "SneakyGremlin", "AngryGremlin", "Nob", "Sentry",
    "AcidSlimeL", "Fungi", "TheGuardian", "TheGuardian2", "Lagavulin", "Lagavulin2", "Looter"]

def Combat():
    MoveMouseOffScreen()
    enemies = GetEnemies()
    RewardScreen = False
    # Main Combat loop
    while len(enemies) > 0:
        energy = 3
        # Main Turn loop
        while (energy > 0 and len(enemies) > 0):
            hand = GetHand([''] * 6)
            for card in CARD_NAMES:
                isPlaying = True
                while (card in hand and isPlaying and len(enemies) > 0):
                    index = hand.index(card)
                    if (IsPlayable(card, index)):
                        print("Playing " + card)
                        PlayAttack(enemies[0])
                        hand.pop(index)
                        hand.append('')
                        time.sleep(0.1)
                        MoveMouseOffScreen()
                        enemies = GetEnemies()
                        CenterMouse()
                        if len(enemies) > 0:
                            hand = GetHand(hand)
                    else:
                        isPlaying = False
            energy = 0
            # MoveMouseOffScreen()
            # enemies = GetEnemies()

        MoveMouseOffScreen()
        enemies = GetEnemies()
        if (len(enemies) > 0):
            print("End Turn")
            pushKey(E)
            time.sleep(3)
        MoveMouseOffScreen()
        enemies = GetEnemies()
        # Just to be sure
        if (len(enemies) == 0):
            #if not FindImage("Reward_Screen", click=False)[0]:
            time.sleep(0.1)
            enemies = GetEnemies()
    
    Rewards()

def IsPlayable(name, index):
    isPlayable = False
    pushKey(KEYS[index])
    time.sleep(0.1)
    if (FindImage("Combat_" + name, click=False, threshold=0.6)[0]):
        isPlayable = True
    time.sleep(0.1)
    return isPlayable

def GetHand(hand = [''] * 6):
    print("Cards in Hand")
    time.sleep(0.1)
    CenterMouse()
    for i in range(len(hand)):
        if hand[i] == '':
            pushKey(KEYS[i])
            time.sleep(0.1)
            for card in CARD_NAMES:
                if (FindImage("Combat_" + card, click=False, threshold=0.6)[0]):
                    print(card)
                    hand[i] = card
                    break
            pushKey(KEYS[i])
    
    return hand

def GetEnemies():
    enemies = []
    for enemy in ENEMIES:
        exist, pos = FindImage("Enemy_" + enemy, click=False)
        if exist:
            enemies.append(Enemy(enemy, pos))
    return enemies

def PlayAttack(enemy):
    print("Attacking " + enemy.name)
    # Just to be sure
    for _ in range(3):
        Click(enemy.pos[0], enemy.pos[1])
        time.sleep(0.05)

class Enemy:
    name = ""
    pos = (0,0)
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos

##########################################
#        Rewards
#######################################

CARD_REWARDS = ["PerfectedStrike", "Anger", "IronWave", "Cleave", "Pummel", "Rage", "Shrug", "BloodforBlood", "TwinStrike", "ThunderClap", "WildStrike", "Bloodletting"]

def Rewards():
    # Rewards
    print("pick up gold")
    FindImage("Reward_Gold")

    time.sleep(0.1)
    MoveMouseOffScreen()
    # Pick up card
    print("Pick up card")
    FindImage("Reward_Card", tries = 2)
    MoveMouseOffScreen()
    time.sleep(0.5)

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
        time.sleep(1)
        print("proceed")
        FindImage("Reward_SkipPotion")
        FindImage("Reward_Proceed", tries=3)

    # print("Skip Rewards")
    # FindImage("Reward_Skip")

#####################################
#           Events
####################################

EVENTS = ["Heal", "Leave", "Attack", "Forget", "Disagree"]

def Event():
    clicked = True
    chosen = ""
    while clicked:
        MoveMouseOffScreen()
        for event in EVENTS:
            clicked = FindImage("Event_" + event, tries = 2)[0]
            if clicked:
                print("Clicked "  + event)
                chosen = event
                break
        time.sleep(1)
        if chosen == "Forget":
            time.sleep(1)
            FindImage("Deck_Strike")
            time.sleep(1)
            FindImage("Confirm")

        if chosen == "":
            Shop()
            Chest()
            Combat()

#####################################
#              Shop
####################################

def Shop():
    print("Skip Shop")
    time.sleep(1)
    FindImage("Shop_Skip", tries = 3)
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
#Combat()
NavigateMainMenu()
isGameover = FindImage("End_Continue")[0]

while not isGameover:
    event = NavigateMap()
    if event == 0:
        Combat()
    elif event == 1:
        Event()
    elif event == 2:
        Chest()
    elif event == 3:
        Shop()
    elif event == 4:
        Rest()
    isGameover = FindImage("End_Continue")[0]

time.sleep(0.5)
FindImage("End_MainMenu")
