"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal

# Example schemas (kept for reference)

class User(BaseModel):
    """
    Example Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Example Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# SMCC Classroom Evaluation Schemas
# --------------------------------------------------

SMCCRole = Literal[
    "dean",
    "chairperson",
    "subject coordinator",
    "principal",
    "president",
    "vice president",
    "teacher",
]

class SmccUser(BaseModel):
    """
    SMCC users participating in classroom evaluations
    Collection: "smccuser"
    """
    name: str = Field(..., description="Full name")
    role: SMCCRole
    email: Optional[str] = Field(None, description="Email address")
    department: Optional[str] = Field(None, description="Department/Program")

class Evaluation(BaseModel):
    """
    Evaluation records for teachers
    Collection: "evaluation"
    """
    evaluator_name: str
    evaluator_role: SMCCRole
    teacher_name: str
    course: str
    section: Optional[str] = None
    term: Optional[str] = None

    # Core criteria scored 1-5
    teaching_effectiveness: int = Field(..., ge=1, le=5)
    classroom_management: int = Field(..., ge=1, le=5)
    content_knowledge: int = Field(..., ge=1, le=5)
    professionalism: int = Field(..., ge=1, le=5)

    comments: Optional[str] = None

class EvaluationResponse(BaseModel):
    id: str
    overall_score: float

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint (if provided)
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
