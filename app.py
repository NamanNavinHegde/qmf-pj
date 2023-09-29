#!/usr/bin/python3.6

from flask import Flask, render_template
import test
from config import Config
from model import db
from model import Todo


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/service')
def service():
    return render_template('service.html')


@app.route('/favaver', methods=['POST', 'GET'])
def favaver():
    test.loadfavaver()
    tasks_qmf = Todo.query.filter(Todo.stack.like('%qmf%'))
    tasks_qmn = Todo.query.filter(Todo.stack.like('%qmn%'))
    tasks_qmnj = Todo.query.filter(Todo.stack.like('%qmnj%'))
    tasks_qcg = Todo.query.filter(Todo.stack.like('%qcg%'))
    return render_template('favaver.html', tasks_qmf=tasks_qmf,
                           tasks_qmn=tasks_qmn, tasks_qmnj=tasks_qmnj,
                           tasks_qcg=tasks_qcg)


@app.route('/fengine/<string:stack>')
def fengine(stack):
    str = 'https://{0}.fava.fb.com/{1}/fava_engine'.format(stack[:3], stack)    
    print(str)
    task = test.favaEngine(str)
    return render_template('fengine.html', stack=stack.capitalize(), task=task)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, ssl_context='adhoc')
    
    
