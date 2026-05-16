from fastapi import FastAPI, Path, Query, HTTPException
from typing_extensions import Annotated
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str
    pages: int

library = {
    "Автор1": [
        Book(title="Книга1", author="Автор1", pages=150),
        Book(title="Книга2", author="Автор1", pages=200),
    ],
    "Автор2": [
        Book(title="Книга3", author="Автор2", pages=120),
        Book(title="Книга4", author="Автор2", pages=180),
    ],
}

def validate(author: str, pages: int):
    if (not 3 <= len(author) <= 30) or (pages < 10):
        raise HTTPException(status_code=400)

@app.get("/books")
async def get_books():
    return library

@app.post("/books/upload")
async def upload_book(title: str, 
                      author: Annotated[str, Query(
                                    min_length = 3, 
                                    max_length = 30, 
                                    description = "Author's name")],
                      pages: Annotated[int, Query(
                                    ge = 10,
                                    description = "Amount of pages"
                      )]):
    validate(author, pages)
    if author in library.keys():
        if title in [book.title for book in library[author]]:
            raise HTTPException(status_code=400, detail="Book already exists")
        else:
            library[author].append(Book(title = title, author = author, pages = pages))
    else:
        library[author] = [Book(title = title, author = author, pages = pages)]

@app.get("/books/{author}")
async def get_author_books(author: str):
    if author in library.keys():
        return library[author]
    else:
        raise HTTPException(status_code=400, detail="No such author in the library")

@app.put("/book/update")
async def change_book_info(author: str, 
                           title: str, 
                           new_title: str,
                           new_pages: int):
    validate(author, new_pages)
    books_author = [book for book in library[author]]
    for book in books_author:
        if book.title == title:
            book.title = new_title
            book.pages = new_pages
            break
        else:
            raise HTTPException(status_code=400, detail="No such book in the library")

@app.delete("/book/delete")
async def delete_book(author: str, title: str):
    if author in library.keys():
        for book in library[author]:
            if book.title == title:
                library[author].remove(book)
    else:
        raise HTTPException(status_code=400, detail="No such book in the library")