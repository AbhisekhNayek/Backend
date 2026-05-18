from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId

from app.database import db
from app.services.socket import socket_service

class ChatService:
    async def get_history(self, user_id: str, partner_id: str) -> List[Dict[str, Any]]:
        cursor = db.messages.find({
            "$or": [
                {"sender": ObjectId(user_id), "receiver": ObjectId(partner_id)},
                {"sender": ObjectId(partner_id), "receiver": ObjectId(user_id)}
            ]
        }).sort("createdAt", 1)
        messages = await cursor.to_list(length=1000)
        for msg in messages:
            msg["_id"] = str(msg["_id"])
            msg["sender"] = str(msg["sender"])
            msg["receiver"] = str(msg["receiver"])
        return messages

    async def send_message(self, sender_id: str, receiver_id: str, text: Optional[str] = None, attachments: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        msg_doc = {
            "sender": ObjectId(sender_id),
            "receiver": ObjectId(receiver_id),
            "text": text,
            "attachments": attachments or [],
            "isRead": False,
            "chatType": "DOCTOR_PATIENT",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        await db.messages.insert_one(msg_doc)
        
        # Serialize for json & socket
        msg_doc["_id"] = str(msg_doc["_id"])
        msg_doc["sender"] = str(msg_doc["sender"])
        msg_doc["receiver"] = str(msg_doc["receiver"])
        if msg_doc.get("createdAt"):
            msg_doc["createdAt"] = msg_doc["createdAt"].isoformat()
        if msg_doc.get("updatedAt"):
            msg_doc["updatedAt"] = msg_doc["updatedAt"].isoformat()

        # Socket emit (await the async emit)
        await socket_service.emit_to_user(receiver_id, "new_message", msg_doc)

        return msg_doc

    async def get_recent_chats(self, user_id: str) -> List[Dict[str, Any]]:
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"sender": ObjectId(user_id)},
                        {"receiver": ObjectId(user_id)}
                    ]
                }
            },
            {"$sort": {"createdAt": -1}},
            {
                "$group": {
                    "_id": {
                        "$cond": [
                            {"$eq": ["$sender", ObjectId(user_id)]},
                            "$receiver",
                            "$sender"
                        ]
                    },
                    "lastMessage": {"$first": "$$ROOT"}
                }
            },
            {"$limit": 20}
        ]

        cursor = db.messages.aggregate(pipeline)
        recent_messages = await cursor.to_list(length=20)

        populated_chats = []
        for chat in recent_messages:
            partner_id = chat["_id"]
            if not partner_id:
                continue

            # Find partner in users or doctors
            partner = await db.users.find_one({"_id": partner_id}, {"name": 1, "profileImage": 1, "profilePic": 1})
            if not partner:
                partner = await db.doctors.find_one({"_id": partner_id}, {"name": 1, "profileImage": 1})

            if partner:
                partner["_id"] = str(partner["_id"])
                # Map profilePic to profileImage if needed for front-end consistency
                if "profilePic" in partner and "profileImage" not in partner:
                    partner["profileImage"] = partner["profilePic"]

            last_msg = chat["lastMessage"]
            last_msg["_id"] = str(last_msg["_id"])
            last_msg["sender"] = str(last_msg["sender"])
            last_msg["receiver"] = str(last_msg["receiver"])
            if last_msg.get("createdAt"):
                last_msg["createdAt"] = last_msg["createdAt"].isoformat()
            if last_msg.get("updatedAt"):
                last_msg["updatedAt"] = last_msg["updatedAt"].isoformat()

            populated_chats.append({
                "user": partner,
                "lastMessage": last_msg
            })

        return populated_chats

chat_service = ChatService()
