import json
import base64
from concrete import fhe 
from mongo_context import find_circuit, find_keys

def fhe_server_compute(eval_key_id: str, argb64: str):
    k = find_keys(eval_key_id)
    c = k['circuit']
    
    print(c)

    configuration = fhe.Configuration().fork(**json.loads(c['config']))
    server = fhe.Server.create(c['mlir'], configuration, False)
    deserialized_evaluation_keys = fhe.EvaluationKeys.deserialize(k['evaluation_keys'])

    arg = fhe.Value.deserialize(base64.b64decode(argb64))
    result: fhe.Value = server.run(arg, evaluation_keys=deserialized_evaluation_keys)
    serialized_result: bytes = result.serialize()

    return [base64.b64encode(serialized_result).decode("ascii")]