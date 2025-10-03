from dotenv import load_dotenv

load_dotenv()


def main():
    from ssh_mcp import mcp_main

    mcp.run()
