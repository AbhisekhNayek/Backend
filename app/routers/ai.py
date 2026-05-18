from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import re
from bson import ObjectId

from app.database import db
from app.middlewares.auth import get_current_user

router = APIRouter(prefix="/api/ai", tags=["AI Hub"])

class AIChatRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None

class PinkChatRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None

# Symptom-to-Specialist mapping for Recommendation Cards
SYMPTOM_MAP = [
    (r"stomach|tummy|abdomen|indigestion|acid|vomit", "Gastroenterologist", "Gastroenterology"),
    (r"head|migraine|headache|dizzy|seizure|numbness", "Neurologist", "Neurology"),
    (r"heart|chest pain|palpitation|breathless|bp|cardiac", "Cardiologist", "Cardiology"),
    (r"fever|cough|cold|flu|infection|weakness", "General Physician", "General Medicine"),
    (r"skin|rash|itch|acne|hair|psoriasis", "Dermatologist", "Dermatology"),
    (r"bone|joint|fracture|muscle|back pain|neck pain", "Orthopedist", "Orthopedics"),
    (r"depressed|anxious|mental|sleep|stress|sad", "Psychiatrist", "Psychiatry"),
    (r"sugar|diabetes|thyroid|hormone|obese", "Endocrinologist", "Endocrinology")
]

def check_symptoms(message: str) -> Optional[Dict[str, str]]:
    msg_clean = message.lower()
    for pattern, specialist, spec_code in SYMPTOM_MAP:
        if re.search(pattern, msg_clean):
            return {
                "specialist": specialist,
                "specialization": spec_code,
                "title": f"Recommended: Book a {specialist} near you.",
                "subtitle": f"Based on your symptoms, a consult with a specialist in {spec_code} is recommended."
            }
    return None

@router.post("/chat")
async def general_chat(payload: AIChatRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    user_id = current_user["id"]
    message = payload.message
    
    # 1. Look up or create session
    session_id = payload.sessionId
    session = None
    if session_id:
        try:
            session = await db.ai_sessions.find_one({"_id": ObjectId(session_id), "userId": user_id})
        except Exception:
            pass

    if not session:
        session_doc = {
            "userId": user_id,
            "sessionType": "GENERAL_CHAT",
            "history": [],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        res = await db.ai_sessions.insert_one(session_doc)
        session_id = str(res.inserted_id)
        session = session_doc
    else:
        session_id = str(session["_id"])

    # 2. Heuristic smart response (mimics dynamic AI processing)
    rec_card = check_symptoms(message)
    
    if rec_card:
        ai_response = (
            f"I have recorded your symptoms regarding '{message}'. It is important to monitor these signs. "
            f"Since these symptoms can be associated with underlying issues, consulting a specialized "
            f"{rec_card['specialist']} is highly recommended for a thorough physical evaluation."
        )
    else:
        ai_response = (
            "Thank you for sharing. Please maintain proper hydration, get adequate rest, and monitor your symptoms. "
            "If you experience any sudden discomfort, severe pain, or fever, please schedule a visit with a medical professional."
        )

    # 3. Save to history
    new_history = session.get("history", [])
    new_history.append({"role": "user", "content": message, "timestamp": datetime.utcnow()})
    new_history.append({"role": "model", "content": ai_response, "timestamp": datetime.utcnow()})
    
    await db.ai_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {
            "history": new_history,
            "updatedAt": datetime.utcnow()
        }}
    )

    return {
        "success": True,
        "sessionId": session_id,
        "response": ai_response,
        "recommendationCard": rec_card
    }

@router.post("/analyze-report")
async def analyze_report(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        filename = file.filename.lower()
        file_content = await file.read()
        
        # 1. OCR Mockup analysis - parse filename & content length to trigger different mock clinical reports
        report_text = ""
        abnormalities = []
        specialist = "General Physician"
        otc_medicines = []
        
        if "cbc" in filename or "blood" in filename or len(file_content) % 3 == 0:
            report_text = "Complete Blood Count (CBC) Panel. Hemoglobin: 11.2 g/dL (Low, normal: 12-16). WBC: 10,500/mcL (Normal)."
            abnormalities.append({
                "parameter": "Hemoglobin",
                "value": "11.2 g/dL",
                "status": "LOW",
                "explanation": "Low hemoglobin levels indicate mild anemia, which can cause fatigue and weakness."
            })
            otc_medicines = ["Iron Supplements", "Vitamin B12", "Folic Acid"]
            specialist = "Hematologist"
        elif "lipid" in filename or "cholesterol" in filename or len(file_content) % 3 == 1:
            report_text = "Lipid Profile Panel. Total Cholesterol: 245 mg/dL (High, normal: <200). HDL: 42 mg/dL (Normal). LDL: 165 mg/dL (High, normal: <100)."
            abnormalities.append({
                "parameter": "Total Cholesterol",
                "value": "245 mg/dL",
                "status": "HIGH",
                "explanation": "Elevated cholesterol levels increase the risk of plaque build-up in arteries. Dietary modifications are advised."
            })
            abnormalities.append({
                "parameter": "LDL Cholesterol",
                "value": "165 mg/dL",
                "status": "HIGH",
                "explanation": "High bad cholesterol (LDL) increases cardiovascular risk."
            })
            otc_medicines = ["Omega-3 Fish Oil", "Coenzyme Q10"]
            specialist = "Cardiologist"
        else:
            # Thyroid or general
            report_text = "Thyroid Function Test. TSH: 5.8 mIU/L (High, normal: 0.4-4.0). Free T4: 1.1 ng/dL (Normal)."
            abnormalities.append({
                "parameter": "TSH (Thyroid Stimulating Hormone)",
                "value": "5.8 mIU/L",
                "status": "HIGH",
                "explanation": "Mildly elevated TSH indicates a borderline underactive thyroid (subclinical hypothyroidism)."
            })
            otc_medicines = ["Selenium Supplements", "Vitamin D3"]
            specialist = "Endocrinologist"

        ai_explanation = (
            f"The report analysis reveals {len(abnormalities)} abnormal values. "
            f"Most notably, your {abnormalities[0]['parameter']} is currently flagged as {abnormalities[0]['status']}. "
            f"We suggest discussing these values with a {specialist} to decide if formal prescription medication is required."
        )

        return {
            "success": True,
            "reportName": file.filename,
            "detectedText": report_text,
            "abnormalities": abnormalities,
            "aiExplanation": ai_explanation,
            "otcSuggestions": otc_medicines,
            "recommendedSpecialist": specialist
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pink-chat")
async def pink_chat(payload: PinkChatRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    user_id = current_user["id"]
    message = payload.message
    
    session_id = payload.sessionId
    session = None
    if session_id:
        try:
            session = await db.ai_sessions.find_one({"_id": ObjectId(session_id), "userId": user_id})
        except Exception:
            pass

    if not session:
        session_doc = {
            "userId": user_id,
            "sessionType": "PINK_MODE",
            "history": [],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        res = await db.ai_sessions.insert_one(session_doc)
        session_id = str(res.inserted_id)
        session = session_doc
    else:
        session_id = str(session["_id"])

    # Female-centric empathetic helper responses
    msg_clean = message.lower()
    if any(k in msg_clean for k in ["period", "cycle", "cramp", "pain", "menstruation"]):
        ai_response = (
            "Cycles can definitely be tough. Make sure to stay warm, drink plenty of warm liquids "
            "(like chamomile or ginger tea), and avoid intensive physical stress. If your cramps are severe, "
            "gentle heat therapy or mild over-the-counter anti-inflammatories can help. Remember, your body "
            "is doing incredible work—give yourself some loving care today!"
        )
    elif "package" in msg_clean or "free" in msg_clean:
        ai_response = (
            "Our Pink Care Package contains organic sanitary pads, soothing herbal tea bags, warm cramp patches, "
            "and wellness journals! Your first care package is 100% free when you log your first menstrual cycle "
            "on the tracker. Would you like me to walk you through logging your cycle?"
        )
    else:
        ai_response = (
            "I'm here to support you in every aspect of your reproductive and hormonal health journey. "
            "Whether you want to understand cycle patterns, log symptoms, or discuss wellness packages, "
            "please know this is a safe, completely private space."
        )

    # Save to history
    new_history = session.get("history", [])
    new_history.append({"role": "user", "content": message, "timestamp": datetime.utcnow()})
    new_history.append({"role": "model", "content": ai_response, "timestamp": datetime.utcnow()})
    
    await db.ai_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {
            "history": new_history,
            "updatedAt": datetime.utcnow()
        }}
    )

    return {
        "success": True,
        "sessionId": session_id,
        "response": ai_response
    }
