import httpx


class API:
    def __init__(
            self,
            device_ip
    ):
        self.device_ip = device_ip

    async def get_current_state(self):
        async with httpx.AsyncClient() as client:
            request = await client.get('http://{}/station/get/info'.format(self.device_ip))
            return request.json()
