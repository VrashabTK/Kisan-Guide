from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
from backend.app.core.security import get_current_user_id
from backend.app.schemas import SavedItemCreate
from backend.app.services.firebase_service import (
    save_item,
    get_saved_items,
    delete_saved_item
)

router = APIRouter(prefix="/saved", tags=["Saved & Bookmarks"])

@router.post("")
async def create_saved_item(
    payload: SavedItemCreate,
    uid: str = Depends(get_current_user_id)
):
    saved = await save_item(uid, payload.model_dump())
    return saved

@router.get("")
async def list_saved_items(
    category: Optional[str] = Query(None, description="Category filter"),
    uid: str = Depends(get_current_user_id)
):
    items = await get_saved_items(uid, category=category)
    return items

@router.delete("/{saved_item_id}")
async def remove_saved_item(
    saved_item_id: str,
    uid: str = Depends(get_current_user_id)
):
    success = await delete_saved_item(uid, saved_item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Saved item not found")
    return {"success": True, "message": "Item removed from bookmarks"}
