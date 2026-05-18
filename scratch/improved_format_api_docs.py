import json
import os

def resolve_schema(schema_ref, schemas, visited=None):
    if visited is None:
        visited = set()
    if not schema_ref:
        return {}
    if "$ref" in schema_ref:
        ref = schema_ref["$ref"]
        if ref in visited:
            return {}  # Avoid circular refs
        visited.add(ref)
        ref_name = ref.split("/")[-1]
        resolved = resolve_schema(schemas.get(ref_name, {}), schemas, visited)
        visited.remove(ref)
        return resolved
    if "anyOf" in schema_ref:
        non_null_subschemas = [s for s in schema_ref["anyOf"] if resolve_schema(s, schemas, visited).get("type") != "null"]
        if non_null_subschemas:
            return resolve_schema(non_null_subschemas[0], schemas, visited)
    return schema_ref

def build_mock_body(schema, schemas, visited_schemas=None):
    if visited_schemas is None:
        visited_schemas = set()
    
    resolved = resolve_schema(schema, schemas)
    
    schema_title = resolved.get("title")
    if schema_title:
        if schema_title in visited_schemas:
            return f"<{schema_title} (circular reference)>"
        visited_schemas.add(schema_title)
        
    p_type = resolved.get("type", "object")
    
    if "properties" in resolved and p_type != "object":
        p_type = "object"
        
    if p_type == "object":
        obj = {}
        for k, prop in resolved.get("properties", {}).items():
            res_prop = resolve_schema(prop, schemas)
            p_t = res_prop.get("type")
            
            if "properties" in res_prop and not p_t:
                p_t = "object"
                
            if p_t == "string":
                if "format" in res_prop and res_prop["format"] == "date-time":
                    obj[k] = "2026-05-18T23:15:00Z"
                elif "email" in k:
                    obj[k] = "user@docton.com"
                elif "dob" in k:
                    obj[k] = "1995-08-15"
                elif "phone" in k:
                    obj[k] = "+1234567890"
                elif "avatar" in k or "image" in k or "url" in k or "document" in k:
                    obj[k] = "https://example.com/assets/file.jpg"
                else:
                    obj[k] = "string"
            elif p_t == "number" or p_t == "integer":
                obj[k] = 0 if p_t == "integer" else 0.0
            elif p_t == "boolean":
                obj[k] = True
            elif p_t == "array":
                items_schema = res_prop.get("items", {})
                obj[k] = [build_mock_body(items_schema, schemas, visited_schemas.copy())]
            elif p_t == "object" or "properties" in res_prop:
                obj[k] = build_mock_body(res_prop, schemas, visited_schemas.copy())
            else:
                obj[k] = {}
        if schema_title:
            visited_schemas.remove(schema_title)
        return obj
        
    elif p_type == "array":
        items_schema = resolved.get("items", {})
        result = [build_mock_body(items_schema, schemas, visited_schemas.copy())]
        if schema_title:
            visited_schemas.remove(schema_title)
        return result
        
    elif p_type == "string":
        if schema_title:
            visited_schemas.remove(schema_title)
        return "string"
        
    elif p_type in ["number", "integer"]:
        val = 0 if p_type == "integer" else 0.0
        if schema_title:
            visited_schemas.remove(schema_title)
        return val
        
    elif p_type == "boolean":
        if schema_title:
            visited_schemas.remove(schema_title)
        return True
        
    if schema_title:
        visited_schemas.remove(schema_title)
    return {}

def format_property_type(prop, schemas):
    p_schema = resolve_schema(prop, schemas)
    p_type = p_schema.get("type", "any")
    
    if "anyOf" in prop:
        sub_types = [format_property_type(sub, schemas) for sub in prop["anyOf"] if resolve_schema(sub, schemas).get("type") != "null"]
        return " | ".join(sub_types)
    if "enum" in p_schema:
        return f"enum ({', '.join([repr(e) for e in p_schema['enum']])})"
    if p_type == "array":
        items = p_schema.get("items", {})
        return f"array of {format_property_type(items, schemas)}"
    return p_type

def get_custom_success_response(path, method, operation_id):
    path = path.strip()
    method = method.upper()
    
    # 1. Auth routes
    if path in ["/api/auth/register", "/api/auth/login", "/api/users/login"]:
        return {
            "success": True,
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY0NTY3OGFkOWYxMmUzNDU2Nzg5MGFiYyIsInJvbGUiOiJQQVRJRU5UIn0.signature",
            "role": "PATIENT" if "users" in path else "DOCTOR",
            "id": "645678ad9f12e34567890abc"
        }
    
    if path == "/api/users/verify-otp":
        return {
            "success": True,
            "message": "Email verified successfully"
        }
        
    if path == "/api/users/quick-fill":
        return {
            "success": True,
            "message": "Onboarding completed successfully"
        }
        
    if path == "/api/users/me":
        return {
            "success": True,
            "user": {
                "id": "645678ad9f12e34567890abc",
                "name": "Jane Doe",
                "email": "user@docton.com",
                "phone": "+1234567890",
                "gender": "female",
                "dob": "1995-08-15",
                "role": "PATIENT",
                "isEmailVerified": True,
                "isPhoneVerified": True,
                "address": {
                    "line1": "123 Main St",
                    "line2": "Apt 4B",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "country": "India",
                    "pincode": "400001"
                },
                "location": {
                    "latitude": 19.0760,
                    "longitude": 72.8777
                }
            }
        }
        
    if path == "/api/users/":
        return {
            "success": True,
            "count": 1,
            "data": [
                {
                    "id": "645678ad9f12e34567890abc",
                    "name": "Jane Doe",
                    "email": "user@docton.com",
                    "phone": "+1234567890",
                    "gender": "female",
                    "dob": "1995-08-15",
                    "role": "PATIENT",
                    "isEmailVerified": True,
                    "isBlocked": False,
                    "isDeleted": False
                }
            ]
        }
        
    if path == "/api/users/register":
        return {
            "success": True,
            "message": "User registered. OTP sent to email."
        }
        
    # 2. Doctors routes
    if path == "/api/doctors/availability":
        return {
            "success": True,
            "message": "Availability updated successfully"
        }
        
    if path == "/api/doctors/incoming-call":
        return {
            "success": True,
            "message": "Call notification initiated"
        }
        
    if path == "/api/doctors/login":
        return {
            "success": True,
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY0NTY3OGFkOWYxMmUzNDU2Nzg5MWRlZiIsInJvbGUiOiJET0NUT1IifQ.signature"
        }
        
    if path == "/api/doctors/":
        return {
            "success": True,
            "count": 1,
            "data": [
                {
                    "id": "645678ad9f12e34567890def",
                    "name": "Dr. Sarah Smith",
                    "profileImage": "https://example.com/dr-sarah.jpg",
                    "bio": "Experienced pediatrician with 10+ years of practice.",
                    "specialization": "Pediatrics",
                    "qualifications": "MD, DNB (Pediatrics)",
                    "experience": 12,
                    "languages": ["English", "Hindi"],
                    "licenseNo": "MCI-12345",
                    "clinicName": "Sunny Pediatric Clinic",
                    "clinicAddress": "456 Park Avenue, Mumbai",
                    "isOnline": 1
                }
            ]
        }
        
    if path == "/api/doctors/{id}" and method == "PUT":
        return {
            "success": True,
            "message": "Doctor profile updated successfully"
        }
        
    if path == "/api/doctors/{id}" and method == "GET":
        return {
            "success": True,
            "doctor": {
                "id": "645678ad9f12e34567890def",
                "name": "Dr. Sarah Smith",
                "profileImage": "https://example.com/dr-sarah.jpg",
                "bio": "Experienced pediatrician with 10+ years of practice.",
                "specialization": "Pediatrics",
                "qualifications": "MD, DNB (Pediatrics)",
                "experience": 12,
                "languages": ["English", "Hindi"],
                "licenseNo": "MCI-12345",
                "clinicName": "Sunny Pediatric Clinic",
                "clinicAddress": "456 Park Avenue, Mumbai",
                "isOnline": 1
            }
        }
        
    # 3. Nurses routes
    if path == "/api/nurses/":
        return {
            "success": True,
            "count": 1,
            "nurses": [
                {
                    "id": "645678ad9f12e34567890ghi",
                    "name": "Nurse Mary Cooper",
                    "email": "mary.cooper@example.com",
                    "phone": "+1987654321",
                    "skills": "Elderly Care, Wound Dressing, Injection",
                    "experience": 8,
                    "rates": {
                        "hourly": 25.0,
                        "daily": 180.0,
                        "monthly": 3500.0
                    },
                    "location": {
                        "latitude": 19.0760,
                        "longitude": 72.8777
                    },
                    "distance_km": 0.0
                }
            ]
        }
        
    if path == "/api/nurses/{id}":
        return {
            "success": True,
            "nurse": {
                "id": "645678ad9f12e34567890ghi",
                "name": "Nurse Mary Cooper",
                "email": "mary.cooper@example.com",
                "phone": "+1987654321",
                "skills": "Elderly Care, Wound Dressing, Injection",
                "experience": 8,
                "rates": {
                    "hourly": 25.0,
                    "daily": 180.0,
                    "monthly": 3500.0
                },
                "location": {
                    "latitude": 19.0760,
                    "longitude": 72.8777
                }
            }
        }
        
    # 4. Clinical routes
    if path == "/api/clinical/prescription/pdf/{id}":
        return {
            "success": True,
            "pdfUrl": "https://storage.googleapis.com/docton-bucket/prescriptions/prescription_645678ad.pdf"
        }
        
    if path == "/api/clinical/prescription":
        return {
            "success": True,
            "message": "Prescription created successfully",
            "prescriptionId": "645678ad9f12e34567890jkl"
        }
        
    if path == "/api/clinical/visit-report/pdf/{id}":
        return {
            "success": True,
            "pdfUrl": "https://storage.googleapis.com/docton-bucket/visit-reports/visit_report_645678ad.pdf"
        }
        
    if path == "/api/clinical/visit-report":
        return {
            "success": True,
            "message": "Visit report created successfully",
            "reportId": "645678ad9f12e34567890mno"
        }
        
    # 5. Financial routes
    if path == "/api/financial/earnings":
        return {
            "success": True,
            "summary": {
                "totalEarnings": 1500.0,
                "totalWithdrawn": 1200.0,
                "pendingWithdrawal": 100.0,
                "currentBalance": 200.0
            },
            "withdrawals": [
                {
                    "id": "645678ad9f12e34567890pqr",
                    "providerId": "645678ad9f12e34567890def",
                    "amount": 1200.0,
                    "status": "APPROVED",
                    "bankDetails": {
                        "accountNumber": "987654321098",
                        "ifscCode": "HDFC0000123",
                        "bankName": "HDFC Bank",
                        "accountHolderName": "Dr. Sarah Smith"
                    },
                    "created_at": "2026-05-10T10:00:00Z",
                    "updated_at": "2026-05-10T12:00:00Z"
                }
            ]
        }
        
    if path == "/api/financial/withdraw":
        return {
            "success": True,
            "withdrawal": {
                "id": "645678ad9f12e34567890stu",
                "providerId": "645678ad9f12e34567890def",
                "providerType": "DOCTOR",
                "amount": 100.0,
                "status": "PENDING",
                "bankDetails": {
                    "accountNumber": "987654321098",
                    "ifscCode": "HDFC0000123",
                    "bankName": "HDFC Bank",
                    "accountHolderName": "Dr. Sarah Smith"
                },
                "created_at": "2026-05-18T23:15:00Z",
                "updated_at": "2026-05-18T23:15:00Z"
            }
        }
        
    if path == "/api/financial/simulate-payment":
        return {
            "success": True,
            "message": "Payment split processed successfully",
            "paymentRecord": {
                "id": "645678ad9f12e34567890vwx",
                "totalAmount": 500.0,
                "bookingId": "645678ad9f12e34567890yyy",
                "userId": "645678ad9f12e34567890abc",
                "providerId": "645678ad9f12e34567890def",
                "providerType": "DOCTOR",
                "paymentMode": "UPI",
                "providerAmount": 425.0,
                "adminAmount": 75.0,
                "status": "SUCCESS"
            }
        }
        
    # 6. Verification routes
    if path == "/api/verification/pending":
        return {
            "success": True,
            "data": [
                {
                    "id": "645678ad9f12e34567890zzz",
                    "userId": "645678ad9f12e34567890def",
                    "userRole": "DOCTOR",
                    "document": "https://example.com/assets/license.jpg",
                    "status": "PENDING",
                    "remarks": None,
                    "created_at": "2026-05-18T10:00:00Z"
                }
            ]
        }
        
    if path == "/api/verification/status/{id}":
        return {
            "success": True,
            "message": "Verification status updated successfully"
        }
        
    if path == "/api/verification/submit":
        return {
            "success": True,
            "message": "Verification documents submitted successfully"
        }
        
    # 7. Video Calling routes
    if path == "/api/video/token":
        return {
            "success": True,
            "token": "04AAAAAABBBBBBCCCCCCDDDDDD111111222222"
        }
        
    if path == "/api/video/webhook":
        return {
            "success": True,
            "message": "Webhook processed successfully"
        }
        
    # 8. Women's Health (Pink Mode)
    if path == "/api/womens-health/auto-pay":
        return {
            "success": True,
            "message": "Auto-pay setup registered successfully"
        }
        
    if path == "/api/womens-health/log":
        return {
            "success": True,
            "message": "Cycle logged successfully"
        }
        
    # 9. AI Hub
    if path == "/api/ai/analyze-report":
        return {
            "success": True,
            "analysis": "The patient report shows normal levels of hemoglobin, but slightly elevated pulse rate."
        }
        
    if path in ["/api/ai/chat", "/api/ai/pink-chat"]:
        return {
            "success": True,
            "reply": "I am Docton AI Assistant. How can I help you today?",
            "sessionId": "645678ad9f12e34567890chat"
        }
        
    # 10. Admin Controls
    if path == "/api/admin/care-packages":
        return {
            "success": True,
            "count": 1,
            "packages": [
                {
                    "id": "645678ad9f12e34567890pkg",
                    "userId": "645678ad9f12e34567890abc",
                    "type": "Maternity Kit",
                    "status": "SHIPPED",
                    "remarks": "Shipped via BlueDart",
                    "address": {
                        "line1": "123 Main St",
                        "city": "Mumbai",
                        "pincode": "400001"
                    },
                    "created_at": "2026-05-15T09:00:00Z",
                    "shipped_at": "2026-05-16T12:00:00Z"
                }
            ]
        }
        
    if path == "/api/admin/care-packages/{id}/ship":
        return {
            "success": True,
            "message": "Care package status updated to SHIPPED"
        }
        
    if path == "/api/admin/commissions":
        return {
            "success": True,
            "dashboard": {
                "totalRevenue": 15000.0,
                "adminCommission": 2250.0,
                "providerEarnings": 12750.0,
                "commissionRate": "15%"
            }
        }
        
    # 11. Analytics
    if path == "/api/analytics/growth":
        return {
            "success": True,
            "data": {
                "period": "monthly",
                "growthRate": "12.5%",
                "newUsers": 350,
                "newProviders": 45
            }
        }
        
    if path == "/api/analytics/heatmap":
        return {
            "success": True,
            "heatmap": [
                {"latitude": 19.0760, "longitude": 72.8777, "weight": 5}
            ]
        }
        
    if path == "/api/analytics/revenue":
        return {
            "success": True,
            "data": {
                "totalEarnings": 50000.0,
                "adminEarnings": 7500.0,
                "refunds": 250.0
            }
        }
        
    # 12. Chat
    if path == "/api/chat/history/{partnerId}":
        return {
            "success": True,
            "messages": [
                {
                    "id": "645678ad9f12e34567890msg1",
                    "senderId": "645678ad9f12e34567890abc",
                    "receiverId": "645678ad9f12e34567890def",
                    "text": "Hello Doctor",
                    "attachments": [],
                    "timestamp": "2026-05-18T20:00:00Z"
                }
            ]
        }
        
    if path == "/api/chat/recent":
        return {
            "success": True,
            "chats": [
                {
                    "partnerId": "645678ad9f12e34567890def",
                    "partnerName": "Dr. Sarah Smith",
                    "partnerRole": "DOCTOR",
                    "lastMessage": "Please make sure to stay hydrated.",
                    "timestamp": "2026-05-18T20:05:00Z",
                    "unreadCount": 0
                }
            ]
        }
        
    if path == "/api/chat/send":
        return {
            "success": True,
            "message": {
                "id": "645678ad9f12e34567890msg3",
                "senderId": "645678ad9f12e34567890abc",
                "receiverId": "645678ad9f12e34567890def",
                "text": "Thank you, doctor!",
                "attachments": [],
                "timestamp": "2026-05-18T23:15:00Z"
            }
        }
        
    if path == "/api/chat/token":
        return {
            "success": True,
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NDU2NzhhZDlmMTJlMzQ1Njc4OTBhYmMiLCJhcHBJZCI6IjExMTEifQ.signature"
        }
        
    # 13. System
    if path == "/api/system/announcements" and method == "GET":
        return {
            "success": True,
            "count": 1,
            "announcements": [
                {
                    "id": "645678ad9f12e34567890ann",
                    "title": "System Scheduled Maintenance",
                    "content": "Our servers will undergo routine maintenance.",
                    "role": "ALL",
                    "expiresAt": "2026-05-21T00:00:00Z",
                    "created_at": "2026-05-18T00:00:00Z"
                }
            ]
        }
        
    if path == "/api/system/announcements" and method == "POST":
        return {
            "success": True,
            "message": "Announcement created successfully"
        }
        
    if path == "/api/system/banners" and method == "GET":
        return {
            "success": True,
            "banners": [
                {
                    "id": "645678ad9f12e34567890ban",
                    "imageUrl": "https://example.com/banners/healthy-diet.jpg",
                    "actionUrl": "https://docton.com/blog/diet-tips",
                    "title": "5 Tips for a Healthy Heart",
                    "description": "Read our latest article on dietary tips for cardiovascular wellness."
                }
            ]
        }
        
    if path == "/api/system/banners" and method == "POST":
        return {
            "success": True,
            "message": "Banner created successfully"
        }
        
    if path == "/api/system/banners/{id}" and method == "DELETE":
        return {
            "success": True,
            "message": "Banner deleted successfully"
        }
        
    if path == "/api/system/config" and method == "POST":
        return {
            "success": True,
            "message": "Config parameter updated successfully"
        }
        
    if path == "/api/system/config/{key}" and method == "GET":
        return {
            "success": True,
            "key": "app_version",
            "value": "1.0.4"
        }
        
    # 14. Tasks
    if path == "/api/tasks" and method == "GET":
        return {
            "success": True,
            "tasks": [
                {
                    "id": "645678ad9f12e34567890tsk1",
                    "title": "Complete Doctor Profile",
                    "description": "Upload clinic registration and license documents.",
                    "isCompleted": False
                }
            ]
        }
        
    if path == "/api/tasks/{id}" and method == "PUT":
        return {
            "success": True,
            "message": "Task status updated successfully"
        }
        
    # 15. Tracking
    if path == "/api/tracking/admin/activities":
        return {
            "success": True,
            "activities": [
                {
                    "id": "645678ad9f12e34567890act",
                    "userId": "645678ad9f12e34567890def",
                    "role": "DOCTOR",
                    "action": "LOGIN",
                    "details": "User logged in",
                    "timestamp": "2026-05-18T23:15:00Z"
                }
            ]
        }
        
    if path == "/api/tracking/admin/history/{user_id}":
        return {
            "success": True,
            "userId": "645678ad9f12e34567890def",
            "history": [
                {
                    "latitude": 19.0760,
                    "longitude": 72.8777,
                    "timestamp": "2026-05-18T23:15:00Z"
                }
            ]
        }
        
    if path == "/api/tracking/admin/live":
        return {
            "success": True,
            "locations": [
                {
                    "userId": "645678ad9f12e34567890def",
                    "role": "DOCTOR",
                    "name": "Dr. Sarah Smith",
                    "latitude": 19.0760,
                    "longitude": 72.8777,
                    "updatedAt": "2026-05-18T23:15:00Z"
                }
            ]
        }
        
    if path == "/api/tracking/update":
        return {
            "success": True,
            "message": "Location updated successfully"
        }
        
    if path == "/":
        return {
            "success": True,
            "message": "Docton Backend is online",
            "framework": "FastAPI (Python)"
        }
        
    if path == "/api/health":
        return {
            "status": "UP",
            "database": "CONNECTED",
            "timestamp": "2026-05-18T23:15:00Z"
        }
        
    return {"success": True}

def generate_markdown():
    with open("openapi.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    md = []
    md.append("# Docton Backend API Documentation\n")
    md.append("Welcome to the complete production API specifications for the Docton backend. This document covers the comprehensive REST API endpoints, schemas, authentication scopes, and real-time live map details.\n")
    
    # Overview section
    md.append("## 📌 Global Specifications\n")
    md.append("- **Base URL**: `http://localhost:5000` (Local) / Production API Base URL")
    md.append("- **Protocol**: RESTful HTTPS with optional WebSocket endpoints")
    md.append("- **Standard Format**: JSON (`application/json` for request & response bodies)")
    md.append("- **Common Headers**:")
    md.append("  - `Content-Type: application/json`")
    md.append("  - `Authorization: Bearer <JWT_TOKEN>` (for all authenticated endpoints)\n")
    
    md.append("## 🏷️ Standard Error Responses\n")
    md.append("Every endpoint may return one of the following standard errors under invalid execution contexts:\n")
    
    md.append("### `400` Bad Request / Conflict\n")
    md.append("```json\n{\n  \"detail\": \"Error details or constraint violations\"\n}\n```\n")
    
    md.append("### `401` Unauthorized\n")
    md.append("```json\n{\n  \"detail\": \"Could not validate credentials\"\n}\n```\n")
    
    md.append("### `403` Forbidden / Permission Denied\n")
    md.append("```json\n{\n  \"detail\": \"Permission denied\"\n}\n```\n")
    
    md.append("### `404` Route Not Found\n")
    md.append("```json\n{\n  \"success\": false,\n  \"message\": \"Route not found\"\n}\n```\n")
    
    md.append("### `422` Request Validation Error\n")
    md.append("```json\n{\n  \"detail\": [\n    {\n      \"loc\": [\"body\", \"field_name\"],\n      \"msg\": \"field required\",\n      \"type\": \"value_error.missing\"\n    }\n  ]\n}\n```\n")
    
    md.append("---\n")
    
    paths = data.get("paths", {})
    components = data.get("components", {})
    schemas = components.get("schemas", {})
    
    # Group by tags
    endpoints_by_tag = {}
    for path, methods in paths.items():
        for method, info in methods.items():
            tags = info.get("tags", ["General"])
            for tag in tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append((path, method, info))

    for tag in sorted(endpoints_by_tag.keys()):
        endpoints = endpoints_by_tag[tag]
        md.append(f"## 🏷️ {tag}\n")
        
        for path, method, info in sorted(endpoints, key=lambda x: x[0]):
            summary = info.get("summary", "No summary")
            description = info.get("description", "")
            method_upper = method.upper()
            op_id = info.get("operationId", "")
            
            md.append(f"### `{method_upper}` {path}")
            if description:
                md.append(f"**Description**: {summary} - {description}\n")
            else:
                md.append(f"**Description**: {summary}.\n")
            
            # Auth Requirement
            security = info.get("security", [])
            is_authenticated = "Yes (Bearer Token required)" if security else "No"
            md.append(f"- **Authentication**: {is_authenticated}\n")
            
            # Parameters
            params = info.get("parameters", [])
            if params:
                md.append("#### Query/Path Parameters:")
                md.append("| Name | In | Type | Required | Description |")
                md.append("| :--- | :--- | :--- | :--- | :--- |")
                for p in params:
                    p_name = p.get("name")
                    p_in = p.get("in")
                    p_req = "Yes" if p.get("required") else "No"
                    p_schema = resolve_schema(p.get("schema", {}), schemas)
                    p_type = format_property_type(p.get("schema", {}), schemas)
                    p_desc = p.get("description", "") or "No description provided."
                    md.append(f"| `{p_name}` | {p_in} | `{p_type}` | {p_req} | {p_desc} |")
                md.append("")

            # Request Body
            req_body = info.get("requestBody")
            if req_body:
                content = req_body.get("content", {})
                json_content = content.get("application/json", {}) or content.get("multipart/form-data", {})
                schema = json_content.get("schema")
                if schema:
                    mock_json = build_mock_body(schema, schemas)
                    md.append("#### Request Body:")
                    md.append("```json")
                    md.append(json.dumps(mock_json, indent=2))
                    md.append("```\n")
            
            # Response
            custom_resp = get_custom_success_response(path, method, op_id)
            md.append("#### Success Response (200/201):")
            md.append("```json")
            md.append(json.dumps(custom_resp, indent=2))
            md.append("```\n")
            
            md.append("---\n")

    out_path = "api_documentation.md"
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    print(f"SUCCESSFULLY WRITTEN FORMATTED API DOC TO {out_path}")

if __name__ == "__main__":
    generate_markdown()
