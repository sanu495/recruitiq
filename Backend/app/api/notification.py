from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from Backend.app.core.database import get_session
from Backend.app.core.security import get_current_user
from Backend.app.core.genericdal import GenericDal
from Backend.app.Schema.schema import Notification, User
from Backend.app.Models.models import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

# ── Get My Notifications ───────────────────────────────────────────────────────

@router.get("", response_model=List[NotificationOut])
def get_notification(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Returns latest 50 notifications for current user."""
    notifs = session.exec(select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(50)).all()
    return notifs

# ── Unread Count (for bell icon badge) ────────────────────────────────────────

@router.get("/unread-count")
def unread_count(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Returns count of unread notifications — used for bell badge in UI."""
    notifs = session.exec(select(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False)).all()
    return {"unread_count": len(notifs)}

# ── Mark All as Read ───────────────────────────────────────────────────────────

@router.patch("/mark-all-read")
def mark_all_read(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    notifs = session.exec(select(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False)).all()
    dal = GenericDal(Notification, session)

    for notif in notifs:
        dal.update(notif.id, {"is_read":True})

    return {"message":f"{len(notifs)} notification marked as read"}

# ── Mark Single Notification as Read ──────────────────────────────────────────

@router.patch("/{notif_id}/read")
def mark_read(notif_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    dal = GenericDal(Notification, session)
    notif = dal.get(notif_id)

    # Only the owner can mark it read
    if notif.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your notification")
    
    dal.update(notif_id, {"is_read":True})
    return {"message":"Marked as read"}

# ── Delete a Notification ──────────────────────────────────────────────────────
@router.delete("/{notif_id}")
def delete_notifications(notif_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    dal = GenericDal(Notification, session)
    notif = dal.get(notif_id)

    if notif.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your notification")
    
    dal.delete(notif_id)
    return {"message":"Notification deleted"}







