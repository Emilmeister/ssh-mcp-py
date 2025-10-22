import logging
import os
from typing import List

import requests




def update_interface(
        interface_id: str,
        security_group_ids: List[str],
        token: str
    ):

    response = requests.put(
        url=f'{os.getenv("CLOUD_RU_U_API_BASE_URL")}/svp/svc/v1/interfaces/{interface_id}',
        headers={"Authorization": f"Bearer {token}"},
        json={
            "security_groups": security_group_ids
        }
    )
    response.raise_for_status()
    response = response.json()

    logging.info(f'create_security_groups_rule {response}')

    return response