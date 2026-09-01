from fastapi import APIRouter, UploadFile
import os

router = APIRouter()

@router.post("/replicate/artifact")
async def replicate_artifact(file: UploadFile):
    dst = f"/app/data/artifacts/{file.filename}"
    with open(dst, "wb") as f:
        f.write(await file.read())
    return {"status": "ok"}
