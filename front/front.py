import random
import streamlit as st
import numpy as np
import PIL.Image
import requests
from utils import *
from pathlib import Path

addr = get_my_ip()
port = 8051
token = register_node(addr, 8555, 'front')
log(f'Front: running at addr: {addr} port: {port}')

DOWNLOAD_DIR = Path("downloads")
registry_addr = get_registry_addr()

try:
    if token is not None:
        st.title("Edge detection App")
        st.write("Upload your image below to see edge detection at work!")

        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_file:

            response = requests.get(f'http://{registry_addr}/nodes', params={"type": "back"})

            if response.status_code == 200:
                backend_nodes = response.json()['nodes']
                if len(backend_nodes) > 0:
                    node = backend_nodes[random.randint(0, len(backend_nodes) - 1)]
                    response = requests.post(f'http://{node["addr"]}/images',  data={"token": token}, files={"file": uploaded_file.read()})
                else:
                    log("Front: No nodes in the registry")
            else:
                print_error_msg('Failed to get nodes', response)

            if response.status_code == 200:
                st.write(response.json()['desc'])
            else:
                print_error_msg('Failed to download file', response)
    else:
        log('Front: could not obtain token')
        st.title("Uuuups...")
        st.write("We had trouble contacting the registry service. Please try again later.")

finally:
    cleanup_dir(DOWNLOAD_DIR)
    remove_node_from_registry(token)

