

const MessageType = {
    QUESTION: "question",
    ANSWER: "answer"
}

let buttonActive = true;
let API_URL = "http://127.0.0.1:8000/"

async function sendMessage(){
    // console.log("I am sending request:");
    if (!buttonActive) return;
    buttonActive = false;
    let login = document.getElementById("login_box").value;
    let question = document.getElementById("question_box").value;
    let request = new XMLHttpRequest();
    await addMessage(question, null, MessageType.QUESTION);
    request.open(
        "POST",
        API_URL + "ask/" + login,
    )

    request.onload = async () => {
        let responseJson = JSON.parse(request.responseText);
        //console.log(responseJson);
        let id = responseJson['id'];
        let answerText = responseJson['response'];
        await addMessage(answerText, id, MessageType.ANSWER);
        let messagesList = document.getElementById("messagesList");
        let answerElement = messagesList.children[messagesList.children.length - 1];
        let questionElement = messagesList.children[messagesList.children.length - 2];
        answerElement.setAttribute("id", "answer_" + id);
        questionElement.setAttribute("id", "question_" + id);
        buttonActive = true;
    }
    let dataToSend = JSON.stringify(
            {
                "text": question
            }
        );
    //console.log(dataToSend);
    request.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
    request.send(
        dataToSend
    );

}


async function likeMessage(message){
    let login = document.getElementById("login_box").value;
    let request = new XMLHttpRequest();
    request.open(
        "GET",
        API_URL + "like/"+login+"/"+message.id
    );
    request.send();
}



async function loadMessages(){
    //console.log("trying to get messages")
    let login = document.getElementById("login_box").value;
    let request = new XMLHttpRequest();
    request.open(
        "GET",
        API_URL + "messages/" + login,
    )
    request.onload = async () => {
        if (request.status === 200){
            let messagesJson = JSON.parse(request.responseText);
            // console.log(messagesJson);
            await displayMessages(messagesJson);
        }
    }
    request.send();
}

//____________________________________ ОТРИСОВКА _________________________________

class Message {
    constructor(text, id, type, isFavourite=false) {
        this.text = text;
        this.id = id;
        this.type = type;
        this.isFavorite = isFavourite; // По умолчанию сообщение не избранное (НО МОЖНО ЖЕ ПРИНИМАТЬ ЭТО КАК ПАРАМЕТР !!!)
        this.buttonText = 'Like    '; // Текст кнопки по умолчанию

        this.__DOM_ELEMENT__ = null;
    }

    createHTML() {
        const li = document.createElement('li');
        li.classList.add('message'); // Добавляем класс для стилизации
        li.id = `${this.type}_${this.id}`;
        li.classList.add(this.type === 'question' ? 'user-question' : 'jason-answer');
        li.classList.add(this.type === 'question' ? 'question-background' : 'answer-background');

        // Добавляем текст сообщения
        const messageText = document.createElement('span');
        messageText.innerText = this.text;
        li.appendChild(messageText);

        // Добавляем кнопку
        if (this.type === 'answer') {
            const button = document.createElement('button');
            button.innerText = this.buttonText;

            // Создаем SVG-иконку
            const icon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            icon.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
            icon.setAttribute('width', '16');
            icon.setAttribute('height', '16');
            icon.setAttribute('fill', 'red');
            icon.setAttribute('class', 'bi bi-chat-heart-fill');
            icon.setAttribute('viewBox', '0 0 16 16');
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', 'M8 15c4.418 0 8-3.134 8-7s-3.582-7-8-7-8 3.134-8 7c0 1.76.743 3.37 1.97 4.6-.097 1.016-.417 2.13-.771 2.966-.079.186.074.394.273.362 2.256-.37 3.597-.938 4.18-1.234A9 9 0 0 0 8 15m0-9.007c1.664-1.711 5.825 1.283 0 5.132-5.825-3.85-1.664-6.843 0-5.132');
            icon.appendChild(path);
            button.appendChild(icon);

            // Добавляем обработчик события клика по кнопке
            button.addEventListener('click', () => {
                this.toggleBackground(li); // Вызываем метод для изменения фона
                this.toggleFavorite(); // Вызываем метод для изменения состояния избранного
                likeMessage(this);
            });
            li.appendChild(button);
        }
        if (this.isFavorite) this.toggleBackground(li);
        return li;
    }

    // Метод для переключения состояния избранного
    toggleFavorite() {
        this.isFavorite = !this.isFavorite;
    }

    // Метод для изменения фона сообщения
    toggleBackground(element) {
        element.classList.toggle('favorite'); // Добавляем или удаляем класс для изменения фона
    }
}


// CSS стиль для избранных сообщений

async function displayMessages(messagesJson) {
    const messagesList = document.getElementById("messagesList");
    messagesList.innerHTML = "";

    for (const messageContent of messagesJson['content']) {
        const questionMessage = new Message(messageContent['question'], messageContent['id'], MessageType.QUESTION);
        const answerMessage = new Message(messageContent['answer'],
            messageContent['id'], MessageType.ANSWER,
            messageContent['favourite']);

        messagesList.appendChild(questionMessage.createHTML());
        messagesList.appendChild(answerMessage.createHTML());
    }
}

async function addMessage(messageText, id, type="question") {
    const messagesList = document.getElementById("messagesList");
    const newMessage = new Message(messageText, id, type);
    messagesList.appendChild(newMessage.createHTML());
}

