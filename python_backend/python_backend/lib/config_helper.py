from os import environ
from typing import Self

import toml

# check the deployment mode in the environment variables
# Modes: PROD, DEV
try:
	DEPLOYMENT_MODE = environ["DEPLOYMENT_MODE"]
except KeyError:
	# the environment variable is not set so we default to development mode
	DEPLOYMENT_MODE = "DEV"


class Config:
	"""Project configurations as singleton class.

	This class is used to access all configuration inside our `config.[mode].toml` files.

	Changing the configuration mode:
	    To change which file is used for the configuration mode you need to change the
	    `DEPLOYMENT_MODE` environment variable. The variable is set to `DEV` by default.

	    Available options for the variable are: `PROD`, `DEV`

	    - PROD: uses the `config.prod.toml` file for configuration
	    - DEV: uses the `config.dev.toml` file for configuration
	"""

	_instance: Self | None = None  # set the instance to None when created

	def __new__(cls):
		# if the instance is None, create a new instance
		if cls._instance is None:
			cls._instance = super(Config, cls).__new__(cls)

			# selecting the config file dependant on the deployment mode
			if DEPLOYMENT_MODE == "DEV":
				file_name = "config.dev.toml"
			elif DEPLOYMENT_MODE == "PROD":
				file_name = "config.prod.toml"
			else:
				raise RuntimeError("Config file not found in path.")

			toml_data = toml.load(file_name)

			cls._data = toml_data

		return cls._instance

	def __getitem__(self, key):
		return self._data[key]
