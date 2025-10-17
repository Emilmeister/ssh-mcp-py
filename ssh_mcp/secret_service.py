import base64
import logging
import os

import requests


def get_secret_last_version(secret_id: str, token: str, project_id: str):
    response = requests.get(
        url=f'{os.getenv("CLOUD_RU_SECRET_API_BASE_URL")}/v1/secrets/{secret_id}',
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    response = response.json()

    logging.info(f'Просмотр секрета={response}')

    name = response['name']

    response = requests.get(
        url=f'{os.getenv("CLOUD_RU_SECRET_API_BASE_URL")}/v1/secrets/{secret_id}/versions',
        headers={"Authorization": f"Bearer {token}"},
        params={
            "page.limit": 1000,
            "page.offset": 0,
        }
    )

    response.raise_for_status()
    response = response.json()

    logging.info(f'Просмотр версий={response}')

    version_id = response['versions'][-1]['id']


    response = requests.get(
        url=f'{os.getenv("CLOUD_RU_SECRET_API_BASE_URL")}/v2/version/{name}',
        headers={"Authorization": f"Bearer {token}"},
        params={
            "projectId": project_id,
            "version": version_id,
            "jsonPath": "",
        }
    )

    response.raise_for_status()
    response = response.json()
    return base64.b64decode(response['payload']).decode('utf-8')