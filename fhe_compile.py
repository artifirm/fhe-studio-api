import json
from typing import Callable
from RestrictedPython import safe_builtins, compile_restricted
from RestrictedPython import Eval, Guards
from RestrictedPython.PrintCollector import PrintCollector
from concrete.fhe.extensions.tag import tag_context 
from mongo_context import persist_circuit
from multiprocessing import Process, Manager
from concrete import fhe
import logging

_SAFE_MODULES = frozenset(("numpy","concrete", "numpy.core._methods"))

def _safe_import(name, *args, **kwargs):
    logging.debug(f'import {name}')
    if name not in _SAFE_MODULES:
        logging.warn(f'import not permitted {name}')
        raise Exception(f"Don't you even think about {name!r}")
    module = __import__(name, *args, **kwargs) 

    # inject proxy methods
    if name == 'concrete':
        fhe_studio_ex = {
            "compiler_fn": module.fhe.Compiler,
            "compiler_decorator_fn": module.fhe.compiler,
            "compile_decorator_fn": None,
            "compile_fn": None,
            "_globals": args[0]
        }

        # fhe.Compile class support
        def _compile_fn(*args, **kwargs):
            logging.debug('compiling the circuit')
            compiled_circuit =  fhe_studio_ex["compile_fn"] (*args, **kwargs)
            fhe_studio_ex["_globals"]["compiled_circuit"] = compiled_circuit
            logging.debug('_compile_fn set using the class fhe.Compile')
            return compiled_circuit
        
        def _compiler_fn(*args, **kwargs):
            logging.debug('creating the compiler instance')
            compiler = fhe_studio_ex["compiler_fn"] (*args, **kwargs)
            
            fhe_studio_ex["compile_fn"] = compiler.compile
            compiler.compile = _compile_fn
            return compiler
        # @fhe.compile decorator support
        def _fhe_compile_decor_fn(*args, **kwargs):
            logging.debug('creating the compile decorator')
            compiled_circuit = fhe_studio_ex["compile_decorator_fn"](*args, **kwargs)
            fhe_studio_ex["_globals"]["compiled_circuit"] = compiled_circuit
            logging.debug('_fhe_compile_decor_fn set using @fhe.compile')
            return compiled_circuit
        
        def _fhe_compiler_decor_fn(*args, **kwargs):
            logging.debug('creating the compiler decorator')
            dec_fn = fhe_studio_ex["compiler_decorator_fn"] (*args, **kwargs)
            def decoration(func: Callable):
                dec_fn_result = dec_fn(func)
                fhe_studio_ex["compile_decorator_fn"] = dec_fn_result.compile
                dec_fn_result.compile = _fhe_compile_decor_fn
                #logging.error(dec_fn_result)
                return dec_fn_result
            return decoration
        
        module.fhe.Compiler = _compiler_fn
        module.fhe.compiler = _fhe_compiler_decor_fn
    return module

# sandbox for fhe compilation
def execute_user_code_local(user_code, user_func, return_dict):
    
    def _apply(f, *a, **kw):
        return f(*a, **kw)
    
    my_globals = {
        "__builtins__": {
            **safe_builtins,
            "__import__": _safe_import,
            "_getitem_": Eval.default_guarded_getitem,
            "_getiter_": Eval.default_guarded_getiter,
            "_apply_": _apply,
            "map": map,
            "filter": filter,
            "list": list,
            "_iter_unpack_sequence_": Guards.guarded_iter_unpack_sequence
        },
        '_print_': PrintCollector,
    }

    try:
        byte_code = compile_restricted(user_code)
        exec(byte_code, my_globals)
        
        if user_func not in my_globals:
            raise Exception("FHE circuit has not been compiled, please make sure you call the compile function!")
        
        server = my_globals[user_func].server;
        print_lines = my_globals.get("_print", lambda : '')()[-1024:]

        config_str =  server.client_specs.serialize().decode('utf-8');
        logging.debug(config_str)

        bootstrap_keys = json.loads(config_str).get("bootstrapKeys" ,[])
        # if keys dont exists
        bootstrap_keys.append({})

        return_dict['value'] = { 
            "mlir": server._mlir, 
            "complexity": int(server.complexity), 
            "config": json.dumps(server._configuration.__dict__), 
            "client_specs": config_str,
            "polynomial_size": bootstrap_keys[0].get("polynomialSize" , 0),
            'output': print_lines
        }

    except Exception as e:
        err_str = str(e)
        logging.error (e)
        return_dict['value'] = {'exception': err_str }


def execute_user_code(user_code, user_func, time_out_sec = 30):
    manager = Manager()
    return_dict = manager.dict()

    p = Process(
        target=execute_user_code_local,
        args=(user_code, user_func, return_dict), 
        kwargs={})
    p.start()
    p.join(time_out_sec)  # sec
    if p.is_alive():
        p.terminate()
        raise Exception(f"Exceeded execution limit")
    logging.debug(f'return_dict: {return_dict}' )
    return return_dict['value']

def fhe_play(usrData):
    src = usrData['src']
    tag_context.stack = []
    logging.info(src)
    doc = execute_user_code(src, "compiled_circuit")
    if 'exception' in doc:
        return {'exception' : doc['exception'] }
    
    return doc

def fhe_compile(id, usrData):
    doc = fhe_play(usrData)
    new_doc = { **doc, **usrData }

    logging.debug(new_doc)
    id = persist_circuit(id, new_doc)
    
    return { 'id': id, 
            'output': doc.get('output', ''),
            'exception': doc.get('exception', '')
        }