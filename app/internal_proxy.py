"""
Internal Proxy Service for forwarding requests to internal service.
"""
import aiohttp
from aiohttp import web
import json
import logging
import os
from typing import Optional, Dict, Any

# Internal service configuration
INTERNAL_SERVICE_URL = os.environ.get("INTERNAL_SERVICE_URL", "http://localhost:8080")
INTERNAL_SERVICE_TOKEN = os.environ.get("INTERNAL_SERVICE_TOKEN", "")

# Internal API prefix for the Go service
INTERNAL_API_PREFIX = "/api/v1/internal"

class InternalProxyService:
    """
    Service to proxy requests to internal pipeline service.
    """
    
    def __init__(self):
        self.client_session: Optional[aiohttp.ClientSession] = None
        self.base_url = INTERNAL_SERVICE_URL
        self.auth_token = INTERNAL_SERVICE_TOKEN
    
    async def setup(self):
        """Initialize the aiohttp client session."""
        timeout = aiohttp.ClientTimeout(total=None)
        self.client_session = aiohttp.ClientSession(timeout=timeout)
        logging.info(f"[InternalProxy] Initialized with base URL: {self.base_url}")
    
    async def close(self):
        """Close the client session."""
        if self.client_session:
            await self.client_session.close()
    
    def _get_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get headers including authentication."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        if extra_headers:
            headers.update(extra_headers)
        return headers
    
    async def forward_get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Forward a GET request to internal service."""
        if not self.client_session:
            raise RuntimeError("InternalProxyService not initialized")
        
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        
        try:
            async with self.client_session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logging.error(f"[InternalProxy] GET {path} failed: {response.status} - {error_text}")
                    return {"error": error_text, "status": response.status}
        except aiohttp.ClientError as e:
            logging.error(f"[InternalProxy] GET {path} error: {e}")
            return {"error": str(e), "status": 500}
    
    async def forward_post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Forward a POST request to internal service."""
        if not self.client_session:
            raise RuntimeError("InternalProxyService not initialized")
        
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        
        try:
            async with self.client_session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logging.error(f"[InternalProxy] POST {path} failed: {response.status} - {error_text}")
                    return {"error": error_text, "status": response.status}
        except aiohttp.ClientError as e:
            logging.error(f"[InternalProxy] POST {path} error: {e}")
            return {"error": str(e), "status": 500}
    
    # Pipeline execution endpoints
    async def execute_pipeline(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a pipeline workflow."""
        return await self.forward_post(f"{INTERNAL_API_PREFIX}/pipeline/execute", workflow_data)
    
    async def get_execution_list(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get list of pipeline executions."""
        return await self.forward_get(f"{INTERNAL_API_PREFIX}/pipeline/executions", params)
    
    async def get_execution_detail(self, execution_id: str) -> Dict[str, Any]:
        """Get detail of a specific execution."""
        return await self.forward_get(f"{INTERNAL_API_PREFIX}/pipeline/executions/{execution_id}")
    
    async def cancel_execution(self, execution_id: str) -> Dict[str, Any]:
        """Cancel a running execution."""
        return await self.forward_post(f"{INTERNAL_API_PREFIX}/pipeline/executions/{execution_id}/cancel")
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get execution status."""
        return await self.forward_get(f"{INTERNAL_API_PREFIX}/pipeline/executions/{execution_id}/status")
    
    # Pipeline management endpoints
    async def get_pipeline_detail(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline detail."""
        return await self.forward_get(f"{INTERNAL_API_PREFIX}/pipeline/{pipeline_id}")
    
    async def save_pipeline(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a pipeline (create or update)."""
        return await self.forward_post(f"{INTERNAL_API_PREFIX}/pipeline/save", pipeline_data)
    
    # Task queue endpoints
    async def get_task_queue(self) -> Dict[str, Any]:
        """Get task queue list."""
        return await self.forward_get(f"{INTERNAL_API_PREFIX}/task_queue")


# Global instance
_internal_proxy: Optional[InternalProxyService] = None


def get_internal_proxy() -> InternalProxyService:
    """Get the global internal proxy instance."""
    global _internal_proxy
    if _internal_proxy is None:
        _internal_proxy = InternalProxyService()
    return _internal_proxy


async def setup_internal_proxy():
    """Setup the internal proxy service."""
    proxy = get_internal_proxy()
    await proxy.setup()


async def close_internal_proxy():
    """Close the internal proxy service."""
    proxy = get_internal_proxy()
    await proxy.close()