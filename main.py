import math
import os
import random
import sys
import time

import cv2
import keyboard
import mss
import numpy as np
import pygetwindow as gw
import win32api
import win32con

from colorama import Fore, Style, init

AUTOCLICKER_TEXT = """

██████╗░███████╗██╗░░░██╗░█████╗░██████╗░██╗░░░██╗██████╗░████████╗░█████╗░░██████╗░██████╗░
██╔══██╗██╔════╝██║░░░██║██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗╚══██╔══╝██╔══██╗██╔════╝░██╔══██╗
██║░░██║█████╗░░╚██╗░██╔╝██║░░╚═╝██████╔╝░╚████╔╝░██████╔╝░░░██║░░░██║░░██║██║░░██╗░██████╔╝
██║░░██║██╔══╝░░░╚████╔╝░██║░░██╗██╔══██╗░░╚██╔╝░░██╔═══╝░░░░██║░░░██║░░██║██║░░╚██╗██╔══██╗
██████╔╝███████╗░░╚██╔╝░░╚█████╔╝██║░░██║░░░██║░░░██║░░░░░░░░██║░░░╚█████╔╝╚██████╔╝██║░░██║
╚═════╝░╚══════╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░░░░╚═╝░░░░╚════╝░░╚═════╝░╚═╝░░╚═╝
"""

# Инициализация для Windows
init(autoreset=True)

def resource_path(relative_path):
    """ Load images for .exe """
    try:
        base_path = sys._MEIPASS
        return str(os.path.join(base_path, relative_path))
    except Exception:
        return relative_path

class Logger:
    def __init__(self, prefix=None):
        self.prefix = prefix

    def log(self, data: str, color=None):
        if self.prefix == ">>>    Dev | Crypto_GR  <<<   ":
            print(f"{Fore.CYAN}{self.prefix}{Style.RESET_ALL} {data}")
        else:
            color = color if color else ""
            print(f"{color}{self.prefix} {data}")

    def input(self, text: str, color=None):
        if self.prefix == ">>>    Dev | Crypto_GR  <<<   ":
            return input(f"{Fore.CYAN}{self.prefix}{Style.RESET_ALL} {text}")
        else:
            color = color if color else ""
            return input(f"{color}{self.prefix} {text}")

class AutoClicker:
    def __init__(self, window_title, logger, percentages: float, is_continue: bool):
        self.window_title = window_title
        self.logger = logger
        self.running = False
        self.clicked_points = []
        self.iteration_count = 0

        self.percentage_click = percentages
        self.is_continue = is_continue

        # 
        self.targets = {
            "act": {
                "colors": ["#c9e100", "#bae70e"],
                "nearby": ["#abff61", "#87ff27"],
                "chance": self.percentage_click
            }
        }


        for obj_type, data in self.targets.items():
            data["hsv_colors"] = [self.hex_to_hsv(color) for color in data["colors"]]
            data["nearby_hsv"] = [self.hex_to_hsv(color) for color in data["nearby"]]

        self.templates_plays = [
            cv2.cvtColor(cv2.imread(img, cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2GRAY) for img in CLICK_IMAGES
        ]  # click image

    @staticmethod
    def hex_to_hsv(hex_color):
        hex_color = hex_color.lstrip('#')
        h_len = len(hex_color)
        rgb = tuple(int(hex_color[i:i + h_len // 3], 16) for i in range(0, h_len, h_len // 3))
        rgb_normalized = np.array([[rgb]], dtype=np.uint8)
        hsv = cv2.cvtColor(rgb_normalized, cv2.COLOR_RGB2HSV)
        return hsv[0][0]

    @staticmethod
    def click_at(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def toggle_script(self):
        self.running = not self.running
        r_text = "ON" if self.running else "OFF"
        self.logger.log(f'Status: {r_text}')

    def is_near_color(self, hsv_img, center, target_hsvs, radius=8):
        x, y = center
        height, width = hsv_img.shape[:2]
        for i in range(max(0, x - radius), min(width, x + radius + 1)):
            for j in range(max(0, y - radius), min(height, y + radius + 1)):
                distance = math.sqrt((x - i) ** 2 + (y - j) ** 2)
                if distance <= radius:
                    pixel_hsv = hsv_img[j, i]
                    for target_hsv in target_hsvs:
                        if np.allclose(pixel_hsv, target_hsv, atol=[1, 50, 50]):
                            return True
        return False

    def find_and_click_image(self, template_gray, screen, monitor):
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGRA2GRAY)
        result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= 0.6:  
            template_height, template_width = template_gray.shape
            center_x = max_loc[0] + template_width // 2 + monitor["left"]
            center_y = max_loc[1] + template_height // 2 + monitor["top"]
            self.click_at(center_x, center_y)
            return True
        return False

    def click_color_areas(self):
        windows = gw.getWindowsWithTitle("Мини-приложение: Blum")
        if len(windows) < 1:
            self.logger.log(f"Не найдено окон с заголовком: Мини-приложение: Blum")
            all_windows = gw.getAllTitles()
            self.logger.log(f"Все открытые окна: {all_windows}")
            return

        try:
            for window in windows:
                if not window.isActive:
                    window.activate()
                self.logger.log(f"Активировано окно: {window.title}")
        except Exception as e:
            self.logger.log(f"Ошибка при активации окон: {str(e)}")
            return

        self.logger.log("Игра началась")

        with mss.mss() as sct:
            grave_key_code = 41
            keyboard.add_hotkey(grave_key_code, self.toggle_script)

            iteration_delay = 0.2  # Увеличьте интервал между циклами обработки
            max_windows_to_process = 2  # Ограничьте количество окон для обработки за раз

            while True:
                if self.running:
                    # Обрабатываем только ограниченное количество окон за один цикл
                    windows_to_process = windows[:max_windows_to_process]
                    for window in windows_to_process:
                        if not window.isActive:
                            window.activate()

                        monitor = {
                            "top": window.top,
                            "left": window.left,
                            "width": window.width,
                            "height": window.height
                        }
                        img = np.array(sct.grab(monitor))
                        hsv = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGRA2BGR), cv2.COLOR_BGR2HSV)

                        for obj_type, data in self.targets.items():
                            for target_hsv in data["hsv_colors"]:
                                lower_bound = np.array([max(0, target_hsv[0] - 1), 30, 30])
                                upper_bound = np.array([min(179, target_hsv[0] + 1), 255, 255])
                                mask = cv2.inRange(hsv, lower_bound, upper_bound)
                                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                                for contour in contours:
                                    if random.random() >= data["chance"]:
                                        continue

                                    if cv2.contourArea(contour) < 8:
                                        continue

                                    M = cv2.moments(contour)
                                    if M["m00"] == 0:
                                        continue
                                    cX = int(M["m10"] / M["m00"]) + monitor["left"]
                                    cY = int(M["m01"] / M["m00"]) + monitor["top"]

                                    if not self.is_near_color(hsv, (cX - monitor["left"], cY - monitor["top"]), data["nearby_hsv"]):
                                        continue

                                    if any(math.sqrt((cX - px) ** 2 + (cY - py) ** 2) < 35 for px, py in self.clicked_points):
                                        continue
                                    cY += 7
                                    self.click_at(cX, cY)
                                    self.clicked_points.append((cX, cY))

                        time.sleep(0.29)
                        self.iteration_count += 1
                        if self.iteration_count >= 5:
                            self.clicked_points.clear()
                            if self.is_continue:
                                for tp in self.templates_plays:
                                    self.find_and_click_image(tp, img, monitor)
                            self.iteration_count = 0

                    time.sleep(iteration_delay)  # Увеличенный интервал между обработкой окон
        self.logger.log("Игра завершена")  # Уведомление о завершении игры


if __name__ == "__main__":
    logger = Logger(">>>    Dev | Crypto_GR  <<<   ")
    logger.log(AUTOCLICKER_TEXT)
    logger.log("Ежедневное использование FarmBot для TinyVerse - эффективно улучшает галактику: https://t.me/farm_cryptogr_bot")
    
    CLICK_IMAGES = [resource_path("media\\lobby-play.png"), resource_path("media\\continue-play.png")]

    PERCENTAGES = {
        "1": 0.1,
        "2": 0.14,
        "3": 0.2,
        "4": 1,
    }

    answer = None
    while answer is None:
        points_key = logger.input("Сколько очков хотите добыть? | 1 -> Простая разминка | 2 -> Серьезный вызов | 3 -> Почти на вершине | 4 -> Максимум очков! ")
        answer = PERCENTAGES.get(points_key, None)
        if answer is None:
            logger.log("Неверное значение", color=Fore.RED)
    percentages = answer

    answer = None
    answs = {
        "1": True,
        "0": False
    }
    while answer is None:
        points_key = logger.input("Активировать автоматический запуск игры? | 1 - Да / 0 - Нет: ")
        answer = answs.get(points_key, None)
        if answer is None:
            logger.log("Неверное значение", color=Fore.RED)
    is_continue = answer

    logger.log('Перед началом игры нажмите клавишу "ё" (`) на клавиатуре, чтобы активировать режим автокликера.', color=Fore.YELLOW)

    auto_clicker = AutoClicker("Мини-приложение: Blum", logger, percentages=percentages, is_continue=is_continue)

    try:
        auto_clicker.click_color_areas()
    except Exception as e:
        logger.log(f"Произошла ошибка: {e}", color=Fore.RED)
    
    for i in reversed(range(5)):
        i += 1
        print(f"Скрипт завершит работу через {i}")
        time.sleep(1)
