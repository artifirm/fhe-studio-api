# save this as app.py
from flask import Flask, request
from fhe_compile import fhe_compile
from fhe_client import client_key_gen, encrypt, decrypt
from fhe_server import fhe_server_compute
import json

from mongo_context import find_circuit, find_circuits,vault, delete_circuit, client_specs, delete_vault_item

app = Flask(__name__)

@app.route('/api/edit-circuit/', methods=['PUT'], defaults={'id': None})
@app.route('/api/edit-circuit/<id>', methods=['PUT'])
def edit_circuit(id):
    form = json.loads(request.data)
    usrData = {
        "sub": request.headers["sub"],
        "email": request.headers["email"],
        "src": form['src'],
        "name": form['name'],
        "description": form['description']
        }
    print(f'edit-circuit id: {id} , {usrData}')
    result = fhe_compile(id, usrData)
    if result is None:
        return {}
    
    return {'exception': result}

@app.route('/api/delete-circuit/<id>', methods=['DELETE'])
def api_edit_circuit(id):
    return delete_circuit(id, request.headers["sub"])


@app.route('/api/fhe-eval/<eval_key_id>', methods=['POST'])
def fhe_eval(eval_key_id):
    form = json.loads(request.data)
    return fhe_server_compute(eval_key_id, form['values'])


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

@app.route('/api/add-vault/<id>', methods=['PUT'])
def add_vault_api(id):
    client_key_gen(id, request.headers["sub"])
    return "{}"

@app.route('/api/vault', methods=['POST'])
def vault_api():
    c = vault()
    records = []
    for x in c:
        records.append ({
            'id' : str(x['_id']), 
            'circuit_id':str(x['circuit']['_id']),
            'name': x['circuit']['name'],
            'email': x['circuit']['email'],
            'created_time': x.get('created_time', None)
        })
    return records

@app.route('/api/vault/encrypt/<id>', methods=['POST'])
def vault_encrypt_api(id):
    form = json.loads(request.data)
    return encrypt(id, form['values'])

@app.route('/api/vault/decrypt/<id>', methods=['POST'])
def vault_decrypt_api(id):
    form = json.loads(request.data)
    return [ decrypt(id, form['values']) ]

@app.route('/api/vault/client-specs/<id>', methods=['POST'])
def client_specs_api(id):
    return client_specs(id)


@app.route('/api/delete-vault-item/<id>', methods=['DELETE'])
def api_delete_vault_item(id):
    return delete_vault_item(id, request.headers["sub"])



@app.route('/dev-token', methods=['POST'])
def dev_token():
    return {'access_token':'dev-access-token'}

@app.route('/dev-user')
def dev_user():
    return {
        'email': 'dev-user@example.com',
        'sub': 'dev-id',
        'picture': None,
        'email_verified': True}