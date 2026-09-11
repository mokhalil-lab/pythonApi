from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import Response
from pydantic.main import BaseModel
from sqlalchemy.orm import Session

from pythonapi.database import Base, SessionLocal, engine
from pythonapi.models import Post as PostModel  # alias! see below

Base.metadata.create_all(bind=engine)

app = FastAPI()

load_dotenv()


class Post(BaseModel):
    title: str
    description: str
    published: bool = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "welcome to my api"}


@app.get("/posts")
def get_posts(db: Annotated[Session, Depends(get_db)]):
    posts = db.query(PostModel).all()
    return {"data": posts}


@app.post("/posts")
def create_post(post: Post, db: Annotated[Session, Depends(get_db)]):
    new_post = PostModel(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"new_post": new_post}


@app.get("/posts/{id}")
def get_post(id: int, db: Annotated[Session, Depends(get_db)]):
    post = db.query(PostModel).filter(PostModel.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"the post with id: {id} not found",
        )
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Annotated[Session, Depends(get_db)]):
    post = db.query(PostModel).filter(PostModel.id == id).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"the post with id : {id} not found",
        )

    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post, db: Annotated[Session, Depends(get_db)]):
    existing = db.query(PostModel).filter(PostModel.id == id).first()

    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"the post with id: {id} not found",
        )

    existing.title = post.title
    existing.description = post.description
    existing.published = post.published

    db.commit()
    db.refresh(existing)
    return {"data": existing}
