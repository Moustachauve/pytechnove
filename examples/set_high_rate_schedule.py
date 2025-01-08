"""Asynchronous Python client for TechnoVE."""

import asyncio

from technove import TechnoVE


async def main() -> None:
    """Show example on setting the max current of a station."""
    async with TechnoVE("192.168.10.162") as technove:
        print("Initial value:")
        device = await technove.update()
        initial_value = device.info.high_charge_period_active
        print(initial_value)

        print("Activating high rate schedule...")
        await technove.set_high_rate_schedule(enabled=True)
        # Sleep is needed because the station takes a bit of time to fully
        # enable the automatic charging feature.
        await asyncio.sleep(2)
        device = await technove.update()
        print(device.info.high_charge_period_active)

        print("Disabling auto_charge...")
        await technove.set_high_rate_schedule(enabled=False)
        await asyncio.sleep(2)
        device = await technove.update()
        print(device.info.high_charge_period_active)

        if device.info.high_charge_period_active != initial_value:
            # Sets the initial value back, just to be nice
            print("Setting back to initial value...")
            await technove.set_high_rate_schedule(enabled=initial_value)
            await asyncio.sleep(2)
            device = await technove.update()
            print(device.info.high_charge_period_active)


if __name__ == "__main__":
    asyncio.run(main())
