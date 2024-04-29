from app.api import *
import os
import datetime


pytest_plugins = ('pytest_asyncio',)


def test_check_time(event_loop):
    """
    Функция отправляет 5 запросов, иммитирующие обращения пользователей к психологу Джейсону. Ожидаемое среднее время
    ответа для 5 пользователей не должно превышать 15 секунд
    """
    # ождаемое время выполнения запросов
    expected_time = datetime.timedelta(seconds=15)
    # Вопросы пользователей
    questions = [
        'Мне плохо',
        'Я не сдал экзамен',
        'Меня бросил парень',
        'Со мной развелась жена',
        'У меня провал на работе'
    ]

    # текст окружения для YandexGPT
    prompt_file = os.path.join(os.path.abspath(os.curdir), "app", "prompt.txt")
    prompt = read_text_from_prompt_file(prompt_file)
    

    start_time = datetime.datetime.now()

    for request in questions:
        
       event_loop.run_until_complete(
            
            send_prompt(prompt, request)
            
        )
        
        

    finish_time = datetime.datetime.now()

    average_time = (finish_time - start_time) / 5
    
    assert average_time < expected_time
