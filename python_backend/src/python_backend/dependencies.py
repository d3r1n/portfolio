from aiohttp import ClientSession


class ClientSessionManager:
	def __init__(self):
		self._session: ClientSession | None = None
		self.references: int = 0

	def startup(self):
		self._session = ClientSession()

	def get_session(self) -> ClientSession:
		if not self._session:
			raise RuntimeError("Client Session not initialized, call startup() first.")

		self.references += 1
		return self._session

	async def shutdown(self):
		if self._session:
			await self._session.close()


CLIENT_SESSION = ClientSessionManager()


def get_client_session() -> ClientSession:
	return CLIENT_SESSION.get_session()
