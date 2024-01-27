"""Asynchronous Python client for TechnoVE."""

import asyncio

from technove import TechnoVE


async def main() -> None:
    """Show example on getting infos from your TechnoVE station."""
    async with TechnoVE("192.168.10.162") as technove:
        device = await technove.update()
        print(device.info.name)
        print(device.info.version)

        print(device.info)


if __name__ == "__main__":
    asyncio.run(main())
