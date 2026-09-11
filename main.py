from fastapi import FastAPI, HTTPException, status
from fastapi.responses import Response
from pydantic.main import BaseModel
import psycopg
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()


class Post(BaseModel):
    title: str
    description: str
    published: bool = True


while True:
    try:
        conn = psycopg.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        print(conn.execute("SELECT version();").fetchone())
        break
    except psycopg.OperationalError as error:
        print("Connecting to database failed:", error)


@app.get("/")
async def root():
    return {"message": "welcome to my api"}


@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts")
def create_post(post: Post):
    cursor.execute(
        "INSERT INTO posts(title , description , published) VALUES (%s , %s , %s) RETURNING *;",
        (post.title, post.description, post.published),
    )
    new_post = cursor.fetchone()
    conn.commit()
    return {"new_post": new_post}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"the post with id: {id} not found",
        )
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *;", (id,))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"the post with id : {id} not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        "UPDATE posts SET title = %s , description = %s , published = %s WHERE id = %s RETURNING * ;",
        (post.title, post.description, post.published, id),
    )
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"the post with id: {id} not found",
        )

    return {"data": updated_post}
