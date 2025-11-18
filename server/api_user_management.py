"""
User Management API
Handles all user-related operations: add, update, delete, view, and search users.
Admin users require username and password, members do not.
"""

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/users", tags=["Users"])

# User database
user_db = {
    1: {
        "name": "John Doe",
        "email": "john@example.com",
        "role": "admin",
        "username": "johndoe",
        "password": "admin123",
    },
    2: {"name": "Jane Smith", "email": "jane@example.com", "role": "member"},
    3: {"name": "Bob Wilson", "email": "bob@example.com", "role": "member"},
    4: {"name": "Alice Brown", "email": "alice@example.com", "role": "member"},
}


class UserModel(BaseModel):
    """User model schema"""

    name: str
    email: EmailStr
    role: str
    username: Optional[str] = None
    password: Optional[str] = None


@router.post("/", response_model=UserModel, summary="Add a new user")
async def create_user(user: UserModel):
    """
    Add a new user to the system.
    Admin users must have username and password.
    Members do not need username and password.
    """
    if user.role == "admin" and (not user.username or not user.password):
        raise HTTPException(
            status_code=400, detail="Admin users must have username and password"
        )

    new_id = max(user_db.keys()) + 1 if user_db else 1
    user_data = user.model_dump()

    # Remove username and password for members
    if user.role == "member":
        user_data.pop("username", None)
        user_data.pop("password", None)

    user_db[new_id] = user_data
    return user_db[new_id]


@router.get("/", summary="Get all users")
async def get_all_users():
    """Retrieve all users in the system"""
    return {"users": user_db, "total": len(user_db)}


@router.get("/search/", summary="Search users by keyword")
async def search_users(
    keyword: str = Query(..., description="Keyword to search in any user field")
):
    """Search users by keyword in any field"""
    q = keyword.lower()
    results = []
    for user_id, user in user_db.items():
        if q in str(user_id).lower():
            results.append({"id": user_id, **user})
            continue
        for value in user.values():
            if q in str(value).lower():
                results.append({"id": user_id, **user})
                break
    return {"results": results, "total": len(results)}


@router.put("/{user_id}", response_model=UserModel, summary="Update user")
async def update_user(
    user: UserModel, user_id: int = Path(..., description="The ID of the user to update")
):
    """
    Update an existing user.
    Admin users must have username and password.
    """
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin" and (not user.username or not user.password):
        raise HTTPException(
            status_code=400, detail="Admin users must have username and password"
        )

    user_data = user.model_dump()

    # Remove username and password for members
    if user.role == "member":
        user_data.pop("username", None)
        user_data.pop("password", None)

    user_db[user_id] = user_data
    return user_db[user_id]


@router.delete("/{user_id}", summary="Delete user")
async def delete_user(
    user_id: int = Path(..., description="The ID of the user to delete")
):
    """Delete a user from the system"""
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="User not found")
    del user_db[user_id]
    return {"message": "User deleted successfully", "user_id": user_id}
