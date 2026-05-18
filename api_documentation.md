# Docton Backend API Documentation

Welcome to the complete production API specifications for the Docton backend. This document covers the comprehensive REST API endpoints, schemas, authentication scopes, and real-time live map details.

## 📌 Global Specifications

- **Base URL**: `http://localhost:5000` (Local) / Production API Base URL
- **Protocol**: RESTful HTTPS with optional WebSocket endpoints
- **Standard Format**: JSON (`application/json` for request & response bodies)
- **Common Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer <JWT_TOKEN>` (for all authenticated endpoints)

## 🏷️ Standard Error Responses

Every endpoint may return one of the following standard errors under invalid execution contexts:

### `400` Bad Request / Conflict

```json
{
  "detail": "Error details or constraint violations"
}
```

### `401` Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### `403` Forbidden / Permission Denied

```json
{
  "detail": "Permission denied"
}
```

### `404` Route Not Found

```json
{
  "success": false,
  "message": "Route not found"
}
```

### `422` Request Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🏷️ AI Hub

### `POST` /api/ai/analyze-report
**Description**: Analyze Report.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "file": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "analysis": "The patient report shows normal levels of hemoglobin, but slightly elevated pulse rate."
}
```

---

### `POST` /api/ai/chat
**Description**: General Chat.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "message": "string",
  "sessionId": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "reply": "I am Docton AI Assistant. How can I help you today?",
  "sessionId": "645678ad9f12e34567890chat"
}
```

---

### `POST` /api/ai/pink-chat
**Description**: Pink Chat.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "message": "string",
  "sessionId": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "reply": "I am Docton AI Assistant. How can I help you today?",
  "sessionId": "645678ad9f12e34567890chat"
}
```

---

## 🏷️ Admin Controls

### `GET` /api/admin/care-packages
**Description**: Get All Care Packages.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
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
```

---

### `PATCH` /api/admin/care-packages/{id}/ship
**Description**: Ship Care Package.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | path | `string` | Yes | No description provided. |

#### Request Body:
```json
{
  "remarks": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Care package status updated to SHIPPED"
}
```

---

### `GET` /api/admin/commissions
**Description**: Get Commission Dashboard.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
  "dashboard": {
    "totalRevenue": 15000.0,
    "adminCommission": 2250.0,
    "providerEarnings": 12750.0,
    "commissionRate": "15%"
  }
}
```

---

## 🏷️ Analytics

### `GET` /api/analytics/growth
**Description**: Get Growth.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
  "data": {
    "period": "monthly",
    "growthRate": "12.5%",
    "newUsers": 350,
    "newProviders": 45
  }
}
```

---

### `GET` /api/analytics/heatmap
**Description**: Get Heatmap.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
  "heatmap": [
    {
      "latitude": 19.076,
      "longitude": 72.8777,
      "weight": 5
    }
  ]
}
```

---

### `GET` /api/analytics/revenue
**Description**: Get Revenue.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
  "data": {
    "totalEarnings": 50000.0,
    "adminEarnings": 7500.0,
    "refunds": 250.0
  }
}
```

---

## 🏷️ Auth

### `POST` /api/auth/login
**Description**: User Login.

- **Authentication**: No

#### Request Body:
```json
{
  "role": "string",
  "username": "string",
  "password": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY0NTY3OGFkOWYxMmUzNDU2Nzg5MGFiYyIsInJvbGUiOiJQQVRJRU5UIn0.signature",
  "role": "DOCTOR",
  "id": "645678ad9f12e34567890abc"
}
```

---

### `POST` /api/auth/register
**Description**: User Register.

- **Authentication**: No

#### Request Body:
```json
{
  "role": "string",
  "username": "string",
  "password": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY0NTY3OGFkOWYxMmUzNDU2Nzg5MGFiYyIsInJvbGUiOiJQQVRJRU5UIn0.signature",
  "role": "DOCTOR",
  "id": "645678ad9f12e34567890abc"
}
```

---

## 🏷️ Chat

### `GET` /api/chat/history/{partnerId}
**Description**: Get History.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `partnerId` | path | `string` | Yes | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
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
```

---

### `GET` /api/chat/recent
**Description**: Get Recent.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
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
```

---

### `POST` /api/chat/send
**Description**: Send Msg.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "receiverId": "string",
  "text": "string",
  "attachments": [
    {
      "url": "https://example.com/assets/file.jpg",
      "fileType": "string",
      "name": "string"
    }
  ]
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": {
    "id": "645678ad9f12e34567890msg3",
    "senderId": "645678ad9f12e34567890abc",
    "receiverId": "645678ad9f12e34567890def",
    "text": "Thank you, doctor!",
    "attachments": [],
    "timestamp": "2026-05-18T23:15:00Z"
  }
}
```

---

### `GET` /api/chat/token
**Description**: Get Cometchat Token.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NDU2NzhhZDlmMTJlMzQ1Njc4OTBhYmMiLCJhcHBJZCI6IjExMTEifQ.signature"
}
```

---

## 🏷️ Clinical

### `POST` /api/clinical/prescription
**Description**: Create Prescription.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "bookingId": "string",
  "medications": [
    {
      "name": "string",
      "dosage": "string",
      "frequency": "string",
      "duration": "string",
      "instructions": "string"
    }
  ],
  "advice": "string",
  "nextFollowUp": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Prescription created successfully",
  "prescriptionId": "645678ad9f12e34567890jkl"
}
```

---

### `GET` /api/clinical/prescription/pdf/{id}
**Description**: Get Prescription Pdf Endpoint.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | path | `string` | Yes | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
  "pdfUrl": "https://storage.googleapis.com/docton-bucket/prescriptions/prescription_645678ad.pdf"
}
```

---

### `POST` /api/clinical/visit-report
**Description**: Create Visit Report.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "bookingId": "string",
  "vitals": {
    "temperature": "string",
    "bloodPressure": "string",
    "pulseRate": "string",
    "spO2": "string",
    "weight": "string"
  },
  "chiefComplaints": "string",
  "diagnosis": "string",
  "observations": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Visit report created successfully",
  "reportId": "645678ad9f12e34567890mno"
}
```

---

### `GET` /api/clinical/visit-report/pdf/{id}
**Description**: Get Visit Report Pdf Endpoint.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | path | `string` | Yes | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
  "pdfUrl": "https://storage.googleapis.com/docton-bucket/visit-reports/visit_report_645678ad.pdf"
}
```

---

## 🏷️ Doctors

### `GET` /api/doctors/
**Description**: Get All Doctors.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `specialization` | query | `string` | No | No description provided. |
| `latitude` | query | `number` | No | No description provided. |
| `longitude` | query | `number` | No | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
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
      "languages": [
        "English",
        "Hindi"
      ],
      "licenseNo": "MCI-12345",
      "clinicName": "Sunny Pediatric Clinic",
      "clinicAddress": "456 Park Avenue, Mumbai",
      "isOnline": 1
    }
  ]
}
```

---

### `POST` /api/doctors/availability
**Description**: Update Availability.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "isOnline": 0,
  "clinicHours": [
    {
      "day": "string",
      "start": "string",
      "end": "string"
    }
  ]
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Availability updated successfully"
}
```

---

### `POST` /api/doctors/incoming-call
**Description**: Initiate Incoming Call.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "bookingId": "string",
  "patientId": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Call notification initiated"
}
```

---

### `POST` /api/doctors/login
**Description**: Login.

- **Authentication**: No

#### Request Body:
```json
{
  "username": "string",
  "password": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY0NTY3OGFkOWYxMmUzNDU2Nzg5MWRlZiIsInJvbGUiOiJET0NUT1IifQ.signature"
}
```

---

### `GET` /api/doctors/{id}
**Description**: Get Doctor By Id.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | path | `string` | Yes | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
  "doctor": {
    "id": "645678ad9f12e34567890def",
    "name": "Dr. Sarah Smith",
    "profileImage": "https://example.com/dr-sarah.jpg",
    "bio": "Experienced pediatrician with 10+ years of practice.",
    "specialization": "Pediatrics",
    "qualifications": "MD, DNB (Pediatrics)",
    "experience": 12,
    "languages": [
      "English",
      "Hindi"
    ],
    "licenseNo": "MCI-12345",
    "clinicName": "Sunny Pediatric Clinic",
    "clinicAddress": "456 Park Avenue, Mumbai",
    "isOnline": 1
  }
}
```

---

### `PUT` /api/doctors/{id}
**Description**: Update Profile.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | path | `string` | Yes | No description provided. |

#### Request Body:
```json
{
  "name": "string",
  "profileImage": "string",
  "bio": "string",
  "specialization": "string",
  "qualifications": [
    "string"
  ],
  "experience": 0,
  "languages": [
    "string"
  ],
  "licenseNo": "string",
  "clinicName": "string",
  "clinicAddress": "string",
  "isOnline": 0
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Doctor profile updated successfully"
}
```

---

## 🏷️ Financial

### `GET` /api/financial/earnings
**Description**: Get Earnings.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
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
```

---

### `POST` /api/financial/simulate-payment
**Description**: Simulate Payment.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "totalAmount": 0.0,
  "bookingId": "string",
  "userId": "string",
  "providerId": "string",
  "providerType": "string",
  "paymentMode": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
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
```

---

### `POST` /api/financial/withdraw
**Description**: Withdraw.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "amount": 0.0,
  "bankDetails": {
    "accountNumber": "string",
    "ifscCode": "string",
    "bankName": "string",
    "accountHolderName": "string"
  }
}
```

#### Success Response (200/201):
```json
{
  "success": true,
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
```

---

## 🏷️ General

### `GET` /
**Description**: Root.

- **Authentication**: No

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Docton Backend is online",
  "framework": "FastAPI (Python)"
}
```

---

## 🏷️ Health

### `GET` /api/health
**Description**: Health Check.

- **Authentication**: No

#### Success Response (200/201):
```json
{
  "status": "UP",
  "database": "CONNECTED",
  "timestamp": "2026-05-18T23:15:00Z"
}
```

---

## 🏷️ Nurses

### `GET` /api/nurses/
**Description**: Get Nurses.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `task` | query | `string` | No | Comma-separated skills/tasks, e.g. Injection,Elderly Care |
| `duration_mode` | query | `string` | No | hourly, daily, or monthly |
| `max_rate` | query | `number` | No | Maximum price based on duration mode |
| `latitude` | query | `number` | No | No description provided. |
| `longitude` | query | `number` | No | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
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
        "latitude": 19.076,
        "longitude": 72.8777
      },
      "distance_km": 0.0
    }
  ]
}
```

---

### `GET` /api/nurses/{id}
**Description**: Get Nurse By Id.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | path | `string` | Yes | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
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
      "latitude": 19.076,
      "longitude": 72.8777
    }
  }
}
```

---

## 🏷️ Quick Fill Onboarding

### `POST` /api/users/quick-fill
**Description**: Quick Fill Onboarding.

- **Authentication**: No

#### Request Body:
```json
{
  "provider": "string",
  "token": "string",
  "phone": "+1234567890",
  "gender": "string",
  "dob": "1995-08-15"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Onboarding completed successfully"
}
```

---

## 🏷️ System

### `GET` /api/system/announcements
**Description**: Get Announcements.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
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
```

---

### `POST` /api/system/announcements
**Description**: Create Announcement.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "title": "string",
  "content": "string",
  "role": "string",
  "expiresAt": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Announcement created successfully"
}
```

---

### `GET` /api/system/banners
**Description**: Get Banners.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
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
```

---

### `POST` /api/system/banners
**Description**: Create Banner.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "imageUrl": "https://example.com/assets/file.jpg",
  "actionUrl": "string",
  "title": "string",
  "description": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Banner created successfully"
}
```

---

### `DELETE` /api/system/banners/{id}
**Description**: Delete Banner.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | path | `string` | Yes | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Banner deleted successfully"
}
```

---

### `POST` /api/system/config
**Description**: Update Config.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "key": "string",
  "value": {}
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Config parameter updated successfully"
}
```

---

### `GET` /api/system/config/{key}
**Description**: Get Config.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `key` | path | `string` | Yes | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
  "key": "app_version",
  "value": "1.0.4"
}
```

---

## 🏷️ Tasks

### `GET` /api/tasks
**Description**: Get Tasks.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
  "tasks": [
    {
      "id": "645678ad9f12e34567890tsk1",
      "title": "Complete Doctor Profile",
      "description": "Upload clinic registration and license documents.",
      "isCompleted": false
    }
  ]
}
```

---

### `PUT` /api/tasks/{id}
**Description**: Update Task Status.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | path | `string` | Yes | No description provided. |

#### Request Body:
```json
{
  "isCompleted": true
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Task status updated successfully"
}
```

---

## 🏷️ Tracking

### `GET` /api/tracking/admin/activities
**Description**: Get Recent Activities.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `limit` | query | `integer` | No | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
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
```

---

### `GET` /api/tracking/admin/history/{user_id}
**Description**: Get Location History.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | path | `string` | Yes | No description provided. |
| `limit` | query | `integer` | No | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
  "userId": "645678ad9f12e34567890def",
  "history": [
    {
      "latitude": 19.076,
      "longitude": 72.8777,
      "timestamp": "2026-05-18T23:15:00Z"
    }
  ]
}
```

---

### `GET` /api/tracking/admin/live
**Description**: Get Live Locations.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
  "locations": [
    {
      "userId": "645678ad9f12e34567890def",
      "role": "DOCTOR",
      "name": "Dr. Sarah Smith",
      "latitude": 19.076,
      "longitude": 72.8777,
      "updatedAt": "2026-05-18T23:15:00Z"
    }
  ]
}
```

---

### `POST` /api/tracking/update
**Description**: Update Location.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "latitude": 0.0,
  "longitude": 0.0
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Location updated successfully"
}
```

---

## 🏷️ Users

### `GET` /api/users/
**Description**: Get All Users.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `role` | query | `string` | No | No description provided. |
| `isBlocked` | query | `string` | No | No description provided. |
| `isDeleted` | query | `string` | No | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
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
      "isEmailVerified": true,
      "isBlocked": false,
      "isDeleted": false
    }
  ]
}
```

---

### `POST` /api/users/login
**Description**: Login.

- **Authentication**: No

#### Request Body:
```json
{
  "email": "user@docton.com",
  "password": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY0NTY3OGFkOWYxMmUzNDU2Nzg5MGFiYyIsInJvbGUiOiJQQVRJRU5UIn0.signature",
  "role": "PATIENT",
  "id": "645678ad9f12e34567890abc"
}
```

---

### `GET` /api/users/me
**Description**: Get Me.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
  "user": {
    "id": "645678ad9f12e34567890abc",
    "name": "Jane Doe",
    "email": "user@docton.com",
    "phone": "+1234567890",
    "gender": "female",
    "dob": "1995-08-15",
    "role": "PATIENT",
    "isEmailVerified": true,
    "isPhoneVerified": true,
    "address": {
      "line1": "123 Main St",
      "line2": "Apt 4B",
      "city": "Mumbai",
      "state": "Maharashtra",
      "country": "India",
      "pincode": "400001"
    },
    "location": {
      "latitude": 19.076,
      "longitude": 72.8777
    }
  }
}
```

---

### `POST` /api/users/register
**Description**: Register.

- **Authentication**: No

#### Request Body:
```json
{
  "name": "string",
  "email": "user@docton.com",
  "phone": "+1234567890",
  "password": "string",
  "gender": "string",
  "dob": "1995-08-15"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "User registered. OTP sent to email."
}
```

---

### `POST` /api/users/verify-otp
**Description**: Verify Otp.

- **Authentication**: No

#### Request Body:
```json
{
  "email": "user@docton.com",
  "otp": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Email verified successfully"
}
```

---

## 🏷️ Verification

### `GET` /api/verification/pending
**Description**: Get Pending Verifications.

- **Authentication**: Yes (Bearer Token required)

#### Success Response (200/201):
```json
{
  "success": true,
  "data": [
    {
      "id": "645678ad9f12e34567890zzz",
      "userId": "645678ad9f12e34567890def",
      "userRole": "DOCTOR",
      "document": "https://example.com/assets/license.jpg",
      "status": "PENDING",
      "remarks": null,
      "created_at": "2026-05-18T10:00:00Z"
    }
  ]
}
```

---

### `PATCH` /api/verification/status/{id}
**Description**: Update Verification Status.

- **Authentication**: Yes (Bearer Token required)

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | path | `string` | Yes | No description provided. |

#### Request Body:
```json
{
  "status": "string",
  "remarks": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Verification status updated successfully"
}
```

---

### `POST` /api/verification/submit
**Description**: Submit Verification.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "document": "https://example.com/assets/file.jpg"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Verification documents submitted successfully"
}
```

---

## 🏷️ Video Calling

### `GET` /api/video/token
**Description**: Get Video Token - Generate a secure ZEGOCLOUD room access token (token04)

- **Authentication**: No

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `userId` | query | `string` | Yes | No description provided. |
| `roomId` | query | `string` | Yes | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
  "token": "04AAAAAABBBBBBCCCCCCDDDDDD111111222222"
}
```

---

### `POST` /api/video/webhook
**Description**: Zegocloud Webhook - Handle ZEGOCLOUD Server-to-Server callbacks

- **Authentication**: No

#### Query/Path Parameters:
| Name | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `timestamp` | query | `string` | No | No description provided. |
| `nonce` | query | `string` | No | No description provided. |
| `signature` | query | `string` | No | No description provided. |

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Webhook processed successfully"
}
```

---

## 🏷️ Women's Health (Pink Mode)

### `POST` /api/womens-health/auto-pay
**Description**: Register Auto Pay.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "upiId": "string",
  "cardNumber": "string",
  "cardExpiry": "string",
  "mandateLimit": 0.0
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Auto-pay setup registered successfully"
}
```

---

### `POST` /api/womens-health/log
**Description**: Log Cycle.

- **Authentication**: Yes (Bearer Token required)

#### Request Body:
```json
{
  "startDate": "string",
  "endDate": "string",
  "notes": "string",
  "shippingAddress": "string"
}
```

#### Success Response (200/201):
```json
{
  "success": true,
  "message": "Cycle logged successfully"
}
```

---
