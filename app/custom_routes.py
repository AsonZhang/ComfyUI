"""
Custom routes for internal service proxy.
These routes replace the original ComfyUI execution/queue routes.
"""
from aiohttp import web
import logging
import json
from typing import Dict, Any

from app.internal_proxy import get_internal_proxy


def create_custom_routes(routes: web.RouteTableDef):
    """Create custom routes that forward to internal service."""
    
    # Pipeline execution - replaces original /prompt
    @routes.post("/api/custom/pipeline/execute")
    async def execute_pipeline(request: web.Request) -> web.Response:
        """
        Execute a pipeline workflow.
        Forward to internal service: POST /pipeline/execute
        """
        proxy = get_internal_proxy()
        
        try:
            data = await request.json()
            result = await proxy.execute_pipeline(data)
            
            if "error" in result:
                return web.json_response(result, status=result.get("status", 500))
            
            return web.json_response(result)
        except json.JSONDecodeError as e:
            logging.error(f"[CustomRoutes] Invalid JSON in execute_pipeline: {e}")
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logging.error(f"[CustomRoutes] execute_pipeline error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # Get execution list - replaces original /history
    @routes.get("/api/custom/pipeline/executions")
    async def get_executions(request: web.Request) -> web.Response:
        """
        Get list of pipeline executions.
        Forward to internal service: GET /pipeline/executions
        """
        proxy = get_internal_proxy()
        
        try:
            # Extract query parameters
            params = {}
            for key, value in request.rel_url.query.items():
                params[key] = value
            
            result = await proxy.get_execution_list(params)
            
            if "error" in result:
                return web.json_response(result, status=result.get("status", 500))
            
            return web.json_response(result)
        except Exception as e:
            logging.error(f"[CustomRoutes] get_executions error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # Get execution detail
    @routes.get("/api/custom/pipeline/executions/{execution_id}")
    async def get_execution_detail(request: web.Request) -> web.Response:
        """
        Get detail of a specific execution.
        Forward to internal service: GET /pipeline/executions/:id
        """
        proxy = get_internal_proxy()
        
        try:
            execution_id = request.match_info.get("execution_id", "")
            if not execution_id:
                return web.json_response({"error": "execution_id required"}, status=400)
            
            result = await proxy.get_execution_detail(execution_id)
            
            if "error" in result:
                return web.json_response(result, status=result.get("status", 500))
            
            return web.json_response(result)
        except Exception as e:
            logging.error(f"[CustomRoutes] get_execution_detail error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # Cancel execution - replaces original /interrupt (with prompt_id)
    @routes.post("/api/custom/pipeline/executions/{execution_id}/cancel")
    async def cancel_execution(request: web.Request) -> web.Response:
        """
        Cancel a running execution.
        Forward to internal service: POST /pipeline/executions/:id/cancel
        """
        proxy = get_internal_proxy()
        
        try:
            execution_id = request.match_info.get("execution_id", "")
            if not execution_id:
                return web.json_response({"error": "execution_id required"}, status=400)
            
            result = await proxy.cancel_execution(execution_id)
            
            if "error" in result:
                return web.json_response(result, status=result.get("status", 500))
            
            return web.json_response(result)
        except Exception as e:
            logging.error(f"[CustomRoutes] cancel_execution error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # Get execution status
    @routes.get("/api/custom/pipeline/executions/{execution_id}/status")
    async def get_execution_status(request: web.Request) -> web.Response:
        """
        Get execution status.
        Forward to internal service: GET /pipeline/executions/:id/status
        """
        proxy = get_internal_proxy()
        
        try:
            execution_id = request.match_info.get("execution_id", "")
            if not execution_id:
                return web.json_response({"error": "execution_id required"}, status=400)
            
            result = await proxy.get_execution_status(execution_id)
            
            if "error" in result:
                return web.json_response(result, status=result.get("status", 500))
            
            return web.json_response(result)
        except Exception as e:
            logging.error(f"[CustomRoutes] get_execution_status error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # Get pipeline detail
    @routes.get("/api/custom/pipeline/{pipeline_id}")
    async def get_pipeline_detail(request: web.Request) -> web.Response:
        """
        Get pipeline detail.
        Forward to internal service: GET /pipeline/:id
        """
        proxy = get_internal_proxy()
        
        try:
            pipeline_id = request.match_info.get("pipeline_id", "")
            if not pipeline_id:
                return web.json_response({"error": "pipeline_id required"}, status=400)
            
            result = await proxy.get_pipeline_detail(pipeline_id)
            
            if "error" in result:
                return web.json_response(result, status=result.get("status", 500))
            
            return web.json_response(result)
        except Exception as e:
            logging.error(f"[CustomRoutes] get_pipeline_detail error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # Save pipeline - replaces original workflow save functionality
    @routes.post("/api/custom/pipeline/save")
    async def save_pipeline(request: web.Request) -> web.Response:
        """
        Save a pipeline (create or update).
        Forward to internal service: POST /pipeline/save
        """
        proxy = get_internal_proxy()
        
        try:
            data = await request.json()
            result = await proxy.save_pipeline(data)
            
            if "error" in result:
                return web.json_response(result, status=result.get("status", 500))
            
            return web.json_response(result)
        except json.JSONDecodeError as e:
            logging.error(f"[CustomRoutes] Invalid JSON in save_pipeline: {e}")
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logging.error(f"[CustomRoutes] save_pipeline error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # Get task queue - replaces original /queue
    @routes.get("/api/custom/task_queue")
    async def get_task_queue(request: web.Request) -> web.Response:
        """
        Get task queue list.
        Forward to internal service: GET /task_queue
        """
        proxy = get_internal_proxy()
        
        try:
            result = await proxy.get_task_queue()
            
            if "error" in result:
                return web.json_response(result, status=result.get("status", 500))
            
            return web.json_response(result)
        except Exception as e:
            logging.error(f"[CustomRoutes] get_task_queue error: {e}")
            return web.json_response({"error": str(e)}, status=500)


def register_custom_routes(app: web.Application):
    """Register custom routes with the application."""
    routes = web.RouteTableDef()
    create_custom_routes(routes)
    app.add_routes(routes)
    logging.info("[CustomRoutes] Registered custom API routes")