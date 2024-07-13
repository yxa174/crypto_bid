from collections import deque
import time
import random

def get_price():
    # Здесь должна быть функция для получения текущей цены
    # В данном примере она генерирует случайное значение
    return random.uniform(90, 110)

def check_price_jump(prices, threshold=10):
    if len(prices) < 5:
        return False, 0
    min_price = min(prices)
    max_price = max(prices)
    percent_jump = ((max_price - min_price) / min_price) * 100
    return percent_jump > threshold, percent_jump

prices = deque(maxlen=5)

while True:
    current_price = get_price()
    prices.append(current_price)
    print(f"Текущая цена: {current_price}")
    
    if len(prices) == 5:
        jump_detected, percent_jump = check_price_jump(prices)
        if jump_detected:
            print(f"Обнаружен высокий скачок цены: {percent_jump:.2f}%")
        prices.clear()  # Удаление данных последних 5 сохранений
    
    time.sleep(1)  # Ожидание 1 минуты перед следующей проверкой

