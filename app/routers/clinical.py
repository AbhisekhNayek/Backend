from fastapi import APIRouter, HTTPException, Depends, Response, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId

from app.database import db
from app.middlewares.auth import get_current_user
from app.utils.pdf import generate_prescription_pdf, generate_visit_report_pdf

router = APIRouter(prefix="/api/clinical", tags=["Clinical"])

class MedicationRequest(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str
    instructions: Optional[str] = None

class CreatePrescriptionRequest(BaseModel):
    bookingId: str
    medications: List[MedicationRequest]
    advice: Optional[str] = None
    nextFollowUp: Optional[str] = None

class VitalsRequest(BaseModel):
    temperature: Optional[str] = None
    bloodPressure: Optional[str] = None
    pulseRate: Optional[str] = None
    spO2: Optional[str] = None
    weight: Optional[str] = None

class CreateVisitReportRequest(BaseModel):
    bookingId: str
    vitals: VitalsRequest
    chiefComplaints: Optional[str] = None
    diagnosis: Optional[str] = None
    observations: Optional[str] = None

@router.post("/prescription", status_code=status.HTTP_201_CREATED)
async def create_prescription(payload: CreatePrescriptionRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        doctor_id = current_user["id"]
        
        booking = await db.bookings.find_one({"_id": ObjectId(payload.bookingId)})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        prescription_doc = {
            "bookingId": ObjectId(payload.bookingId),
            "patientId": booking["userId"],
            "doctorId": ObjectId(doctor_id),
            "medications": [med.model_dump() for med in payload.medications],
            "advice": payload.advice,
            "nextFollowUp": payload.nextFollowUp,
            "created_at": datetime.utcnow()
        }

        await db.prescriptions.insert_one(prescription_doc)
        
        # Serialize fields
        prescription_doc["_id"] = str(prescription_doc["_id"])
        prescription_doc["bookingId"] = str(prescription_doc["bookingId"])
        prescription_doc["patientId"] = str(prescription_doc["patientId"])
        prescription_doc["doctorId"] = str(prescription_doc["doctorId"])
        if prescription_doc.get("created_at"):
            prescription_doc["created_at"] = prescription_doc["created_at"].isoformat()

        return {"success": True, "prescription": prescription_doc}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prescription/pdf/{id}")
async def get_prescription_pdf_endpoint(id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        prescription = await db.prescriptions.find_one({"_id": ObjectId(id)})
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")

        # Resolve Doctor Name and Patient Name
        doctor = await db.doctors.find_one({"_id": prescription["doctorId"]}, {"name": 1, "specialization": 1})
        patient = await db.users.find_one({"_id": prescription["patientId"]}, {"name": 1, "dob": 1, "gender": 1})

        doctor_name = doctor["name"] if doctor else "N/A"
        specialization = doctor.get("specialization", "N/A") if doctor else "N/A"
        patient_name = patient["name"] if patient else "N/A"
        patient_gender = patient.get("gender", "N/A") if patient else "N/A"

        patient_age = "N/A"
        if patient and patient.get("dob"):
            dob = patient["dob"]
            if isinstance(dob, datetime):
                patient_age = str(datetime.utcnow().year - dob.year)
            elif isinstance(dob, str):
                try:
                    dob_dt = datetime.fromisoformat(dob.replace("Z", "+00:00"))
                    patient_age = str(datetime.utcnow().year - dob_dt.year)
                except ValueError:
                    pass

        pdf_bytes = generate_prescription_pdf({
            "doctorName": doctor_name,
            "specialization": specialization,
            "patientName": patient_name,
            "patientAge": patient_age,
            "patientGender": patient_gender,
            "medications": prescription.get("medications", []),
            "advice": prescription.get("advice", "")
        })

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=prescription-{id}.pdf"
            }
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/visit-report", status_code=status.HTTP_201_CREATED)
async def create_visit_report(payload: CreateVisitReportRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        provider_id = current_user["id"]
        provider_type = current_user.get("role", "DOCTOR")

        booking = await db.bookings.find_one({"_id": ObjectId(payload.bookingId)})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        report_doc = {
            "bookingId": ObjectId(payload.bookingId),
            "patientId": booking["userId"],
            "providerId": ObjectId(provider_id),
            "providerType": provider_type,
            "vitals": payload.vitals.model_dump(),
            "chiefComplaints": payload.chiefComplaints,
            "diagnosis": payload.diagnosis,
            "observations": payload.observations,
            "created_at": datetime.utcnow()
        }

        await db.visit_reports.insert_one(report_doc)
        
        # Serialize fields
        report_doc["_id"] = str(report_doc["_id"])
        report_doc["bookingId"] = str(report_doc["bookingId"])
        report_doc["patientId"] = str(report_doc["patientId"])
        report_doc["providerId"] = str(report_doc["providerId"])
        if report_doc.get("created_at"):
            report_doc["created_at"] = report_doc["created_at"].isoformat()

        return {"success": True, "report": report_doc}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/visit-report/pdf/{id}")
async def get_visit_report_pdf_endpoint(id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        report = await db.visit_reports.find_one({"_id": ObjectId(id)})
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        patient = await db.users.find_one({"_id": report["patientId"]}, {"name": 1})
        patient_name = patient["name"] if patient else "N/A"

        pdf_bytes = generate_visit_report_pdf({
            "patientName": patient_name,
            "vitals": report.get("vitals", {}),
            "chiefComplaints": report.get("chiefComplaints", ""),
            "diagnosis": report.get("diagnosis", ""),
            "observations": report.get("observations", "")
        })

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=visit-report-{id}.pdf"
            }
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
