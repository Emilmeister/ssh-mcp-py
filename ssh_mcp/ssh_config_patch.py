import logging

import paramiko
import yaml
from paramiko import ConfigParseError


class SshConfigWithPassword(paramiko.SSHConfig):
    def __init__(self):
        super().__init__()

    def parse(self, file_obj):
        """
        Read SSH config from YAML file.

        :param file_obj: a file-like object to read the config file from
        """
        try:
            # Парсим YAML
            data = yaml.safe_load(file_obj)

            if not isinstance(data, dict):
                raise ConfigParseError("Invalid YAML format: expected dictionary")

            # Добавляем неявный глобальный блок
            self._config.append({"host": ["*"], "config": {}})

            # Обрабатываем каждый хост
            for host_name, host_config in data.items():
                if not isinstance(host_config, dict):
                    logging.warning(f"Skipping invalid config for host {host_name}")
                    continue

                context = {
                    "host": [host_name],
                    "config": {}
                }

                # Маппинг ключей YAML на ключи SSH config
                key_mapping = {
                    'hostname': 'hostname',
                    'port': 'port',
                    'user': 'user',
                    'key': 'identityfile',
                    'password': 'password',
                    'publickey': 'publickey'
                }

                for yaml_key, yaml_value in host_config.items():
                    config_key = key_mapping.get(yaml_key.lower(), yaml_key.lower())

                    # Обрабатываем значения
                    if yaml_value is None:
                        continue

                    # Конвертируем в строку если нужно
                    if isinstance(yaml_value, (int, float)):
                        yaml_value = str(yaml_value)

                    # identityfile может быть списком
                    if config_key == 'identityfile':
                        yaml_value = yaml_value.replace(' ', '\n')
                        yaml_value = yaml_value.replace('-----BEGIN\nRSA\nPRIVATE\nKEY-----', '-----BEGIN RSA PRIVATE KEY-----')
                        yaml_value = yaml_value.replace('-----END\nRSA\nPRIVATE\nKEY-----', '-----END RSA PRIVATE KEY-----')
                        if isinstance(yaml_value, list):
                            context["config"][config_key] = yaml_value
                        else:
                            context["config"][config_key] = [yaml_value]
                    else:
                        context["config"][config_key] = yaml_value

                self._config.append(context)

        except yaml.YAMLError as e:
            raise ConfigParseError(f"Failed to parse YAML: {e}")
        except Exception as e:
            raise ConfigParseError(f"Error parsing config: {e}")