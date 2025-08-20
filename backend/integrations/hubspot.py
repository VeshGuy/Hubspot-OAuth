from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import requests
import datetime
import json
import secrets
import httpx
import asyncio
import base64
import hashlib
import logging
from integrations.integration_item import IntegrationItem

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLIENT_ID = "d1ff3409-7b29-4e73-9311-09e8868e48d4"
CLIENT_SECRET = "54788fe0-54e1-44ac-a2c4-1c01e67b17d3"
SCOPE = 'oauth crm.objects.companies.read crm.objects.companies.write crm.objects.contacts.read crm.objects.contacts.write'

REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
AUTHORIZATION_URI = f'https://app-na2.hubspot.com/oauth/authorize'

async def authorize_hubspot(user_id, org_id):
    logger.info(f"Authorize HubSpot called with user_id={user_id}, org_id={org_id}")
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')
    auth_url = f'{AUTHORIZATION_URI}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&state={encoded_state}'
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', json.dumps(state_data), expire=600)
    logger.info(f"Returning auth_url: {auth_url}")
    return auth_url

async def oauth2callback_hubspot(request: Request):
    logger.info("oauth2callback_hubspot called")
    if request.query_params.get('error'):
        logger.error(f"OAuth error: {request.query_params.get('error_description')}")
        raise HTTPException(status_code=400, detail=request.query_params.get('error_description'))
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    logger.info(f"Received code: {'True' if code else 'False'}, state: {'True' if encoded_state else 'False'}")
    state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}') 
    logger.info(f"Saved state bytes from redis: {'True' if saved_state  else 'False'}")

    if not saved_state: 
        logger.error("No saved state found in Redis.")
        raise HTTPException(status_code=400, detail='State does not match or has expired.')

    saved_state_decoded = saved_state.decode('utf-8') 
    saved_state_json = json.loads(saved_state_decoded) 

    if original_state != saved_state_json.get('state'): 
        logger.error("State does not match.")
        raise HTTPException(status_code=400, detail='State does not match.')

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://api.hubspot.com/oauth/v1/token',
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': REDIRECT_URI,
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                },
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}')
        )
    logger.info(f"Token response: {'Positive' if response.json() else 'Negative'}")
    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)

    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_hubspot_credentials(user_id, org_id):
    logger.info(f"get_hubspot_credentials called with user_id={user_id}, org_id={org_id}")
    credentials_bytes = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}') 
    logger.info(f"Fetched credentials bytes from redis: {'True' if credentials_bytes else 'False'}")
    if not credentials_bytes:
        logger.error("No credentials found.")
        raise HTTPException(status_code=400, detail='No credentials found.')
    
    credentials_decoded = credentials_bytes.decode('utf-8') 
    credentials = json.loads(credentials_decoded) 
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')
    logger.info("Returning credentials.")
    return credentials

# Didn't use this function in the final version of the code since I wanted to display the actual data being pulled from the CRM
def create_integration_item_metadata_object(response_json: str, item_type: str, parent_id=None, parent_name=None) -> IntegrationItem:
    parent_id = None if parent_id is None else parent_id + '_Base'
    integration_item_metadata = IntegrationItem(
        id=response_json.get('id', None) + '_' + item_type,
        name=response_json.get('properties', {}).get('name', None),
        domain=response_json.get('properties', {}).get('domain', None), 
        type=item_type,
        parent_id=parent_id,
        parent_path_or_name=parent_name,
    )
    return integration_item_metadata

def fetch_items(access_token: str, url: str, aggregated_response: list, limit=None) -> dict:
    params = {'limit': limit} if limit is not None else {}
    if 'companies' in url:
        params['properties'] = 'name,domain,hs_object_id' 
    elif 'contacts' in url:
        params['properties'] = 'firstname,lastname,email,hs_object_id'

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json().get('results', []) 
        paging = response.json().get('paging') 

        for item in results:
            aggregated_response.append(item)

        if paging and paging.get('next'):
            next_url = paging['next']['link']
            fetch_items(access_token, next_url, aggregated_response) 
    else:
        logger.error(f"Error fetching items from HubSpot: {response.status_code} - {response.text}")
        raise HTTPException(status_code=response.status_code, detail=f"Error fetching HubSpot items: {response.text}")


async def get_items_hubspot(credentials_str: str, entity_type: str):
    credentials = json.loads(credentials_str)
    access_token = credentials.get('access_token')

    if not access_token:
        raise HTTPException(status_code=400, detail="Access token not found in credentials.")

    hubspot_data = {
        "companies": [],
        "contacts": []
    }

    if entity_type == 'companies' or entity_type == 'all':
        company_url = 'https://api.hubapi.com/crm/v3/objects/companies'
        try:
            fetch_items(access_token, company_url, hubspot_data["companies"])
            logger.info(f"Fetched {len(hubspot_data['companies'])} companies for entity_type: {entity_type}.")
        except HTTPException as e:
            logger.error(f"Failed to fetch HubSpot companies: {e.detail}")
            raise e

    if entity_type == 'contacts' or entity_type == 'all':
        contact_url = 'https://api.hubapi.com/crm/v3/objects/contacts'
        try:
            fetch_items(access_token, contact_url, hubspot_data["contacts"])
            logger.info(f"Fetched {len(hubspot_data['contacts'])} contacts for entity_type: {entity_type}.")
        except HTTPException as e:
            logger.error(f"Failed to fetch HubSpot contacts: {e.detail}")
            raise e 

    if entity_type == 'companies':
        return {"companies": hubspot_data["companies"]}
    elif entity_type == 'contacts':
        return {"contacts": hubspot_data["contacts"]}
    else: 
        return hubspot_data
