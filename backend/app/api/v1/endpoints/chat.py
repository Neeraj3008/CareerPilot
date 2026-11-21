from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.models import User, Conversation, Message
from app.schemas.schemas import ChatMessageCreate, ChatResponse, ConversationResponse, MessageResponse
from app.services.agent import run_agent_turn

router = APIRouter()

@router.post("/", response_model=ChatResponse)
def chat_with_agent(
    chat_in: ChatMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Find or create conversation
    conv = None
    if chat_in.conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == chat_in.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

    if not conv:
        # Create title from first message
        title_snippet = chat_in.message[:35] + ("..." if len(chat_in.message) > 35 else "")
        conv = Conversation(user_id=current_user.id, title=title_snippet)
        db.add(conv)
        db.flush()

    # Save user message
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=chat_in.message
    )
    db.add(user_msg)
    db.commit()

    # Run agent turn with genuine tool execution
    agent_output = run_agent_turn(db, current_user, conv.id, chat_in.message)

    # Save assistant message
    asst_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=agent_output["reply"],
        tool_calls=agent_output["tool_calls_executed"]
    )
    db.add(asst_msg)
    db.commit()

    return {
        "conversation_id": conv.id,
        "reply": agent_output["reply"],
        "tool_calls_executed": agent_output["tool_calls_executed"]
    }

@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()

@router.get("/conversations/{conv_id}", response_model=ConversationResponse)
def get_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conv
