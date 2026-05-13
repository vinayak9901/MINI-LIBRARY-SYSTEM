from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List

# Initialize the API
app = FastAPI(title="Mini-Library API")
@app.get("/")
def read_root():
    return {"message": "Welcome to the Mini-Library API! Go to /docs to test it."}

# --- FAKE DATABASE ---
# For this example, we will store data in a simple Python dictionary instead of a real database.
fake_db = {
    1: {"id": 1, "title": "The Hobbit", "author": "J.R.R. Tolkien"},
    2: {"id": 2, "title": "1984", "author": "George Orwell"}
}
current_id = 2 # Keeps track of the latest ID

# --- SCHEMAS (Data Validation) ---
# Pydantic makes sure the user sends the correct JSON body format
class BookCreate(BaseModel):
    title: str
    author: str

class BookResponse(BookCreate):
    id: int


# --- THE ENDPOINTS (From your image) ---

# 1. GET /books -> Retrieve all books
# Requirements: Supports optional Query Parameter 'author'
@app.get("/books", response_model=List[BookResponse])
def get_all_books(author: Optional[str] = None):
    # If the user typed an author query (e.g., /books?author=1984), filter it:
    if author:
        return [book for book in fake_db.values() if book["author"].lower() == author.lower()]
    
    # Otherwise, return all books
    return list(fake_db.values())


# 2. GET /books/{id} -> Retrieve a specific book
# Requirements: Requires Path Parameter id: int. Returns 404 if not found.
@app.get("/books/{id}", response_model=BookResponse)
def get_book(id: int):
    book = fake_db.get(id)
    if not book:
        # This automatically sends the 404 error back to the user
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# 3. POST /books -> Create a new book
# Requirements: Requires JSON body. Returns 201 Created.
@app.post("/books", status_code=status.HTTP_201_CREATED, response_model=BookResponse)
def create_book(book: BookCreate):
    global current_id
    current_id += 1
    
    # Convert the user's JSON into a dictionary and add the new ID
    new_book = {"id": current_id, **book.model_dump()}
    fake_db[current_id] = new_book
    
    return new_book


# 4. PUT /books/{id} -> Update a book
# Requirements: Requires Path Parameter id: int and a JSON Body
@app.put("/books/{id}", response_model=BookResponse)
def update_book(id: int, book: BookCreate):
    # First, check if the book exists
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Book not found")

    # Update the data
    updated_book = {"id": id, **book.model_dump()}
    fake_db[id] = updated_book
    
    return updated_book