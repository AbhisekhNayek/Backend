from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from bson import ObjectId

from app.database import db
from app.middlewares.auth import admin_only

router = APIRouter(prefix="/api/system", tags=["System"])

class BannerRequest(BaseModel):
    imageUrl: str
    actionUrl: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None

class ConfigRequest(BaseModel):
    key: str
    value: Any

class AnnouncementRequest(BaseModel):
    title: str
    content: str
    role: str = "ALL"  # ALL, DOCTOR, NURSE, PATIENT
    expiresAt: Optional[str] = None

@router.get("/banners")
async def get_banners(admin: Dict[str, Any] = Depends(admin_only)):
    try:
        cursor = db.banners.find().sort("created_at", -1)
        banners = await cursor.to_list(length=1000)
        for b in banners:
            b["_id"] = str(b["_id"])
            if b.get("created_at"):
                b["created_at"] = b["created_at"].isoformat()
        return {"success": True, "data": banners}
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.post("/banners", status_code=status.HTTP_201_CREATED)
async def create_banner(payload: BannerRequest, admin: Dict[str, Any] = Depends(admin_only)):
    try:
        banner_doc = payload.model_dump()
        banner_doc["created_at"] = datetime.now(timezone.utc)
        await db.banners.insert_one(banner_doc)
        banner_doc["_id"] = str(banner_doc["_id"])
        banner_doc["created_at"] = banner_doc["created_at"].isoformat()
        return {"success": True, "data": banner_doc}
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.delete("/banners/{id}")
async def delete_banner(id: str, admin: Dict[str, Any] = Depends(admin_only)):
    try:
        res = await db.banners.delete_one({"_id": ObjectId(id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Banner not found")
        return {"success": True, "message": "Banner deleted successfully"}
    except HTTPException as he:
        raise he
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.get("/config/{key}")
async def get_config(key: str, admin: Dict[str, Any] = Depends(admin_only)):
    try:
        config = await db.system_configs.find_one({"key": key})
        if config:
            config["_id"] = str(config["_id"])
            if config.get("created_at"):
                config["created_at"] = config["created_at"].isoformat()
            if config.get("updated_at"):
                config["updated_at"] = config["updated_at"].isoformat()
        return {"success": True, "data": config}
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.post("/config")
async def update_config(payload: ConfigRequest, admin: Dict[str, Any] = Depends(admin_only)):
    try:
        config = await db.system_configs.find_one_and_update(
            {"key": payload.key},
            {"$set": {
                "value": payload.value,
                "updated_at": datetime.now(timezone.utc)
            }},
            upsert=True,
            return_document=True
        )
        config["_id"] = str(config["_id"])
        if config.get("created_at"):
            config["created_at"] = config["created_at"].isoformat()
        if config.get("updated_at"):
            config["updated_at"] = config["updated_at"].isoformat()
        return {"success": True, "data": config}
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.get("/config")
async def get_all_config(admin: Dict[str, Any] = Depends(admin_only)):
    try:
        cursor = db.system_configs.find()
        configs = await cursor.to_list(length=1000)
        config_dict = {}
        for c in configs:
            config_dict[c["key"]] = c["value"]
        return {"success": True, "config": config_dict}
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.put("/config")
async def update_all_config(payload: Dict[str, Any], admin: Dict[str, Any] = Depends(admin_only)):
    try:
        for k, v in payload.items():
            await db.system_configs.find_one_and_update(
                {"key": k},
                {"$set": {
                    "value": v,
                    "updated_at": datetime.now(timezone.utc)
                }},
                upsert=True
            )
        return {"success": True, "message": "Configuration updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.get("/announcements")
async def get_announcements(admin: Dict[str, Any] = Depends(admin_only)):
    try:
        now = datetime.now(timezone.utc)
        # Find announcements that have not expired
        cursor = db.announcements.find({
            "$or": [
                {"expiresAt": {"$exists": False}},
                {"expiresAt": {"$eq": None}},
                {"expiresAt": {"$gt": now}}
            ]
        }).sort("created_at", -1)
        announcements = await cursor.to_list(length=1000)

        for a in announcements:
            a["_id"] = str(a["_id"])
            if a.get("created_at"):
                a["created_at"] = a["created_at"].isoformat()
            if a.get("expiresAt"):
                a["expiresAt"] = a["expiresAt"].isoformat()

        return {"success": True, "data": announcements}
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.post("/announcements", status_code=status.HTTP_201_CREATED)
async def create_announcement(payload: AnnouncementRequest, admin: Dict[str, Any] = Depends(admin_only)):
    try:
        ann_doc = payload.model_dump()
        ann_doc["created_at"] = datetime.now(timezone.utc)
        if ann_doc.get("expiresAt"):
            try:
                ann_doc["expiresAt"] = datetime.fromisoformat(ann_doc["expiresAt"].replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid expiresAt ISO format")
        
        await db.announcements.insert_one(ann_doc)
        
        ann_doc["_id"] = str(ann_doc["_id"])
        ann_doc["created_at"] = ann_doc["created_at"].isoformat()
        if ann_doc.get("expiresAt"):
            ann_doc["expiresAt"] = ann_doc["expiresAt"].isoformat()

        return {"success": True, "data": ann_doc}
    except HTTPException as he:
        raise he
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

