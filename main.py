import cv2
import numpy as np
import time
import autopy
import pyperclip
import pyautogui
import webbrowser
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import hand_tracking_service as hts
import speech_to_text_service as s2t

wCam, hCam = 640, 480

frameR = 100
smooth = 5
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# Настройка камеры
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

# Создание сервисов
hands_detector = hts.hand_tracking_service()
voice_detector = s2t.speech_to_text_service()

# Настройка взаимодействия с динамиками
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

wScreen, hScreen = autopy.screen.size()

start = 0
MOUSE_MODE = True

while True:
    # Нахождение точек id на изображении
    _, img = cap.read()
    img = hands_detector.find_hands(img)
    lmList, bbox = hands_detector.find_position(img)
    if len(lmList) != 0:
        if MOUSE_MODE:
            # Получение координат указательного и среднего пальцев
            x1, y1 = lmList[8][1:]

            # Проверка поднятых пальцев
            fingers = hands_detector.fingers_up()

            # Если поднят только указательный (режим движения)
            if fingers[1] == 1 and fingers[2] == 0:
                # Преобразование фактических координат в удобную форму
                cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScreen))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScreen))

                # Сглаживание полученных координат
                clocX = plocX + (x3 - plocX) / smooth
                clocY = plocY + (y3 - plocY) / smooth

                # Движение мыши
                autopy.mouse.move(wScreen - clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

                plocX, plocY = clocX, clocY

            # Если поднят указательный и средний палец (режим клика)
            if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
                autopy.mouse.click()

            # Если поднят указательный, средний и безымянный пальцы (режим скролла)
            if fingers[0] == 0 and fingers[1] == 1 and \
                    fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                autopy.mouse.click(autopy.mouse.Button.MIDDLE)
                time.sleep(0.2)

            if fingers[0] == 0 and fingers[1] == 0 and \
                    fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:
                autopy.mouse.click(autopy.mouse.Button.RIGHT)
                time.sleep(0.2)

            # Если поднят указательный палец и мизинец (режим голосового управления)
            if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:
                text = voice_detector.speech_to_text()
                print(text)
                if text == "звук":
                    MOUSE_MODE = False
                    start = time.time()
                elif "найди" in text:
                    text = text.replace('найди', '')
                    text = text.strip()
                    webbrowser.open('https://www.google.com/search?q=' + text)

        # Режим настройки громкости (работает 5 секунд)
        elif time.time() < start + 5:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            length = math.hypot(x2 - x1, y2 - y1)

            vol = np.interp(length, [50, 300], [min_vol, max_vol])
            print(int(length), vol)
            volume.SetMasterVolumeLevel(vol, None)

            if length < 50:
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

        else:
            MOUSE_MODE = True

    # Вывод изображения
    cv2.imshow("img", img)
    cv2.waitKey(1)
