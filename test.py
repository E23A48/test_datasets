from PIL import Image, ImageSequence, features
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from starlette.responses import StreamingResponse
import io
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

def thumbnails(frames, size):
    for frame in frames:
        thumbnail = frame.copy()
        thumbnail.thumbnail(size, Image.ANTIALIAS)
        yield thumbnail

def image_to_byte_array(image:Image):
  imgByteArr = io.BytesIO()
  image.save(imgByteArr, format=image.format)
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr


@app.post("/operation")
async def to_webp(file: UploadFile = File(...), width: int = Form(96), height: int = Form(96), quality: int = Form(70)):
    contents = await file.read()
    im = Image.open(io.BytesIO(contents))
    size = width, height
    im.thumbnail(size, Image.ANTIALIAS)

    tempFile = io.BytesIO()
    im.save(tempFile, format="WEBP", save_all=False, quality=quality)
    tempFile.seek(0)

    return StreamingResponse(io.BytesIO(tempFile.read()), media_type="image/webp")


@app.post("/webpmux")
async def webpmux(file: UploadFile = File(...), width: int = Form(96), height: int = Form(96), quality: int = Form(70)):
    contents = await file.read()
    size = width, height
    im = Image.open(io.BytesIO(contents))
    frames = ImageSequence.Iterator(im)
    frames = thumbnails(frames, size)

    tempFile = io.BytesIO()

    om = next(frames)
    om.info = im.info
    om.save(tempFile, format="WEBP", save_all=True, append_images=list(frames), quality=quality)
    tempFile.seek(0)
    
    return StreamingResponse(io.BytesIO(tempFile.read()), media_type="image/webp")
