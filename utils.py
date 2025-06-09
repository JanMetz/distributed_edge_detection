import shutil
import requests
from pathlib import Path
import json
import socket

configfile_filename = 'config.json'

def register_node(addr: str, port: int, type: str):
    registry_addr = get_registry_addr()
    response = requests.post(f'http://{registry_addr}/nodes', json={"addr": addr + ':' + str(port), "type": type})
    if response.status_code == 200:
        return response.json()['token']

    return None

def remove_node_from_registry(token: str):
    if token is not None:
        registry_addr = get_registry_addr()
        response = requests.delete(f'http://{registry_addr}/nodes/{token}')

        if response.status_code == 200:
            print('Node deleted')

def print_error_msg(msg: str, response: requests.Response):
    print(f'{msg}. Status code: {response.status_code} {response.text}')

def log(msg: str):
    with open('log.txt', 'a') as f:
        f.write(msg + '\n')

def get_config_value(key: str):
    with open(configfile_filename) as json_data:
        d = json.load(json_data)
        return d[key]

def put_value_in_config(key: str, value: str):
    with open(configfile_filename, 'r') as file:
        data = json.load(file)

    data[key] = value

    with open(configfile_filename, 'w') as file:
        json.dump(data, file, indent=4)

def get_registry_addr():
    return get_config_value('registry_addr') + ':' + str(get_config_value('registry_port'))

def get_my_ip():
    return socket.gethostbyname(socket.gethostname())

def cleanup_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)