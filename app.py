# save this as app.py
from flask import Flask, request
from fhe_compile import fhe_compile
from fhe_client import client_key_gen
from fhe_server import fhe_server_compute

app = Flask(__name__)


@app.route('/edit-circuit/<id>', methods=['POST'])
def edit_circuit(id):
    print(id)
    print(request.form.get('id'))
    return fhe_compile(request.form.get('src'))

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