import datetime
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


FILE_NAME = os.path.join(os.path.abspath(os.curdir), "app", "app.html")

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)


def logIntoAccount(login: str):
    driver.get(FILE_NAME)
    loginInputElement: WebElement = driver.find_element(By.ID, "login_box")
    loginInputElement.send_keys(login)
    loginButton: WebElement = driver.find_element(By.ID, "login_button")
    loginButton.click()
    time.sleep(2)


def testWithHistoryLogin():
    logIntoAccount("test1")
    questionElements = driver.find_elements(
        By.CLASS_NAME,
        "user-question"
    )
    questionTexts = [element.find_element(By.TAG_NAME, "span").get_attribute("innerText")
                     for element in questionElements]
    assert any(element == "Я грустен" for element in questionTexts)


def testWithoutHistoryLogin():
    logIntoAccount("test2")
    questionElements = driver.find_elements(
        By.CLASS_NAME,
        "user-question"
    )
    assert len(questionElements) == 0


def testAddingToFavourites():
    logIntoAccount("test1")
    favouriteAnswers = driver.find_elements(By.CLASS_NAME, "favorite")
    assert len(favouriteAnswers) == 0
    elementToLike = driver.find_elements(By.CLASS_NAME, "jason-answer")[0]
    likedIdentificator = elementToLike.get_property("id")
    elementToLike.find_element(By.TAG_NAME, "button").click()
    logIntoAccount("test1")
    favouriteAnswers = driver.find_elements(By.CLASS_NAME, "favorite")
    assert len(favouriteAnswers) == 1
    assert favouriteAnswers[0].get_property("id") == likedIdentificator
    favouriteAnswers[0].find_element(By.TAG_NAME, "button").click()
    logIntoAccount("test1")
    favouriteAnswers = driver.find_elements(By.CLASS_NAME, "favorite")
    assert len(favouriteAnswers) == 0

def testAskQuestion():
    accountName = "test" + str(
        int(
            time.mktime(
                datetime.datetime.now().timetuple()
            )
        )
    )
    logIntoAccount(accountName)
    questionField = driver.find_element(By.ID, "question_box")
    questionField.send_keys("Быть или не быть?")
    driver.find_element(By.ID, "ask_question_button").click()
    time.sleep(5)
    logIntoAccount(accountName)
    messages = driver.find_elements(By.CLASS_NAME, "message")
    assert len(messages) == 2
    assert any(
        message.find_element(By.TAG_NAME, "span").get_attribute("innerText") == "Быть или не быть?"
        for message in messages
    )
