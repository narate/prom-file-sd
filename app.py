from flask import Flask, request
from flask_restful import Resource, Api
from jsonschema import validate
from pymongo import MongoClient
from bson.objectid import ObjectId
import json, os

MONGO_HOST = os.environ.get('MONGO_HOST', 'db')
MONGO_PORT = os.environ.get('MONGO_PORT', 27017)

app = Flask(__name__)
api = Api(app)

schema = {
     "type" : "object",
     "properties" : {
         "target" : {"type" : "string"},
         "labels" : {"type" : "object"}
     },
     "required": ["target"]
}

delete_schema = {
     "type" : "object",
     "properties" : {
         "id" : {"type" : "string"},
     },
     "required": ["id"]
}

class IndexPage(Resource):
    def get(self):
        return { "message": "Need Web UI, Please add UI support https://github.com/narate/prom-file-sd"}

class PromTargets(Resource):
    def get(self):
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.prom
        col = db.targets
        targets = []
        for o in col.find():
            targets.append({'target': o['target'], 'labels': o.get('labels',{}), 'id': str(o['_id'])})
        return { 'targets': targets }
    
    def post(self):
        body = request.get_json()
        try:
            validate(body, schema)
        except:
            return {
                    'message': 'Input data invalid or miss some value, required: {}'.format(schema['required'])
                }, 400
        
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.prom
        col = db.targets
        labels = body.get('labels', {})
        doc = {
            'target': body['target'],
            'labels': labels
        }
        
        sel = {
            'target': body['target']
        }
        metrics_path = labels.get('__metrics_path__')
        if metrics_path is not None:
            sel['labels.__metrics_path__'] = metrics_path
        else:
            doc['labels']['__metrics_path__'] = '/metrics'
        
        col.replace_one(sel, doc, True)
        with open('/prom/conf/targets.json', 'w') as f:
            targets = []
            for o in col.find({}, projection={'_id': False}):
                targets.append(
                    {
                        'targets': [o['target']],
                        'labels': o.get('labels',{})
                    }
                )
    
            f.write(json.dumps(targets, indent=2))
            f.flush()
            os.fsync(f.fileno())
        return {
            'status': 'created',
            'data': doc
        }, 201

    def delete(self):
        body = request.get_json()
        try:
            validate(body, delete_schema)
        except:
            return {
                    'message': 'Input data invalid or miss some value, required: {}'.format(schema['required'])
                }, 400
        
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.prom
        col = db.targets
        sel = {
            '_id': ObjectId(body['id'])
        }
        col.delete_one(sel)
        with open('/prom/conf/targets.json', 'w') as f:
            targets = []
            for o in col.find({}, projection={'_id': False}):
                targets.append(
                    {
                        'targets': [o['target']],
                        'labels': o.get('labels',{})
                    }
                )
    
            f.write(json.dumps(targets, indent=2))
            f.flush()
            os.fsync(f.fileno())
        return None, 204

api.add_resource(IndexPage, '/')
api.add_resource(PromTargets, '/targets')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
