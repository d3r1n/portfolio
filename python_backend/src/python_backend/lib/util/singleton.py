import threading


class ThreadSafeSingletonMeta(type):
	"""Thread-safe Singleton metaclass."""

	_instances = {}
	_lock = threading.Lock()  # one lock shared across all singleton classes

	def __call__(cls, *args, **kwargs):
		# Double-checked locking
		if cls not in cls._instances:
			with cls._lock:
				if cls not in cls._instances:
					cls._instances[cls] = super().__call__(*args, **kwargs)
		return cls._instances[cls]


class SingletonMeta(type):
	"""Singleton metaclass."""

	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super().__call__(*args, **kwargs)
		return cls._instances[cls]
