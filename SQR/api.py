import traceback

from fastapi import FastAPI
import typing
import sqlite3
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()
connection = sqlite3.connect('messages.db')

origins = [
    "127.0.0.1"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Можно протестировать, что если файл с промптом пустой
def read_text_from_prompt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def delete_spec_symbols(question: str):
    """
    Функция для очистки вопроса пользователя от специальных символов, которые могут сломать sql запрос к дб
    """
    special_symbols = ['"', "'"]
    for symbol in special_symbols:
        question = question.replace(symbol,"")
    return question

# Здесь можно тестить успешное получение ответа от сервера (код 200), а также рассмотреть дугие кейсы (404, 403)
async def send_prompt(user_question: str, prompt: str):
    id_key = "b1gum2orksfbmak13ar5"
    key = "AQVN0ypGVYUSvIFBATSkTgxxr6FczAWm5er78dc7"
    prompt = {
        "modelUri": f"gpt://{id_key}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "1000"
        },
        "messages": [
            {
                "role": "system",
                "text": prompt
            },
            {
                "role": "user",
                "text": user_question
            },
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {key}"
    }

    response = requests.post(url, headers=headers, json=prompt)
    result = response.json()["result"]["alternatives"][0]["message"]["text"]
    return result
class QuestionModel(BaseModel):
    text: str


@app.get("/messages/{loginValue}")
async def transmit_messages(loginValue: str):
    cursor = connection.cursor()
    cursor.execute(
        f'SELECT * FROM messages WHERE login=\"{loginValue}\"'
    )
    return {"content":
        [
            {"id": element[0],
             "login": element[1],
             "question": element[2],
             "answer": element[3],
             "favourite": element[4]}
            for element in cursor.fetchall()
        ]
    }


@app.post("/ask/{login}")
async def ask_question_API(login: str, question: QuestionModel):
    text_prompt = read_text_from_prompt_file("prompt.txt")
    user_question = delete_spec_symbols(question.text)
    response = await send_prompt(user_question, text_prompt)
    cursor = connection.cursor()
    cursor.execute(
        f'INSERT INTO MESSAGES (login, question, answer, favourite) VALUES  (\"{login}\", \"{user_question}\", \"{response}\", 0)'
    )
    connection.commit()
    cursor.execute(
        f"SELECT * FROM MESSAGES WHERE login=\"{login}\""
    )
    _id = cursor.fetchall()[-1][0]
    return {"id": _id, "response": response}


@app.get("/favourites/{login}")
async def getFavouriteMessages(login: str):
    cursor = connection.cursor()
    cursor.execute(
        f"select * from messages where login={login} and favourite=1"
    )
    return {"content":
        [
            {"id": element[0],
             "login": element[1],
             "question": element[2],
             "answer": element[3],
             "favourite": element[4]}
            for element in cursor.fetchall()
        ]
    }


@app.get('/like/{login}/{message_id}')
async def likeMessage(login: str, message_id: int):
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE messages SET favourite=1 - favourite WHERE id = {message_id}"
        )
        connection.commit()
        return 200
    except Exception as e:
        print(traceback.format_exc())
        return 500
