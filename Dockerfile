FROM python:3.10

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml pyproject.toml

RUN pip install poetry \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi --no-root

ENV MCP_TRANSPORT=sse

COPY ssh_mcp ssh_mcp

CMD poetry run python ssh_mcp/mcp_main.py