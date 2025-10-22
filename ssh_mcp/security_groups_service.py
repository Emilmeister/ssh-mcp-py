import logging
import os

import requests


def get_security_groups_by_id(
        security_group_id: str,
        token: str
    ):
    response = requests.get(
        url=f'{os.getenv("CLOUD_RU_U_API_BASE_URL")}/svp/svc/v1/security-groups/{security_group_id}',
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    response = response.json()

    logging.info(f'get_security_groups_by_id {response}')

    return response


def get_security_groups_rules_by_id(
        security_group_id: str,
        token: str
    ):
    response = requests.get(
        url=f'{os.getenv("CLOUD_RU_U_API_BASE_URL")}/svp/svc/v1/security-groups/{security_group_id}/rules',
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    response = response.json()

    logging.info(f'get_security_groups_by_id {response}')

    return response['items']

def create_security_groups(
        name: str,
        description: str,
        availability_zone_id: str,
        project_id: str,
        token: str
    ):
        response = requests.post(
            url=f'{os.getenv("CLOUD_RU_U_API_BASE_URL")}/svp/svc/v1/security-groups',
            headers={"Authorization": f"Bearer {token}"},
            json={
                "project_id": project_id,
                "name": name,
                "availability_zone_id": availability_zone_id,
                "description": description,
                "security_group_rules": [
                    {
                        "direction": "ingress",
                        "description": "Разрешено подключение по ssh",
                        "ether_type": "IPv4",
                        "ip_protocol": "tcp",
                        "port_range": "22",
                        "remote_ip_prefix": "0.0.0.0/0"
                    },
                    {
                        "direction": "egress",
                        "description": "Разрешены все исходящие соединения",
                        "ether_type": "IPv4",
                        "ip_protocol": "any",
                        "port_range": "any",
                        "remote_ip_prefix": "0.0.0.0/0"
                    }
                ],
                "tag_ids": []
            }
        )
        response.raise_for_status()
        response = response.json()

        logging.info(f'create_security_groups {response}')

        return response

def create_security_groups_rule(
        security_group_id: str,
        token: str,
        description: str,
        port_range: str
    ):
    response = requests.post(
        url=f'{os.getenv("CLOUD_RU_U_API_BASE_URL")}/svp/svc/v1/security-groups/{security_group_id}/rules',
        headers={"Authorization": f"Bearer {token}"},
        json={
            "direction": "ingress",
            "description": description,
            "ether_type": "IPv4",
            "ip_protocol": "tcp",
            "port_range": port_range,
            "remote_ip_prefix": "0.0.0.0/0"
        },
    )
    response.raise_for_status()
    response = response.json()

    logging.info(f'create_security_groups_rule {response}')

    return response

def delete_security_groups_rule(
        security_group_id: str,
        security_group_rule_id: str,
        token: str
    ):
    response = requests.delete(
        url=f'{os.getenv("CLOUD_RU_U_API_BASE_URL")}/svp/svc/v1/security-groups/{security_group_id}/rules/{security_group_rule_id}',
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()

    logging.info(f'delete_security_groups_rule {response}')