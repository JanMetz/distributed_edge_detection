import requests
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
import cv2
from PIL import Image
import numpy as np
from utils import *

app = FastAPI()

images = []
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
registry_addr = get_registry_addr()


@app.post("/images")
async def post_images( token: str = Form(...), file: UploadFile = File(...)):
    if token is not None:
        response = requests.post(f'http://{registry_addr}/tokens', json={"token": token})
        if response.status_code != 200:
            print_error_msg('Failed to check token validity', response)
            raise HTTPException(status_code=500, detail='Registry service error')

        msg = response.json()['message']
        if msg != 'valid':
            raise HTTPException(status_code=400, detail='Provided token is not valid')

    try:
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

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
    port = 8001
    token = None
    try:
        token = register_node(host, port, 'back')
        uvicorn.run(app, host=host, port=port)
    finally:
        cleanup_dir(UPLOAD_DIR)
        remove_node_from_registry(token)