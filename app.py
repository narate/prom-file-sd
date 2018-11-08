from flask import Flask
from flask_restful import Resource, Api, reqparse
from jsonschema import validate
import json, os
from pymongo import MongoClient

MONGO_HOST = 'db'

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('target')
parser.add_argument('job')
parser.add_argument('env')

new_schema = {
     "type" : "object",
     "properties" : {
         "target" : {"type" : "string"},
         "env" : {"type" : "string"},
         "job": {"type" : "string"}
     },
     "required": ["target", "env", "job"]
}

delete_schema = {
     "type" : "object",
     "properties" : {
         "target" : {"type" : "string"}
     },
     "required": ["target"]
}

class IndexPage(Resource):
    def get(self):
        return { "message": "Need Web UI, Please add UI support https://github.com/narate/prom-file-sd"}

class PromTargets(Resource):
    def get(self):
        client = MongoClient(MONGO_HOST, 27017)
        db = client.prom
        col = db.targets
        targets = []
        for o in col.find():
            targets.append({'target': o['target'], 'env': o['env'], 'job': o['job']})
        return { 'targets': targets }
    
    def post(self):
        args = parser.parse_args()
        try:
            validate(args, new_schema)
        except:
            return {
                    'message': 'Input data invalid or miss some value, required: {}'.format(new_schema['required'])
                }, 400
        
        client = MongoClient(MONGO_HOST, 27017)
        db = client.prom
        col = db.targets
        doc = {
            'target': args['target'],
            'job': args['job'],
            'env': args['env']
        }

        col.replace_one({ 'target': args['target']}, doc, True)
        with open('/prom/conf/targets.json', 'w') as f:
            targets = []
            jobs = col.distinct('job')
            envs = col.distinct('env')
            for j in jobs:
                for e in envs:
                    labels = {'job': j, 'env': e }
                    target = []
                    for o in col.find(labels,{'target':1}):
                        target.append(o['target'])
                    if len(target)> 0:
                        targets.append({'targets': target, 'labels':labels})
        
            f.write(json.dumps(targets, indent=2))
            f.flush()
            os.fsync(f.fileno())
        return {
            'status': 'created',
            'data': args
        }, 201


api.add_resource(IndexPage, '/')
api.add_resource(PromTargets, '/targets')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")