import pytest
from httpx import AsyncClient
from fastapi import status
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.connect_db import Base, get_db
from services.auth import auth_services
from db.models import User

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = SessionTesting()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


async def mock_get_current_user():
    return User(id=1, email="test@example.com", username="testuser")


app.dependency_overrides[auth_services.get_current_user] = mock_get_current_user


@pytest.mark.asyncio
async def test_create_contact():
    async with AsyncClient(app=app, base_url="http://test") as client:
        contact_data = {
            "first_name": "John",
            "second_name": "Doe",
            "email": "johndoe@example.com",
            "phone": "1234567890",
            "birthdate": "1990-01-01",
            "additional_data": "Friend"
        }
        response = await client.post("/api/contacts/", json=contact_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["first_name"] == "John"
        assert response_data["second_name"] == "Doe"
        assert response_data["email"] == "johndoe@example.com"
