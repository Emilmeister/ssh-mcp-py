# MCP для работы с виртуальными машинами через командную строку

### Для запуска нужно:

1. Поправить файл config.yaml добавив туда свои настройки
2. Закинуть base64 кодированный текст из config.yaml в переменную SSH_CONFIG
3. Выполнить ```docker compose build && docker compose up -d```
4. MCP sse сервер развернется на порту 8000

Дока по opensource версии хранится в файле README_old.md https://github.com/sondt2709/ssh-mcp-py
