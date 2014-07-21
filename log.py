from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.cors import cross_origin

import json

app = Flask(__name__, static_url_path='')
app.config.from_object('config')
db = SQLAlchemy(app)


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column('id', db.Integer, primary_key=True)
    sujeto = db.Column(db.String(60))
    log = db.Column(db.String)

    def __init__(self, sujeto, log):
        self.sujeto = sujeto
        self.log = log

admin = Admin(app)
admin.add_view(ModelView(Log, db.session))


@app.route('/')
@cross_origin()
def default():
    return ""


@app.route('/create_log', methods=['POST'])
@cross_origin()
def create_log():
    if not request.json:
        return "error not json", 400
    sujeto = request.json['sujeto'] or 'nn'
    sujeto_log = json.dumps(request.json['log']) or ''
    log = Log(sujeto, sujeto_log)
    db.session.add(log)
    db.session.commit()
    return str(log.id), 201


@app.route('/append_log', methods=['POST'])
@cross_origin()
def append_log():
    if not request.json or not 'id' in request.json \
            or not 'log' in request.json:
        return "error, missing parameter (id, log) or not json", 400
    log = Log.query.get(request.json['id'])
    new_log = json.loads(log.log) or ''
    new_log.append(json.loads(request.json[log]))
    log.log = new_log
    db.session.commit()
    return "ok", 200

if __name__ == '__main__':
    app.debug = True
    app.trap_http_exceptions = True
    app.run()
