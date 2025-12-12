# ABOUTME: FastAPI routes for custom agent listing and management
# ABOUTME: Handles retrieval, updating, and deletion of user-specific custom agents

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from elysia.api.core.log import logger
from elysia.api.dependencies.common import get_user_manager
from elysia.api.services.user import UserManager
from elysia.tools.domain.custom_agent_store import (
    load_user_custom_agents,
    delete_custom_agent,
    update_custom_agent,
)
from elysia.util.client import ClientManager

router = APIRouter()


class UpdateAgentRequest(BaseModel):
    agent_name: str
    system_prompt: str


@router.get("/{user_id}/list")
async def list_agents(
    user_id: str,
    user_manager: UserManager = Depends(get_user_manager),
) -> JSONResponse:
    """
    List custom agents created by user

    Args:
        user_id: The ID of the user
        user_manager: The user manager dependency

    Returns:
        JSONResponse with list of agents
    """
    logger.debug(f"List agents request for user: {user_id}")

    try:
        user_local = await user_manager.get_user_local(user_id)
        client_manager: ClientManager = user_local["client_manager"]

        agents = await load_user_custom_agents(
            user_id=user_id,
            client_manager=client_manager,
            logger=logger,
        )

        return JSONResponse(
            content={
                "user_id": user_id,
                "agents": agents,
                "total_count": len(agents),
            },
            status_code=200,
        )

    except Exception as e:
        logger.exception(f"Error in list_agents endpoint")
        return JSONResponse(
            content={
                "user_id": user_id,
                "agents": [],
                "total_count": 0,
                "error": str(e),
            },
            status_code=500,
        )


@router.delete("/{user_id}/delete/{agent_id}")
async def delete_agent(
    user_id: str,
    agent_id: str,
    user_manager: UserManager = Depends(get_user_manager),
) -> JSONResponse:
    """
    Delete a custom agent

    Args:
        user_id: The ID of the user
        agent_id: The ID of the agent to delete
        user_manager: The user manager dependency

    Returns:
        JSONResponse with deletion result
    """
    logger.info(f"Delete agent request: user={user_id}, agent={agent_id}")

    try:
        user_local = await user_manager.get_user_local(user_id)
        client_manager: ClientManager = user_local["client_manager"]

        success = await delete_custom_agent(
            agent_id=agent_id,
            user_id=user_id,
            client_manager=client_manager,
            logger=logger,
        )

        if success:
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Agent deleted successfully",
                },
                status_code=200,
            )
        else:
            return JSONResponse(
                content={
                    "success": False,
                    "error": "Agent not found or unauthorized",
                    "message": "Failed to delete agent",
                },
                status_code=404,
            )

    except Exception as e:
        logger.exception(f"Error in delete_agent endpoint")
        return JSONResponse(
            content={
                "success": False,
                "error": str(e),
                "message": f"Deletion failed: {str(e)}",
            },
            status_code=500,
        )


@router.put("/{user_id}/update/{agent_id}")
async def update_agent(
    user_id: str,
    agent_id: str,
    update_data: UpdateAgentRequest,
    user_manager: UserManager = Depends(get_user_manager),
) -> JSONResponse:
    """
    Update a custom agent

    Args:
        user_id: The ID of the user
        agent_id: The ID of the agent to update
        update_data: Updated agent data
        user_manager: The user manager dependency

    Returns:
        JSONResponse with update result
    """
    logger.info(f"Update agent request: user={user_id}, agent={agent_id}")

    try:
        user_local = await user_manager.get_user_local(user_id)
        client_manager: ClientManager = user_local["client_manager"]
        settings = user_local["tree_manager"].settings

        updated_agent = await update_custom_agent(
            agent_id=agent_id,
            user_id=user_id,
            agent_name=update_data.agent_name,
            system_prompt=update_data.system_prompt,
            client_manager=client_manager,
            settings=settings,
            logger=logger,
        )

        if updated_agent:
            return JSONResponse(
                content={
                    "success": True,
                    "agent": updated_agent,
                    "message": "Agent updated successfully",
                },
                status_code=200,
            )
        else:
            return JSONResponse(
                content={
                    "success": False,
                    "error": "Agent not found or unauthorized",
                    "message": "Failed to update agent",
                },
                status_code=404,
            )

    except Exception as e:
        logger.exception(f"Error in update_agent endpoint")
        return JSONResponse(
            content={
                "success": False,
                "error": str(e),
                "message": f"Update failed: {str(e)}",
            },
            status_code=500,
        )
