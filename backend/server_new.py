from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime, timedelta
import uuid
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI
app = FastAPI(title="SESGRG API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# In-memory database for testing
in_memory_db = {
    "people": [],
    "publications": [],
    "projects": [
        {
            "id": "1",
            "name": "Smart Grid Optimization Using Machine Learning",
            "description": "This project focuses on developing advanced machine learning algorithms to optimize power distribution in smart grid networks. We aim to reduce energy losses and improve overall grid efficiency through predictive analytics and real-time optimization.",
            "start_date": "2024-01-15",
            "end_date": "2025-12-31",
            "team_leader": "Dr. Mohammad Rahman",
            "team_members": "Dr. Sarah Ahmed, Eng. Karim Hassan, Ms. Fatima Ali, Mr. Tanvir Islam",
            "funded_by": "Bangladesh Science and Technology Ministry",
            "total_members": 5,
            "status": "ongoing",
            "research_area": "Smart Grid Technology",
            "project_link": "https://example.com/smart-grid-project",
            "image": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxzbWFydCUyMGdyaWR8ZW58MHx8fHwxNzU2NTM1MTU3fDA&ixlib=rb-4.1.0&q=85"
        },
        {
            "id": "2",
            "name": "Solar Energy Integration in Urban Areas",
            "description": "Research project aimed at developing innovative solutions for integrating solar photovoltaic systems in dense urban environments. Focus on building-integrated photovoltaics and community solar solutions.",
            "start_date": "2023-06-01",
            "end_date": "2024-05-31",
            "team_leader": "Prof. Nasir Uddin",
            "team_members": "Dr. Rashida Khatun, Eng. Ahmed Bin Rashid, Ms. Nusrat Jahan",
            "funded_by": "BRAC University Research Grant",
            "total_members": 4,
            "status": "completed",
            "research_area": "Renewable Energy",
            "project_link": None,
            "image": "https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwyfHxyZW5ld2FibGV8ZW58MHx8fHwxNzU2NTM1MTY0fDA&ixlib=rb-4.1.0&q=85"
        }
    ],
    "achievements": [],
    "news": [],
    "events": [],
    "research_areas": [
        {
            "id": "smart-grid-technologies",
            "title": "Smart Grid Technologies",
            "description": "Next-generation intelligent grid systems for improved reliability and efficiency.",
            "image": "https://i.ibb.co.com/kV0RP1Xh/smart-grid.jpg",
            "details": "Advanced smart grid technologies for modern power systems..."
        }
    ],
    "photo_gallery": [],
    "settings": {
        "site_title": "Sustainable Energy & Smart Grid Research",
        "site_description": "Pioneering Research in Clean Energy, Renewable Integration, and Next-Generation Smart Grid Systems.",
        "contact_email": "sesg@bracu.ac.bd",
        "logo": "https://customer-assets.emergentagent.com/job_da31abd5-8dec-452e-a49e-9beda777d1d4/artifacts/ii07ct2o_Logo.jpg"
    }
}

# Helper functions
def get_collection_data(collection_name, filters=None, order_by=None, limit=None):
    return in_memory_db.get(collection_name, [])

def add_document(collection_name, data):
    data['id'] = str(uuid.uuid4())
    data['created_at'] = datetime.utcnow().isoformat()
    in_memory_db[collection_name].append(data)
    return data

def update_document(collection_name, doc_id, data):
    for item in in_memory_db[collection_name]:
        if item['id'] == doc_id:
            # Allow clearing fields by setting empty strings
            item.update(data)
            item['updated_at'] = datetime.utcnow().isoformat()
            return item
    raise HTTPException(status_code=404, detail="Document not found")

def delete_document(collection_name, doc_id):
    in_memory_db[collection_name] = [item for item in in_memory_db[collection_name] if item['id'] != doc_id]
    return {"message": "Document deleted successfully"}

# Pydantic Models
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_role: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ProjectCreate(BaseModel):
    name: str
    description: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    team_leader: Optional[str] = None
    team_members: Optional[str] = None
    funded_by: Optional[str] = None
    total_members: Optional[int] = None
    status: str = "ongoing"
    research_area: Optional[str] = None
    project_link: Optional[str] = None
    image: Optional[str] = None

# Authentication Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username, "role": payload.get("role", "user")}
    except JWTError:
        raise credentials_exception

# API Endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "@dminsesg705")
    
    if request.username == admin_username and request.password == admin_password:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": request.username, "role": "admin"}, 
            expires_delta=access_token_expires
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_role="admin"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

@app.get("/api/projects")
async def get_projects(category: Optional[str] = None, status: Optional[str] = None):
    filters = []
    if category:
        filters.append(("category", "==", category))
    if status:
        filters.append(("status", "==", status))
    
    return get_collection_data("projects", filters=filters)

@app.post("/api/projects")
async def create_project(project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    project_data = project.dict()
    return add_document("projects", project_data)

@app.put("/api/projects/{project_id}")
async def update_project(project_id: str, project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    project_data = project.dict()
    return update_document("projects", project_id, project_data)

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return delete_document("projects", project_id)

# Other endpoints for research areas, settings etc.
@app.get("/api/research-areas")
async def get_research_areas():
    return get_collection_data("research_areas")

@app.get("/api/settings")
async def get_settings():
    return in_memory_db["settings"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)