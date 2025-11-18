"""
Library Management System - Main Application
Comprehensive API service for managing books, users, loans, and administrative tasks.
"""

from fastapi import FastAPI
from server.api_book_management import router as book_router
from server.api_user_management import router as user_router
from server.api_loan_management import router as loan_router
from server.api_reports_admin import router as admin_router

app = FastAPI(
    title="Library Management System",
    description="A comprehensive API service for Library Management System with Book Management, User Management, Borrow & Return System, and Reports & Admin features.",
    version="2.0.0",
)

# Include all routers
app.include_router(book_router)
app.include_router(user_router)
app.include_router(loan_router)
app.include_router(admin_router, prefix="/users", tags=["Users"])


@app.get("/", summary="API Information")
async def root():
    """Get API information and available endpoints"""
    return {
        "message": "Welcome to Library Management System API",
        "version": app.version,
        "endpoints": {
            "books": "/books - Book Management (Add, Update, Delete, Show All, Search)",
            "users": "/users - User Management (Add, Update, Delete, Show All, Search)",
            "loans": "/loans - Borrow & Return System (Borrow, Return, Track, List, Check Availability)",
            "admin": "/users/admin - Reports & Admin (Overdue, Most Borrowed, History, Receipt, Login, Dashboard)",
            "docs": "/docs - Interactive API Documentation",
            "redoc": "/redoc - Alternative API Documentation",
        },
    }
