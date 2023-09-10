import json
from concrete import fhe 
from mongo_context import find_circuit, find_keys

def fhe_server_compute(eval_key_id):
    k = find_keys(eval_key_id)
    print(k)
    c = find_circuit(k['circuit_id'])
    print(c)

    configuration = fhe.Configuration().fork(**json.loads(c['config']))
    server = fhe.Server.create(c['mlir'], configuration, False)
    deserialized_evaluation_keys = fhe.EvaluationKeys.deserialize(k['evaluation_keys'])

    ###   ####### 
    client_specs = fhe.ClientSpecs.deserialize(c['client_specs'])
    client = fhe.Client(client_specs)

    client.keys.generate(seed=111)

    arg: fhe.Value = client.encrypt(1)

    result: fhe.Value = server.run(arg, evaluation_keys=deserialized_evaluation_keys)
    serialized_result: bytes = result.serialize()

    deserialized_result = fhe.Value.deserialize(serialized_result)
    decrypted_result = client.decrypt(deserialized_result)
    print(f"eval value: {decrypted_result}")