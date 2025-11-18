"""
Reports & Admin API
Handles administrative functions: overdue tracking, statistics, receipts, and authentication.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os

router = APIRouter(prefix="/admin", tags=["Reports & Admin"])

from .api_loan_management import loan_db
from .api_book_management import book_db
from .api_user_management import user_db

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


class LoginModel(BaseModel):
    """Admin login credentials"""

    username: str
    password: str


class ReceiptModel(BaseModel):
    """Receipt generation request"""

    loan_id: int

@router.get("/overdue", summary="Get overdue books")
async def get_overdue_books():
    """Get all books that are overdue for return"""
    today = datetime.now().date()
    overdue_loans = []

    for loan_id, loan in loan_db.items():
        if loan["status"] == "active":
            due_date = datetime.strptime(loan["due_date"], "%Y-%m-%d").date()
            if due_date < today:
                days_overdue = (today - due_date).days
                book_title = book_db.get(loan["book_id"], {}).get("title", "Unknown")
                user_name = user_db.get(loan["user_id"], {}).get("name", "Unknown")

                overdue_loans.append(
                    {
                        "loan_id": loan_id,
                        **loan,
                        "book_title": book_title,
                        "user_name": user_name,
                        "days_overdue": days_overdue,
                    }
                )

    return {"overdue_books": overdue_loans, "total": len(overdue_loans)}

@router.get("/most-borrowed", summary="Get most borrowed book statistics")
async def get_most_borrowed_book():
    """Get statistics on the most borrowed books"""
    borrow_count: dict[int, int] = {}

    for loan in loan_db.values():
        book_id = loan["book_id"]
        borrow_count[book_id] = borrow_count.get(book_id, 0) + 1

    if not borrow_count:
        return {"message": "No borrowing history found"}

    most_borrowed_id = max(borrow_count.keys(), key=lambda k: borrow_count[k])
    most_borrowed_book = book_db.get(most_borrowed_id, {})

    return {
        "book_id": most_borrowed_id,
        "title": most_borrowed_book.get("title", "Unknown"),
        "author": most_borrowed_book.get("author", "Unknown"),
        "times_borrowed": borrow_count[most_borrowed_id],
        "all_books_stats": [
            {
                "book_id": book_id,
                "title": book_db.get(book_id, {}).get("title", "Unknown"),
                "times_borrowed": count,
            }
            for book_id, count in sorted(
                borrow_count.items(), key=lambda x: x[1], reverse=True
            )
        ],
    }

@router.get("/history", summary="Get borrowing history")
async def get_borrowing_history(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    book_id: Optional[int] = Query(None, description="Filter by book ID"),
    status: Optional[str] = Query(None, description="Filter by status (active/returned)"),
):
    """Get complete borrowing history with optional filters"""
    history = []

    for loan_id, loan in loan_db.items():
        if user_id and loan["user_id"] != user_id:
            continue
        if book_id and loan["book_id"] != book_id:
            continue
        if status and loan["status"] != status:
            continue

        book_title = book_db.get(loan["book_id"], {}).get("title", "Unknown")
        user_name = user_db.get(loan["user_id"], {}).get("name", "Unknown")

        history.append(
            {
                "loan_id": loan_id,
                **loan,
                "book_title": book_title,
                "user_name": user_name,
            }
        )

    return {"history": history, "total": len(history)}

@router.post("/receipt", summary="Generate member receipt")
async def generate_receipt(receipt_data: ReceiptModel):
    """Generate a printable receipt for a loan transaction"""
    loan_id = receipt_data.loan_id

    if loan_id not in loan_db:
        raise HTTPException(status_code=404, detail="Loan not found")

    loan = loan_db[loan_id]
    book = book_db.get(loan["book_id"], {})
    user = user_db.get(loan["user_id"], {})

    receipts_dir = "receipts"
    if not os.path.exists(receipts_dir):
        os.makedirs(receipts_dir)

    receipt_content = f"""
{'='*50}
           LIBRARY MANAGEMENT SYSTEM
              BORROWING RECEIPT
{'='*50}

Receipt ID: RCPT-{loan_id:04d}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

MEMBER INFORMATION:
- Member ID: {loan['user_id']}
- Name: {user.get('name', 'Unknown')}
- Email: {user.get('email', 'Unknown')}

BOOK INFORMATION:
- Book ID: {loan['book_id']}
- Title: {book.get('title', 'Unknown')}
- Author: {book.get('author', 'Unknown')}
- ISBN: {book.get('isbn', 'Unknown')}

LOAN DETAILS:
- Loan Date: {loan['loan_date']}
- Due Date: {loan['due_date']}
- Return Date: {loan['return_date'] if loan['return_date'] else 'Not returned yet'}
- Status: {loan['status'].upper()}

{'='*50}
Thank you for using our library service!
{'='*50}
"""

    filename = f"receipt_loan_{loan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(receipts_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(receipt_content)

    return {
        "message": "Receipt generated successfully",
        "filename": filename,
        "filepath": filepath,
        "receipt_content": receipt_content,
    }

@router.post("/login", summary="Admin login")
async def admin_login(credentials: LoginModel):
    """Authenticate admin user (simplified authentication for demo)"""
    if (
        credentials.username == ADMIN_USERNAME
        and credentials.password == ADMIN_PASSWORD
    ):
        return {
            "message": "Login successful",
            "user": credentials.username,
            "role": "admin",
            "token": f"fake-jwt-token-{datetime.now().timestamp()}",
        }
    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.get("/dashboard", summary="Get dashboard statistics")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics for admin"""
    total_books = len(book_db)
    total_users = len(user_db)
    total_loans = len(loan_db)
    active_loans = sum(1 for loan in loan_db.values() if loan["status"] == "active")

    today = datetime.now().date()
    overdue_count = 0
    for loan in loan_db.values():
        if loan["status"] == "active":
            due_date = datetime.strptime(loan["due_date"], "%Y-%m-%d").date()
            if due_date < today:
                overdue_count += 1

    return {
        "total_books": total_books,
        "total_users": total_users,
        "total_loans": total_loans,
        "active_loans": active_loans,
        "overdue_loans": overdue_count,
        "returned_loans": total_loans - active_loans,
    }
