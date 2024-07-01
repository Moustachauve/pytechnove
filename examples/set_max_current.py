"""Asynchronous Python client for TechnoVE."""

import asyncio

from technove import MIN_CURRENT, TechnoVE


async def main() -> None:
    """Show example on setting the max current of a station."""
    async with TechnoVE("192.168.10.162") as technove:
        print("Initial value:")
        device = await technove.update()
        initial_value = device.info.max_current
        print(initial_value)

        print("Setting max current to maximum...")
        await technove.set_max_current(device.info.max_station_current)
        # Sleep is needed because the station takes a bit of time to fully
        # set the correct value.
        await asyncio.sleep(10)
        device = await technove.update()
        print(device.info.max_current)

        print("Setting max current to minimum...")
        await technove.set_max_current(MIN_CURRENT)
        await asyncio.sleep(10)
        device = await technove.update()
        print(device.info.max_current)

        print("Setting max current to odd value...")
        await technove.set_max_current(15)
        await asyncio.sleep(10)
        device = await technove.update()
        print(device.info.max_current)

        if device.info.max_current != initial_value:
            # Sets the initial value back, just to be nice
            print("Setting back to initial value...")
            await technove.set_max_current(initial_value)
            await asyncio.sleep(10)
            device = await technove.update()
            print(device.info.max_current)


if __name__ == "__main__":
    asyncio.run(main())
