# app/main.py
import uvicorn
from fastapi import FastAPI
from app.db import db
from app.routers import plans, permissions, subscriptions, usage, access, services, users
from app.auth import auth_router
from app.routers.services import router as service_router

app = FastAPI(title="Cloud Service Access MGMT")

# auth (login, token)
app.include_router(auth_router)

# feature routers
app.include_router(plans.router)
app.include_router(permissions.router)
app.include_router(subscriptions.router)
app.include_router(usage.router)
app.include_router(access.router)
app.include_router(services.router)
app.include_router(users.router)
app.include_router(service_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
