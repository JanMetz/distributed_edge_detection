import random
import streamlit as st
import numpy as np
import PIL.Image
import requests
from utils import *
from pathlib import Path

addr = get_my_ip()
port = get_config_value('frontend_port')
token = register_node(addr, port, 'front')
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
                DOWNLOAD_DIR.mkdir(exist_ok=True)
                with open(DOWNLOAD_DIR / "edges.npy", "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                    print("File downloaded successfully!")

                edges = np.load(DOWNLOAD_DIR / 'edges.npy')
                image = PIL.Image.open(uploaded_file)

                tab1, tab2 = st.tabs(["Detected edges", "Original"])
                tab1.image(edges, use_container_width=True)
                tab2.image(image, use_container_width=True)
            else:
                print_error_msg('Failed to download file', response)
    else:
        log('Front: could not obtain token')
        st.title("Uuuups...")
        st.write("We had trouble contacting the registry service. Please try again later.")

finally:
    cleanup_dir(DOWNLOAD_DIR)
    remove_node_from_registry(token)

