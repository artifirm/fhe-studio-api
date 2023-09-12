# save this as app.py
from flask import Flask, request
from fhe_compile import fhe_compile
from fhe_client import client_key_gen
from fhe_server import fhe_server_compute
import json

from mongo_context import find_circuit, find_circuits, vault

app = Flask(__name__)


@app.route('/api/edit-circuit/<id>', methods=['POST'])
def edit_circuit(id):
    form = json.loads(request.data)
    usrData = {
        "sub": request.headers["sub"],
        "email": request.headers["email"],
        "src": form['src'],
        "name": form['name'],
        "description": form['description']
        }
    print(f'edit-circuit id: {id} , usrData')
    return fhe_compile(id, usrData)

@app.route('/key-gen/<circuit_id>', methods=['POST'])
def key_gen(circuit_id):
    print(circuit_id)
    client_key_gen(circuit_id)
    return "OK"

@app.route('/fhe-eval/<eval_id>', methods=['POST'])
def fhe_eval(eval_id):
    print(eval_id)
    fhe_server_compute(eval_id)
    return "OK"


@app.route('/api/circuits', methods=['GET'])
def circuits():
    c = find_circuits()
    records = []
    for x in c:
        print(x)
        records.append ({
            'id' : str(x['_id']), 
            'name' : x.get('name', None),
            'email' : x.get('email', None),
            'description' : x.get('description', None),
            'created_time': x.get('created_time', None),
        })
    return records

@app.route('/api/circuit/<circuit_id>', methods=['POST'])
def circuit(circuit_id):
    c = find_circuit(circuit_id)
    return { "name": c['name'], "src": c['src'], "description": c['description']}

@app.route('/api/vault', methods=['POST'])
def circuit(circuit_id):
    c = vault()
    records = []
    for x in c:
        records.append ({
            'id' : str(x['_id']), 
        })
    return records