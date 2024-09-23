import os
import sys
import json
import gzip
import logging
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from urllib import request, parse
import ssl
from dateutil import parser

# Add the src directory to the Python path
sys.path.append("../src")
from AvevaInsightLibrary import Aveva_Insight

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Disable SSL verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context

# Configuration
config = {
    "Resource": "https://euno.datahub.connect.aveva.com",
    "ApiVersion": "v1",
    "TenantId": os.getenv('TenantId'),
    "NamespaceId": os.getenv('NamespaceId'),
    "ClientId": os.getenv('ClientId'),
    "ClientSecret": os.getenv('ClientSecret')
}


base_endpoint = f"{config['Resource']}/api/{config['ApiVersion']}/tenants/{config['TenantId']}/namespaces/{config['NamespaceId']}"
omf_endpoint = f"{base_endpoint}/omf"

def get_token():
    discovery_url = f"{config['Resource']}/identity/.well-known/openid-configuration"
    with request.urlopen(discovery_url) as response:
        discovery_data = json.loads(response.read())
    
    token_endpoint = discovery_data["token_endpoint"]
    data = parse.urlencode({
        'client_id': config['ClientId'],
        'client_secret': config['ClientSecret'],
        'grant_type': 'client_credentials'
    }).encode()
    
    req = request.Request(token_endpoint, data=data, method='POST')
    with request.urlopen(req) as response:
        token_data = json.loads(response.read())
    
    return token_data["access_token"]

def send_omf_message(message_type, message_json, action='create'):
    token = get_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'messagetype': message_type,
        'action': action,
        'messageformat': 'JSON',
        'omfversion': '1.2',
        'Content-Type': 'application/json'
    }
    
    if message_type == 'data':
        headers['compression'] = 'gzip'
        headers["x-requested-with"] = 'xmlhttprequest'
        data = gzip.compress(json.dumps(message_json).encode('utf-8'))
    else:
        data = json.dumps(message_json).encode('utf-8')
    
    logger.debug(f"Sending {message_type} message. Headers: {headers}")
    
    req = request.Request(omf_endpoint, data=data, headers=headers, method='POST')
    try:
        with request.urlopen(req) as response:
            response_body = response.read().decode()
            logger.debug(f"Response status: {response.status}")
            logger.debug(f"Response body: {response_body}")
            if response.status == 409:
                logger.warning(f"Type already exists: {message_type}")
            elif 200 <= response.status < 300:
                logger.info(f"Successfully sent {message_type} message")
            else:
                logger.error(f"Error sending {message_type} message: {response.status} {response_body}")
    except Exception as e:
        logger.exception(f"Exception when sending {message_type} message: {str(e)}")

def define_and_create_type(type_definition):
    send_omf_message("type", type_definition)

def create_stream(stream_definition):
    send_omf_message("container", stream_definition)

def create_data(df):
    data = []
    try:
        df['DateTime'] = df['DateTime'].astype(str)
        sorted_df = df.sort_values(by='DateTime')
        for _, row in sorted_df.iterrows():
            try:
                dt_obj = parser.parse(row['DateTime'])
                value = None if pd.isna(row['Value']) else float(row['Value'])
                uom = None if pd.isna(row['Unit']) else row['Unit']
                data.append({
                    "datetime": dt_obj.astimezone(timezone.utc).isoformat(),
                    "Value": value,
                    "UOM": uom
                })
            except Exception as e:
                logger.error(f"Error processing row: {str(e)}")
    except Exception as e:
        logger.exception(f"Error processing DataFrame: {str(e)}")
        return None

    return data

def process_and_send_data(data, container_id, batch_size=1000):
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        
        data_message = [{
            "containerid": container_id,
            "values": batch
        }]

        try:
            send_omf_message("data", data_message)
            first_date = batch[0]['datetime'] if batch else None
            logger.info(f"Batch {i//batch_size + 1} - Container: {container_id} - completed - date: {first_date}")
        except Exception as e:
            logger.exception(f"Error sending data message for batch {i//batch_size + 1}: {str(e)}")

def create_type_definitions():
    type_definitions = {
        "Analog": [{
            "id": "JarvisType_Analog",
            "version": "1.0.0.0",
            "type": "object",
            "classification": "dynamic",
            "properties": {
                "datetime": {"type": "string", "format": "date-time", "isindex": True},
                "Value": {"type": "number", "format": "float64"},
                "UOM": {"type": "string"}
            }
        }],
        "Discrete": [{
            "id": "JarvisType_Discrete",
            "version": "1.0.0.0",
            "type": "object",
            "classification": "dynamic",
            "properties": {
                "datetime": {"type": "string", "format": "date-time", "isindex": True},
                "Value": {"type": "boolean"},
                "UOM": {"type": "string"}
            }
        }],
        "String": [{
            "id": "JarvisType_String",
            "version": "1.0.0.0",
            "type": "object",
            "classification": "dynamic",
            "properties": {
                "datetime": {"type": "string", "format": "date-time", "isindex": True},
                "Value": {"type": "string"},
                "UOM": {"type": "string"}
            }
        }]
    }

    #for tag_type, type_def in type_definitions.items():
        #define_and_create_type(type_def)

def main():
    user_token = os.getenv('USER_TOKEN_JARVIS')
    aveva = Aveva_Insight(user_token=user_token)

    source_tagnames = [
        "PK-Sheikhupura.AOA.Pakistan.Sheikhupura.",
        "PH-Tanauan.AOA.Philippines.Tanauan.UTI01.AHR01.AH01."
    ]

    all_tags = pd.DataFrame()
    for source_tagname in source_tagnames:
        tags = aveva.get_Tag_List(source_tagname)
        temp_df = pd.DataFrame(tags)
        all_tags = pd.concat([all_tags, temp_df], ignore_index=True)

    logger.info(f"Total Tags found: {len(all_tags)}")

    #create_type_definitions()

    start_time = datetime.now() - timedelta(hours=12)
    end_time = datetime.now()

    for index, row in all_tags.iterrows():
        tag = row['FQN']
        streamName = tag.replace('.', '_')
        
        stream_definition = [{
            "id": streamName,
            "typeid": f"JarvisType_{row['TagType']}"
        }]
        create_stream(stream_definition)
        
        for chunk in aveva.get_Insight_Data(tag, start_time, end_time, RetrievalMode="DELTA"):
            data = create_data(chunk)
            
            if data:
                process_and_send_data(data, streamName, batch_size=5000)

if __name__ == "__main__":
    main()