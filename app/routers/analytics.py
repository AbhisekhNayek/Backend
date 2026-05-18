from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List
from datetime import datetime

from app.database import db
from app.middlewares.auth import admin_only

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/revenue")
async def get_revenue(admin: Dict[str, Any] = Depends(admin_only)):
    try:
        pipeline = [
            {"$match": {"status": "SUCCESS"}},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "totalRevenue": {"$sum": "$totalAmount"},
                    "platformFees": {"$sum": "$platformFee"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        cursor = db.payments.aggregate(pipeline)
        stats = await cursor.to_list(length=1000)
        return {"success": True, "data": stats}
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.get("/growth")
async def get_growth(admin: Dict[str, Any] = Depends(admin_only)):
    try:
        # Users aggregate
        user_pipeline = [
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        u_cursor = db.users.aggregate(user_pipeline)
        user_stats = await u_cursor.to_list(length=1000)

        # Doctors aggregate
        doc_pipeline = [
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        d_cursor = db.doctors.aggregate(doc_pipeline)
        doctor_stats = await d_cursor.to_list(length=1000)

        return {
            "success": True,
            "data": {
                "users": user_stats,
                "doctors": doctor_stats
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.get("/heatmap")
async def get_heatmap(admin: Dict[str, Any] = Depends(admin_only)):
    try:
        # Fetch completed bookings and map coordinates
        pipeline = [
            {"$match": {"status": "COMPLETED"}},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "userId",
                    "foreignField": "_id",
                    "as": "user"
                }
            },
            {"$unwind": "$user"}
        ]
        cursor = db.bookings.aggregate(pipeline)
        bookings = await cursor.to_list(length=2000)

        heatmap_data = []
        for b in bookings:
            user_doc = b.get("user", {})
            location = user_doc.get("location", {})
            if location and location.get("latitude") is not None and location.get("longitude") is not None:
                heatmap_data.append({
                    "lat": location["latitude"],
                    "lng": location["longitude"]
                })

        return {"success": True, "data": heatmap_data}
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

