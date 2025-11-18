"""
Borrow & Return System API
Handles book borrowing, returns, tracking, and availability checks.
"""

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/loans", tags=["Borrow & Return System"])

# Loan database
loan_db = {
    1: {
        "book_id": 1,
        "user_id": 1,
        "loan_date": "2025-11-01",
        "due_date": "2025-11-15",
        "return_date": "2025-11-14",
        "status": "returned",
    },
    2: {
        "book_id": 2,
        "user_id": 2,
        "loan_date": "2025-11-10",
        "due_date": "2025-11-24",
        "return_date": None,
        "status": "active",
    },
    3: {
        "book_id": 3,
        "user_id": 1,
        "loan_date": "2025-11-15",
        "due_date": "2025-11-29",
        "return_date": None,
        "status": "active",
    },
}

from .api_book_management import book_db


class BorrowModel(BaseModel):
    """Borrow request model"""

    book_id: int
    user_id: int


class ReturnModel(BaseModel):
    """Return request model"""

    loan_id: int


@router.post("/borrow", summary="Borrow a book")
async def borrow_book(borrow: BorrowModel):
    """
    Borrow a book from the library.
    Decreases available copies and creates a loan record.
    """
    if borrow.book_id not in book_db:
        raise HTTPException(status_code=404, detail="Book not found")

    if book_db[borrow.book_id]["copies_available"] <= 0:
        raise HTTPException(status_code=400, detail="Book not available")

    loan_date = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    new_id = max(loan_db.keys()) + 1 if loan_db else 1

    loan_db[new_id] = {
        "book_id": borrow.book_id,
        "user_id": borrow.user_id,
        "loan_date": loan_date,
        "due_date": due_date,
        "return_date": None,
        "status": "active",
    }

    book_db[borrow.book_id]["copies_available"] -= 1

    return {
        "loan_id": new_id,
        "message": "Book borrowed successfully",
        **loan_db[new_id],
    }


@router.post("/return", summary="Return a borrowed book")
async def return_book(return_data: ReturnModel):
    """
    Return a borrowed book to the library.
    Increases available copies and updates loan status.
    """
    if return_data.loan_id not in loan_db:
        raise HTTPException(status_code=404, detail="Loan not found")

    loan = loan_db[return_data.loan_id]

    if loan["status"] == "returned":
        raise HTTPException(status_code=400, detail="Book already returned")

    loan["return_date"] = datetime.now().strftime("%Y-%m-%d")
    loan["status"] = "returned"

    book_db[loan["book_id"]]["copies_available"] += 1

    return {"message": "Book returned successfully", "loan": loan}


@router.get("/track", summary="Track borrowing by user or book")
async def track_borrowing(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    book_id: Optional[int] = Query(None, description="Filter by book ID"),
):
    """Track which member borrowed which book"""
    results = []
    for loan_id, loan in loan_db.items():
        if user_id and loan["user_id"] != user_id:
            continue
        if book_id and loan["book_id"] != book_id:
            continue
        results.append({"loan_id": loan_id, **loan})

    return {"borrowings": results, "total": len(results)}


@router.get("/borrowed", summary="List all currently borrowed books")
async def list_borrowed_books():
    """List all books that are currently borrowed (active loans)"""
    active_loans = []
    for loan_id, loan in loan_db.items():
        if loan["status"] == "active":
            book_title = book_db.get(loan["book_id"], {}).get("title", "Unknown")
            active_loans.append({"loan_id": loan_id, **loan, "book_title": book_title})

    return {"borrowed_books": active_loans, "total": len(active_loans)}


@router.get("/availability/{book_id}", summary="Check book availability")
async def check_availability(
    book_id: int = Path(..., description="The ID of the book to check")
):
    """Check if a specific book is available for borrowing"""
    if book_id not in book_db:
        raise HTTPException(status_code=404, detail="Book not found")

    book = book_db[book_id]
    is_available = book["copies_available"] > 0

    return {
        "book_id": book_id,
        "title": book["title"],
        "copies_available": book["copies_available"],
        "is_available": is_available,
    }
