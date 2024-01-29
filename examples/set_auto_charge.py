"""Asynchronous Python client for TechnoVE."""

import asyncio

from technove import TechnoVE


async def main() -> None:
    """Show example on setting the automatic charging feature."""
    async with TechnoVE("192.168.10.162") as technove:
        print("Initial value:")
        device = await technove.update()
        initial_value = device.info.auto_charge
        print(initial_value)

        print("Activating auto_charge...")
        await technove.set_auto_charge(enabled=True)
        # Sleep is needed because the station takes a bit of time to fully
        # enable the automatic charging feature.
        await asyncio.sleep(2)
        device = await technove.update()
        print(device.info.auto_charge)

        print("Disabling auto_charge...")
        await technove.set_auto_charge(enabled=False)
        await asyncio.sleep(2)
        device = await technove.update()
        print(device.info.auto_charge)

        if device.info.auto_charge != initial_value:
            # Sets the initial value back, just to be nice
            print("Setting back to initial value...")
            await technove.set_auto_charge(enabled=initial_value)
            await asyncio.sleep(2)
            device = await technove.update()
            print(device.info.auto_charge)


if __name__ == "__main__":
    asyncio.run(main())
