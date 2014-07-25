from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.cors import cross_origin
from marshmallow import Serializer


import json

app = Flask(__name__, static_url_path='')
app.config.from_object('config')
db = SQLAlchemy(app)


class Experiment(db.Model):
    __tablename__ = 'experiment'
    id = db.Column('id', db.Integer, primary_key=True)
    test_subject = db.Column(db.String(60))
    experiment_log = db.Column(db.String)
    experiment_name = db.Column(db.String)

    # def __init__(self, test_subject, experiment_log, experiment_name):
    #     self.test_subject = test_subject
    #     self.experiment_log = experiment_log
    #     self.experiment_name = experiment_name


class ExperimentSerializer(Serializer):
    class Meta:
        fields = ('id', 'test_subject', 'experiment_log', "experiment_name")

admin = Admin(app)
admin.add_view(ModelView(Experiment, db.session))


@app.route('/')
def default():
    return ""


@app.route('/create_log', methods=['POST'])
@cross_origin()
def create_log():
    if not request.json:
        return "error not json", 400
    test_subject = request.json['test_subject'] or 'nn'
    experiment_log = json.dumps(request.json['experiment_log']) or ''
    experiment_name = json.dumps(request.json['experiment_name']) or ''
    experiment = Experiment(test_subject, experiment_log, experiment_name)
    db.session.add(experiment)
    db.session.commit()
    return str(experiment.id), 201


@app.route('/get_experiment/<experiment>', methods=['GET'])
@cross_origin()
def get_experiment(experiment):
    experiments = db.session.query(Experiment)\
        .filter(Experiment.experiment_name == experiment)
    return jsonify({"experiments":
                    ExperimentSerializer(experiments, many=True).data}), 200


@app.route('/get_log/<int:id>', methods=['GET'])
@cross_origin()
def get_log(id):
    experiment = Experiment.query.get(id)
    return jsonify({"experiments": ExperimentSerializer(experiment).data}), 200


@app.route('/append_log', methods=['POST'])
@cross_origin()
def append_log():
    if not request.json or not 'id' in request.json \
            or not 'log' in request.json:
        return "error, missing parameter (id, log) or not json", 400
    experiment = Experiment.query.get(request.json['id'])
    new_log = json.loads(experiment.log) or ''
    new_log.append(json.loads(request.json['log']))
    experiment.experiment_log = new_log
    db.session.commit()
    return "ok", 200

if __name__ == '__main__':
    app.debug = True
    app.trap_http_exceptions = True
    app.run()
