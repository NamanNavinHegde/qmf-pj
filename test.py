#!/usr/bin/python3.6
import requests
import urllib3
from mycredentials import sys_qmf, sys_qmn, sys_qmnj
from requests import Session
from flask import Flask
from config import Config
from model import db
from model import Todo
from bs4 import BeautifulSoup


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
with app.app_context():
    db.create_all()


def getFAVAversion(list) -> list:
    url = '{0}/{1}'.format(list[1], 'about')
    try:        
        r = requests.get(url, verify=False, timeout=10)
        # Parsing the HTML code
        soup = BeautifulSoup(r.content, 'lxml')
        s = soup.find('div', attrs={'class': 'container'})
        table = s.find_all('table')
        trs = table[0].findAll('tr')
        for idx, tr in enumerate(trs):
            if (idx == 1):
                td = tr.findAll('td')
                return [list[0], td[1].text.strip()]
    except :
        return [list[0], '']

'''
def getassettag(str, list) -> list:
    payload = {'username': '', 'password': ''}
    stack = ''
    match str:
        case 'qmf':
            payload['username'] = sys_qmf.username
            payload['password'] = sys_qmf.password
        case 'qmn':
            payload['username'] = sys_qmn.username
            payload['password'] = sys_qmn.password
        case 'qmnj':
            payload['username'] = sys_qmnj.username
            payload['password'] = sys_qmnj.password
        case _:
            return [list[0], 'Not Support']
    with Session() as s:
        # TODO: Explain this.
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        loginURL = '{0}/{1}'.format(list[1], 'login')
        loginResponse = s.get(loginURL, verify=False, timeout=10)
        soup = BeautifulSoup(loginResponse.text, 'lxml')
        csrfToken = soup.find('input', {'id': 'csrf_token'})['value']
        payload['csrf_token'] = csrfToken       
        ask = s.post(loginURL, data=payload, verify=False)
        url = '{0}/{1}'.format(list[1], 'scanin')
        r = s.get(url, verify=False, timeout=10)
        # Parsing the HTML code
        soup = BeautifulSoup(r.content, 'lxml')
        s = soup.find('select', attrs={'id': 'rack'})        
        select = s.find_all('option')
        for sel in select:
            td = sel.text.strip()
            stack += '{0}, '.format(td)
    return [list[0], stack]
    
'''

def loaderror(list):
    url = '{0}'.format(list[1])
    try:        
        r = requests.get(url, verify=False, timeout=10)
        # Parsing the HTML code
        soup = BeautifulSoup(r.content, 'lxml')
        s = soup.find('div', attrs={'class': 'container'})
        print(s)
        table = s.find_all('table')        
        trs = table[0].findAll('tr')
        for idx, tr in enumerate(trs):
            if (idx == 1):
                td = tr.findAll('td')
                return [list[0], td[1].text.strip()]
    except :
        return [list[0], '']



def loaddef() -> list:
    url_adds = []
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url_adds.append('https://qmf.fava.fb.com/')
    url_adds.append('https://qcg.fava.fb.com/')
    url_adds.append('https://qmn.fava.fb.com/')
    url_adds.append('https://qmnj.fava.fb.com/')
    # Making a GET request
    rows = []
    for idx, url in enumerate(url_adds):
        try:        
            r = requests.get(url, verify=False, timeout=10)
            # Parsing the HTML code
            soup = BeautifulSoup(r.content, 'lxml')
            if (idx == 0):
                s = soup.find('ul', attrs={'class': 'dropdown-menu'})
                for line in s.find_all('li'):
                    rows.append([line.text.strip(), '{0}{1}'
                                .format(url, line.text.strip())])
            else:
                s = soup.find('div', attrs={'class': 'container'})
                for line in s.find_all('table'):
                    td = line.findAll('td')
                    for i in td: 
                        rows.append([i.text.strip(),
                                    '{0}{1}'.format(url, i.text.strip())])
        except:
            rows.append(['', ''])
    return rows


def loadfavaver():
    with open('tmp/favaver.txt') as f:
        for line in f.readlines():
            row = line.strip().split('|')
            ver = row[1].strip().split('-')
            newRow = Todo(stack=row[0].strip(), version=ver[0])
            update_Row = Todo.query.filter(
                Todo.stack == '{0}'.format(row[0].strip())).first()
            if (update_Row):
                if (len(row[1]) > 0):
                    update_Row.version = ver[0]
                db.session.add(update_Row)
            else:
                db.session.add(newRow)
            db.session.commit()


def writetxt():
    rows = loaddef()
    open('tmp/favaver.txt', 'w').close()
    with open('tmp/favaver.txt', 'w') as f:
        for i in rows:
            row = (getFAVAversion(i))
            f.writelines('{0} |{1} \n'.format(row[0], row[1]))


def favaEngine(str) -> str:
    try:        
        r = requests.get(str, verify=False, timeout=10)
        # Parsing the HTML code
        soup = BeautifulSoup(r.content, 'lxml')
        s = soup.find('div', attrs={'class': 'container'})
        txt = s.find('pre')
        return txt.text.strip()
    except :
        return ['Stack Has No Connection']


def loadassetag():
    #rows = loaddef()
    row = ['qmn17', 'https://qmn.fava.fb.com/qmn17']
    #print(getassettag('qmn', row))

