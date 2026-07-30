from portfolio.core.config import load_config
from portfolio.integrations.registry import Integrations


async def test_create_wires_all_clients_to_one_session():
	integrations = Integrations.create(load_config())
	try:
		assert integrations.spotify._session is integrations.session
		assert integrations.hardcover._session is integrations.session
		assert integrations.openweather._session is integrations.session
	finally:
		await integrations.close()

	assert integrations.session.closed
