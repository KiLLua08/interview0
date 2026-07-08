"""User document types used by the accounts domain."""

from typing import TypedDict

from bson import ObjectId


class UserDocument(TypedDict, total=False):
    """MongoDB representation of an application user."""

    _id: ObjectId
    email: str
    full_name: str
    password_hash: str
    created_at: str
    updated_at: str

