import httpx
import asyncio
import json
from datetime import datetime, timedelta
from decouple import config
from loguru import logger
from typing import Any

# Configuration
PORT_CLIENT_ID = config("PORT_CLIENT_ID")
PORT_CLIENT_SECRET = config("PORT_CLIENT_SECRET")
PORT_API_URL = config("PORT_API_URL", default="https://api.getport.io/v1")

# User Configurable Variables
BLUEPRINTS = config("BLUEPRINT_IDENTIFIERS").split(",")
DAYS = int(config("DAYS_TO_RECOVER", default=3))
TIMEOUT = int(config("PORT_API_TIMEOUT", default=300))


AUDIT_ACTION = "DELETE"
AUDIT_STATUS = "SUCCESS"

# Authentication to retrieve access token
async def get_access_token() -> str:
    logger.info("Retrieving access token...")
    credentials = {"clientId": PORT_CLIENT_ID, "clientSecret": PORT_CLIENT_SECRET}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PORT_API_URL}/auth/access_token", json=credentials)
        response_data = response.json()
        access_token = response_data.get("accessToken")
        if access_token:
            logger.info("Access token successfully retrieved")
        else:
            logger.error("Failed to retrieve access token")
        return access_token

# Fetch audit logs for a specified blueprint and action
async def fetch_audit_logs(access_token, blueprint, from_date, to_date) -> list[dict[str, Any]]:
    logger.info(f"Fetching audit logs for blueprint '{blueprint}'...")
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "blueprint": blueprint,
        # "from": from_date, // Uncomment to filter by date range
        # "to": to_date, // Uncomment to filter by date range
        "action": AUDIT_ACTION,
        "status": AUDIT_STATUS
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PORT_API_URL}/audit-log", headers=headers, params=params, timeout=TIMEOUT)
        audits = response.json().get("audits", [])
        logger.info(f"Fetched {len(audits)} audit logs for blueprint '{blueprint}'")
        return audits

# Restore a deleted entity using the Entities API
async def restore_entity(access_token, blueprint_identifier, entity_data) -> tuple[int, dict[str, Any]]:
    logger.info(f"Restoring entity: {entity_data['identifier']}")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    url = f"{PORT_API_URL}/blueprints/{blueprint_identifier}/entities"
    
    payload = json.dumps({
        "identifier": entity_data["identifier"],
        "title": entity_data["title"],
        "properties": entity_data.get("properties", {}),
        "relations": entity_data.get("relations", {})
    })

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload, timeout=TIMEOUT)
        status_code = response.status_code
        response_data = response.json()
        
        if status_code == 200:
            logger.success(f"Successfully restored entity: {entity_data['identifier']}")
        else:
            logger.error(f"Failed to restore entity: {entity_data['identifier']}, Status Code: {status_code}, Error: {response_data}")
        
        return status_code, response_data

# Process and restore deleted entities from audit logs for multiple blueprints
async def restore_deleted_entities(blueprints, days):
    logger.info("Starting the process to restore deleted entities...")
    try:
        access_token = await get_access_token()
        if not access_token:
            logger.critical("Unable to continue without access token. Exiting.")
            return
        
        # Define the date range for fetching audit logs
        to_date = datetime.utcnow().isoformat() + "Z"
        from_date = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        logger.info(f"Restoring data from the last {days} days (from {from_date} to {to_date})")

        for blueprint in blueprints:
            blueprint = blueprint.strip()
            logger.info(f"Processing blueprint: {blueprint}")
            
            # Fetch audit logs
            audit_logs = await fetch_audit_logs(access_token, blueprint, from_date, to_date)
            
            if not audit_logs:
                logger.warning(f"No deleted entities found for blueprint {blueprint} in the specified period.")
                continue
            
            # Filter and restore deleted entities
            index = 0
            for audit in audit_logs:
                if audit.get("action") == AUDIT_ACTION and audit.get("status") == AUDIT_STATUS:
                    before_data = audit["diff"].get("before", {})
                    entity_id = before_data.get("identifier")
                    
                    if entity_id:
                        logger.debug(f"Attempting to restore entity: {entity_id} from blueprint: {blueprint}. Currently at ({index + 1}/{len(audit_logs)}) entities")
                        await restore_entity(access_token, blueprint, before_data)
                        index += 1
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")

    logger.info("Process completed.")

if __name__ == "__main__":
    logger.add("restore_deleted_data.log", rotation="1 MB", level="DEBUG")
    if BLUEPRINTS:
        asyncio.run(restore_deleted_entities(BLUEPRINTS, DAYS))
    else:
        logger.error("No blueprint identifiers provided. Exiting.")
