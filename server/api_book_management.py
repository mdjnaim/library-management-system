"""
Book Management API
Handles all book-related operations: add, update, delete, view, and search books.
"""

from fastapi import APIRouter, Query, Path, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/books", tags=["Books"])

# Book database
book_db = {
    1: {
        "title": "1984",
        "author": "George Orwell",
        "isbn": "9780451524935",
        "published_year": 1949,
        "copies_available": 4,
    },
    2: {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "isbn": "9780060935467",
        "published_year": 1960,
        "copies_available": 2,
    },
    3: {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "9780743273565",
        "published_year": 1925,
        "copies_available": 5,
    },
    4: {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "isbn": "9780141439518",
        "published_year": 1813,
        "copies_available": 3,
    },
    5: {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "isbn": "9780316769488",
        "published_year": 1951,
        "copies_available": 6,
    },
}


class BookModel(BaseModel):
    """Book model schema"""

    title: str
    author: str
    isbn: str
    published_year: int
    copies_available: int


@router.post("/", response_model=BookModel, summary="Add a new book")
async def add_book(book: BookModel):
    """Add a new book to the library"""
    new_id = max(book_db.keys()) + 1 if book_db else 1
    book_db[new_id] = book.model_dump()
    return book_db[new_id]


@router.get("/", summary="Get all books")
async def get_all_books():
    """Retrieve all books in the library"""
    return {"books": book_db, "total": len(book_db)}


@router.get("/search/", summary="Search books by keyword")
async def search_books(
    keyword: str = Query(..., description="Keyword to search in any book field")
):
    """Search books by keyword in any field"""
    q = keyword.lower()
    results = []
    for book_id, book in book_db.items():
        if q in str(book_id).lower():
            results.append({"id": book_id, **book})
            continue
        for value in book.values():
            if q in str(value).lower():
                results.append({"id": book_id, **book})
                break
    return {"results": results, "total": len(results)}


@router.get("/{book_id}", response_model=BookModel, summary="Get book by ID")
async def get_book(
    book_id: int = Path(..., description="The ID of the book to retrieve")
):
    """Retrieve a specific book by ID"""
    if book_id not in book_db:
        raise HTTPException(status_code=404, detail="Book not found")
    return book_db[book_id]


@router.put("/{book_id}", response_model=BookModel, summary="Update book")
async def update_book(
    book: BookModel, book_id: int = Path(..., description="The ID of the book to update")
):
    """Update an existing book"""
    if book_id not in book_db:
        raise HTTPException(status_code=404, detail="Book not found")
    book_db[book_id] = book.model_dump()
    return book_db[book_id]


@router.delete("/{book_id}", summary="Delete book")
async def delete_book(
    book_id: int = Path(..., description="The ID of the book to delete")
):
    """Delete a book from the library"""
    if book_id not in book_db:
        raise HTTPException(status_code=404, detail="Book not found")
    del book_db[book_id]
    return {"message": "Book deleted successfully", "book_id": book_id}