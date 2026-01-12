from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from difflib import unified_diff
from app.models import Prompt, PromptVersion, PromptMetadata, User
from app.schemas import (
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    VersionCreateRequest,
    VersionComparisonResponse,
    PromptListResponse,
)
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.post("/", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
def create_prompt(
    prompt: PromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_prompt = Prompt(
        title=prompt.title,
        description=prompt.description,
        content=prompt.content,
        model=prompt.model,
        tags=prompt.tags,
        author_id=current_user.id,
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)

    db_version = PromptVersion(
        prompt_id=db_prompt.id,
        version_number=1,
        content=prompt.content,
        model=prompt.model,
        change_description="Initial version",
    )
    db.add(db_version)

    db_metadata = PromptMetadata(prompt_id=db_prompt.id)
    db.add(db_metadata)

    db.commit()
    db.refresh(db_prompt)
    return db_prompt


@router.get("/{prompt_id}", response_model=PromptResponse)
def get_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    if prompt.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return prompt


@router.get("/", response_model=PromptListResponse)
def list_prompts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prompts = db.query(Prompt).filter(Prompt.author_id == current_user.id).offset(skip).limit(limit).all()
    total = db.query(Prompt).filter(Prompt.author_id == current_user.id).count()
    return PromptListResponse(total=total, prompts=prompts)


@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt(
    prompt_id: int,
    prompt_update: PromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    if prompt.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    update_data = prompt_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prompt, field, value)

    prompt.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(prompt)
    return prompt


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    if prompt.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db.delete(prompt)
    db.commit()


@router.post("/{prompt_id}/versions", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_version(
    prompt_id: int,
    version_req: VersionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    if prompt.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    last_version = db.query(PromptVersion).filter(PromptVersion.prompt_id == prompt_id).order_by(PromptVersion.version_number.desc()).first()
    next_version_num = (last_version.version_number + 1) if last_version else 1

    db_version = PromptVersion(
        prompt_id=prompt_id,
        version_number=next_version_num,
        content=version_req.content,
        model=version_req.model,
        change_description=version_req.change_description,
    )
    db.add(db_version)

    prompt.content = version_req.content
    prompt.model = version_req.model
    prompt.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_version)
    return {"version_id": db_version.id, "version_number": db_version.version_number}


@router.get("/{prompt_id}/versions", response_model=List[dict])
def get_versions(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    if prompt.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    versions = db.query(PromptVersion).filter(PromptVersion.prompt_id == prompt_id).order_by(PromptVersion.version_number).all()
    return [
        {
            "id": v.id,
            "version_number": v.version_number,
            "content": v.content,
            "model": v.model,
            "change_description": v.change_description,
            "created_at": v.created_at,
        }
        for v in versions
    ]


@router.post("/{prompt_id}/rollback/{version_id}", response_model=PromptResponse)
def rollback_version(
    prompt_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    if prompt.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    version = db.query(PromptVersion).filter(PromptVersion.id == version_id, PromptVersion.prompt_id == prompt_id).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

    last_version = db.query(PromptVersion).filter(PromptVersion.prompt_id == prompt_id).order_by(PromptVersion.version_number.desc()).first()
    new_version_num = last_version.version_number + 1

    new_version = PromptVersion(
        prompt_id=prompt_id,
        version_number=new_version_num,
        content=version.content,
        model=version.model,
        change_description=f"Rolled back to version {version.version_number}",
    )
    db.add(new_version)

    prompt.content = version.content
    prompt.model = version.model
    prompt.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(prompt)
    return prompt


@router.post("/{prompt_id}/compare", response_model=VersionComparisonResponse)
def compare_versions(
    prompt_id: int,
    version_1_id: int,
    version_2_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    if prompt.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    v1 = db.query(PromptVersion).filter(PromptVersion.id == version_1_id, PromptVersion.prompt_id == prompt_id).first()
    v2 = db.query(PromptVersion).filter(PromptVersion.id == version_2_id, PromptVersion.prompt_id == prompt_id).first()

    if not v1 or not v2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

    diff = list(unified_diff(v1.content.splitlines(), v2.content.splitlines(), lineterm=""))
    return VersionComparisonResponse(
        version_1_id=v1.id,
        version_2_id=v2.id,
        version_1_content=v1.content,
        version_2_content=v2.content,
        differences=diff,
    )
