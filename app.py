# save this as app.py
from flask import Flask, request, send_from_directory
from fhe_compile import fhe_compile, fhe_play
from fhe_client import client_key_gen, encrypt, decrypt
from fhe_server import fhe_server_compute
import json
import os
import traceback
import sys
from fhe_studio_config import user_info, user_sub, \
            user_sub_or_default, new_fhe_token
from hashlib import sha256

from mongo_context import find_circuit, find_circuits,\
    vault, delete_circuit, client_specs, delete_vault_item, \
    client_src, mongo_create_fhe_user, mongo_fetch_user,\
    mongo_user_password_update
import logging

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

root.handlers.clear()
root.addHandler(handler)

logging.info('----------Starting FHE STUDIO API----------------')


app = Flask(__name__)

@app.route('/api/edit-circuit/', methods=['PUT'], defaults={'id': None})
@app.route('/api/edit-circuit/<id>', methods=['PUT'])
def edit_circuit(id):
    form = json.loads(request.data)
    u = user_info()
    usrData = {
        "sub": u["sub"],
        "email": u["email"],
        "src": form['src'],
        "name": form['name'],
        "description": form['description'],
        "is_private": bool(form['is_private']),
        "is_published": bool(form['is_published'])
        }
    logging.info(f'edit-circuit id: {id} , {usrData}')
    result = fhe_compile(id, usrData)
    return result

@app.route('/api/play-circuit', methods=['POST'])
def play_circuit():
    form = json.loads(request.data)
    result = fhe_play(form)
    return {
        'output': result.get('output', ''),
        'exception': result.get('exception',''),
    }

@app.route('/api/delete-circuit/<id>', methods=['DELETE'])
def api_edit_circuit(id):
    return delete_circuit(id, user_sub())


@app.route('/api/fhe-eval/<eval_key_id>', methods=['POST'])
def fhe_eval(eval_key_id):
    form = json.loads(request.data)
     
    return fhe_server_compute(eval_key_id, form['values'], user_sub())

def list_circuits(is_published_only = False, sub = None):
    term = str(request.args.get('name',''))
    logging.debug(f'search term:{term}')
    c = find_circuits(term, is_published_only, sub)
    records = []
    for x in c:
        records.append ({
            'id' : str(x['_id']), 
            'name' : x.get('name', None),
            'polynomial_size': x.get('polynomial_size', None),
            'complexity': x.get('complexity', None),
            'description' : x.get('description', None),
            'created_time': x.get('created_time', None),
            "is_published": x.get('is_published', False),
        })
    return records

@app.route('/api/circuits', methods=['GET'])
def circuits():
    return list_circuits(is_published_only = True)

@app.route('/api/my-circuits', methods=['GET'])
def my_circuits():
    return list_circuits(sub = user_sub())

@app.route('/api/circuit/<circuit_id>', methods=['POST'])
def circuit(circuit_id):
    c = find_circuit(circuit_id)
    locked = c['sub'] == user_sub_or_default('None')
    src = c['src']

    if c['is_private'] and c['sub'] != user_sub_or_default('None'):
        src = '# source code is private for this circuit'

    return { 
        "name": c['name'], 
        "src": src, 
        "description": c["description"], 
        "is_private": c["is_private"], 
        "is_published": c.get("is_published", False),
        "polynomial_size": c["polynomial_size"], 
        "locked": not locked,
        "output":c.get('output', '')
    }

@app.route('/api/mlir/<circuit_id>', methods=['GET'])
def show_mlir(circuit_id):
    c = find_circuit(circuit_id)
    return {"mlir": c.get("mlir", "no code for this circuit")}

@app.route('/api/add-vault/<id>', methods=['PUT'])
def add_vault_api(id):
    client_key_gen(id, user_sub())
    return "{}"

   
@app.route('/api/vault', methods=['POST'])
def vault_api():
    c = vault(user_sub())
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

# ********************************
# Todo: redo the vault, make it more intuitive
# ********************************
@app.route('/api/vault/encrypt/<id>', methods=['POST'])
def vault_encrypt_api(id):
    user_sub()
    form = json.loads(request.data)
    return encrypt(form['client_specs'], form['values'], id)

@app.route('/api/vault/decrypt/<id>', methods=['POST'])
def vault_decrypt_api(id):
    user_sub()
    form = json.loads(request.data)
    return [ decrypt(form['client_specs'], form['values']) ]

@app.route('/api/vault/client-specs/<id>', methods=['POST'])
def client_specs_api(id):
    s = client_specs(id, user_sub())
    return [ s ]


@app.route('/api/delete-vault-item/<id>', methods=['DELETE'])
def api_delete_vault_item(id):
    return delete_vault_item(id, user_sub())

@app.route('/api/vault-circuit/<id>', methods=['GET'])
def api_client_src(id):
    return client_src(id, user_sub())


@app.route('/api/fhe-create-user', methods=['POST'])
def app_fhe_create_user():
    form = json.loads(request.data)
    logging.info(f"create a new user {form['username']}")

    h = sha256(form['password'].encode('utf-8')).hexdigest()
    sub = mongo_create_fhe_user(form['username'], h)
    _, token = new_fhe_token(form['username'], str(sub))
    return {'code': token }

@app.route('/api/oid-fhe-login', methods=['POST'])
def app_oid_fhe_login():
    form = json.loads(request.data)
    logging.info(f"authenticating user {form['username']}")

    h = sha256(form['password'].encode('utf-8')).hexdigest()
    u = mongo_fetch_user(form['username'], h)
    _, token = new_fhe_token(u['username'], str(u['_id']))
    return {'code': token }



@app.route('/api/oid-token', methods=['POST'])
def app_oid_token():
    return {'access_token':  request.args.get('code')}

@app.route('/api/oid-user-info')
def app_oid_user_info():
    return user_info()

@app.route('/api/oid_password_update', methods=['POST'])
def app_oid_password_update():
    form = json.loads(request.data)
    h_current = sha256(form['current_password'].encode('utf-8')).hexdigest()
    h_new = sha256(form['new_password'].encode('utf-8')).hexdigest()
    mongo_user_password_update(user_sub(), h_current, h_new)
    return {}

@app.route('/dev-token', methods=['POST'])
def dev_token():
    return {'access_token':'dev-access-token'}



@app.route('/dev-user')
def dev_user():
    return user_info()

@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    traceback.print_exception(*sys.exc_info())

    if str(e) == 'USER_NOT_AUTHORIZED':
        return  f"NOT_AUTHORIZED", 401
    
    return  f"Internal Error: {str(e)}", 500


#this one is to serve local UI in the same docker image
@app.route('/<path:path>')
def send_report(path):
    return send_from_directory('static', path)

@app.route('/')
@app.route('/oauth2')
@app.route('/fhe-vault')
@app.route('/fhe-editor')
@app.route('/circuits-zoo')
def send_report_index():
    return send_from_directory('static', 'index.html')


@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    #print(e)
    traceback.print_exception(*sys.exc_info())

    if str(e) == 'USER_NOT_AUTHORIZED':
        return  f"NOT_AUTHORIZED", 401
    
    return  f"Internal Error: {str(e)}", 500


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
