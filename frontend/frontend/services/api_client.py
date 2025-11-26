import httpx
import reflex as rx
from typing import Optional, Dict, Any

API_URL = "http://localhost:8000/api/v1"

class APIClient:
    """Client for making requests to the backend API."""
    
    @staticmethod
    async def get(url: str, token: Optional[str] = None) -> httpx.Response:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            return await client.get(f"{API_URL}{url}", headers=headers)
            
    @staticmethod
    async def post(url: str, data: Dict[str, Any] = None, json_data: Dict[str, Any] = None, token: Optional[str] = None) -> httpx.Response:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            return await client.post(f"{API_URL}{url}", data=data, json=json_data, headers=headers)

    @staticmethod
    async def post_files(url: str, files: Dict, token: Optional[str] = None) -> httpx.Response:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            return await client.post(f"{API_URL}{url}", files=files, headers=headers)

    @staticmethod
    async def delete(url: str, token: Optional[str] = None) -> httpx.Response:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            return await client.delete(f"{API_URL}{url}", headers=headers)
