import logging
import os

import requests


def get_vm_info(vm_id: str, token: str):
    response = requests.get(
        url=f'{os.getenv("CLOUD_RU_PUBLIC_API_BASE_URL")}/v1/vms/{vm_id}',
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    response = response.json()

    logging.info(f'vm_info {response}')

    hostname = response['name']
    availability_zone_id = response['availability_zone']['id']
    user_name = 'not_found'

    for metadata_field in response['metadata_fields']:
        if 'name' in metadata_field and metadata_field['name'] == 'name':
            user_name = metadata_field['value']

    ip_address = 'public ip address not found'
    security_groups = []
    interface_id = ''

    for interface in response['interfaces']:

        if 'type' in interface and interface['type'] == 'regular':
            interface_id = interface['id']
            ip_address = interface['floating_ip']['ip_address']
            security_groups = interface['security_groups']

        if 'type' in interface and interface['type'] == 'direct_ip':
            interface_id = interface['id']
            ip_address = interface['ip_address']
            security_groups = interface['security_groups']

    return (
        hostname,
        user_name,
        ip_address,
        security_groups,
        availability_zone_id,
        interface_id
    )