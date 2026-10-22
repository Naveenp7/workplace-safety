from __future__ import annotations
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/faces", tags=["Face Recognition"])


def get_face_recognizer(request: Request):
    return request.app.state.face_recognizer


class PersonResponse(BaseModel):
    id: str
    name: str
    image_count: int
    encoding_count: int
    thumbnail_b64: Optional[str] = None


@router.get("", response_model=List[PersonResponse])
async def list_persons(request: Request):
    fr = get_face_recognizer(request)
    persons = fr.get_all_persons()
    result = []
    for p in persons:
        thumb = fr.get_person_thumbnail(p["id"])
        result.append(PersonResponse(**p, thumbnail_b64=thumb))
    return result


@router.post("", response_model=dict)
async def add_person(
    request: Request,
    name: str = Form(...),
    images: List[UploadFile] = File(...)
):
    fr = get_face_recognizer(request)
    image_bytes_list = [await img.read() for img in images]
    result = fr.add_person(name.strip(), image_bytes_list)
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail={"message": "No valid face detected in any image", "errors": result["errors"]}
        )
    return result


@router.post("/{person_id}/images", response_model=dict)
async def add_images_to_person(
    person_id: str,
    request: Request,
    images: List[UploadFile] = File(...)
):
    fr = get_face_recognizer(request)
    image_bytes_list = [await img.read() for img in images]
    result = fr.add_images_to_person(person_id, image_bytes_list)
    return result


@router.delete("/{person_id}")
async def delete_person(person_id: str, request: Request):
    fr = get_face_recognizer(request)
    success = fr.delete_person(person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
    return {"message": "Person deleted"}


@router.get("/status")
async def face_recognition_status(request: Request):
    fr = get_face_recognizer(request)
    return {
        "is_trained": fr.is_trained,
        "person_count": len(fr.get_all_persons()),
        "total_encodings": len(fr._all_encodings),
    }
