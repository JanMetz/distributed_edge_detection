import requests
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from utils import *
from PIL import Image
import numpy as np
import cv2

app = FastAPI()

images = []
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
registry_addr = get_registry_addr()

@app.post("/images")
async def post_images( token: str = Form(...), file: UploadFile = File(...)):
    log(f'Backend: received post @ images')
    if token is not None:
        response = requests.post(f'http://{registry_addr}/tokens', json={"token": token})
        if response.status_code != 200:
            print_error_msg('Failed to check token validity', response)
            raise HTTPException(status_code=500, detail='Registry service error')

        msg = response.json()['message']
        if msg != 'valid':
            raise HTTPException(status_code=400, detail='Provided token is not valid')
    else:
        log(f'Backend: token not provided')

    try:
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        log(f'Backend: retrieved file')
        img = Image.open(file_path)
        img = np.array(img)

        edges = cv2.Canny(img, 100, 200)
        np.save(UPLOAD_DIR / 'edges.npy', edges)
        file_path = UPLOAD_DIR / 'edges.npy'

        if file_path.exists():
            return FileResponse(file_path, media_type="application/octet-stream", filename='edges.npy')

        return {"error": "File not found"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    host = get_my_ip()
    port = get_config_value('backend_port')
    token = None
    try:
        token = register_node(host, port, 'back')
        log(f'Backend: running at: {host} {port}')
        log(f'Backend: registry_addr: {registry_addr}')
        uvicorn.run(app, host=host, port=port)
    finally:
        cleanup_dir(UPLOAD_DIR)
        remove_node_from_registry(token)