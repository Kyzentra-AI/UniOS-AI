from typing import List
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.chat import ConversationResponse, ConversationCreate
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin
from app.core.kie_client import process_memory_context_mock

router = APIRouter(prefix="/api/v1/chat", tags=["Chat & Continuity"])

@router.get("/history", response_model=List[ConversationResponse])
async def get_chat_history(session_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        res = supabase_admin.table("conversations").select("*").eq("user_id", user_id).eq("session_id", session_id).order("timestamp", desc=False).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/message")
async def send_message(msg: ConversationCreate, current_user: dict = Depends(get_current_user)):
    """
    Saves the user message, triggers mock KIE response, and processes memory context.
    """
    user_id = current_user["user_id"]
    try:
        # Save user message
        supabase_admin.table("conversations").insert({
            "user_id": user_id,
            "session_id": msg.session_id,
            "message_role": "user",
            "content": msg.content
        }).execute()
        
        # Mock AI Response
        ai_reply = "This is a mock response from KIE."
        supabase_admin.table("conversations").insert({
            "user_id": user_id,
            "session_id": msg.session_id,
            "message_role": "ai",
            "content": ai_reply
        }).execute()
        
        # Trigger async memory context extraction in background (mocked synchronously for simplicity here)
        recent_chat = [
            {"role": "user", "content": msg.content},
            {"role": "ai", "content": ai_reply}
        ]
        await process_memory_context_mock(recent_chat)
        
        return {"status": "success", "reply": ai_reply}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
