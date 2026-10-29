
import asyncio
from copilot import CopilotClient


async def main():
    client = CopilotClient()

    try:
        await client.start()

        session = await client.create_session(model="auto")

        response = await session.send_and_wait(
            "Reply with exactly: Hello from GitHub Copilot"
        )

        print("Response:", response.data.content)

    finally:
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
