#!/usr/bin/env python


import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

import config #./conig.py, contains path, url and url_breakpoint
# Don't really want to publish direct url to site that I have scrapped

variants = {
    'А':'a',
    'Б':'b',
    'В':'c',
    'Г':'d',
    'Д':'e'
    }

def parse(source):
    '''
    Arg: source - html source of web page of the specific website
    Returns: dictionary of question data got from this page
             or None, if page doesn't contain 
    '''
    soup = BeautifulSoup(source, 'lxml')
    task = soup.findAll('div', class_='task-card current checks')[-1]

    #filter some uncommon types of questions
    task_text = task.find('div', class_='q-info')
    if task_text is None or task_text.text!= u'Позначте відповіді:':
        return;

    table = task.findAll('tr') #panel with selected answer
    # filter questions with only one answer
    if len(table) != 2: return;

    data = dict()

    question = task.find('div', class_='question')
    data['question'] = question.text

    answers = task.findAll('div', class_='answer')
    for answer in answers:    ## TODO rewrite as a dict comprehension
        #0 char is a variant letter
        data[variants[answer.text[0]]] = answer.text[1:]

    #WARNING! hard code
    radio = table[1].findAll('label')
    for button in radio:
        if button.find('span', class_='marker ok') is not None:
            data['correct'] = button.find('input')['value']
            break;    
    return data
    

def web_scrape():
    df = pd.DataFrame(columns=['question','a','b','c','d','e','correct'])
    
    # Selenium is the most simple way I found to "click" button before getting page source
    # If you know another way to call JS function checkResult() on the page before parsing
    # - let me know
    driver = webdriver.Chrome(config.path)
    driver.get(config.url)
    
    while driver.current_url != config.url_breakpoint:
        task = driver.find_elements(By.CLASS_NAME, 'task-card.current')[-1]
        button = task.find_element(By.CLASS_NAME, 'q-btn.button-green.q-check')
    
        # scroll is used to avoid overlapping buttons with bottom ad
        driver.execute_script("window.scrollTo(0, %d)"%(button.location['y']+50) ) 
        button.click()
    
        data = parse(driver.page_source)
        df = df.append(data, ignore_index=True)
        
        try: #to the next question
            button_next = task.find_element(By.CLASS_NAME, 'q-btn.button-gray.q-next')
            button_next.click()
        except: #to the next block of question
            button_next = task.find_element(By.CLASS_NAME, 'q-btn.button-red.q-final')
            button_next.click()
            driver.get(driver.current_url) #wait until loaded
    
    driver.quit()
    df.to_csv("data/ukrainian_questions_dataset.csv")


if __name__ == '__main__':
    web_scrape()

