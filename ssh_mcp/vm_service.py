import logging
import os

import requests


def get_vm_info(headers: dict):
    response = requests.get(
        url=f'{os.getenv("CLOUD_RU_PUBLIC_API_BASE_URL")}/v1/vms/{headers["vm_id"]}',
        headers={"Authorization": f"Bearer {headers.get('token')}"}
    )
    response.raise_for_status()
    response = response.json()

    logging.info(f'vm_info {response}')

    hostname = response['name']
    user_name = 'not_found'

    for metadata_field in response['metadata_fields']:
        if 'name' in metadata_field and metadata_field['name'] == 'name':
            user_name = metadata_field['value']

    ip_address = 'public ip address not found'

    for interface in response['interfaces']:
        if 'type' in interface and interface['type'] == 'direct_ip':
            ip_address = interface['ip_address']

    return hostname, user_name, ip_address