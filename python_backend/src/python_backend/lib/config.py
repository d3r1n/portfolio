from os import environ

import toml

from python_backend.lib.util.singleton import SingletonMeta

# check the deployment mode in the environment variables
# Modes: PROD, DEV
try:
	deployment_mode = environ["DEPLOYMENT_MODE"]
except KeyError:
	# the environment variable is not set so we default to development mode
	deployment_mode = "DEV"


class Config(metaclass=SingletonMeta):
	"""Project configurations as singleton class.

	This class is used to access all configuration inside our `config.[mode].toml` files.

	Changing the configuration mode:
	    To change which file is used for the configuration mode you need to change the
	    `DEPLOYMENT_MODE` environment variable. The variable is set to `DEV` by default.

	    Available options for the variable are: `PROD`, `DEV`

	    - PROD: uses the `config.prod.toml` file for configuration
	    - DEV: uses the `config.dev.toml` file for configuration
	"""

	def __init__(self):
		# selecting the config file dependant on the deployment mode
		if deployment_mode == "DEV":
			file_name = "config.dev.toml"
		elif deployment_mode == "PROD":
			file_name = "config.prod.toml"
		else:
			raise RuntimeError(
				"Config file not found in path.\nMake sure you have `config.dev.toml` or `config.prod.toml` in root of python_backend directory."
			)

		self._data = toml.load(file_name)

	def __getitem__(self, key):
		return self._data[key]
