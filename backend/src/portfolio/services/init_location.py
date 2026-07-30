from ..database import Database


async def init_current_location(db: Database):
	# Reset and reseed atomically so a crash mid-init can't leave the table empty.
	async with db.transaction():
		if await db.locations.get_current() is not None:
			# reset
			await db.locations.clear()

		# initalize placeholder location
		await db.locations.set_current(
			location_name="Sackville, New Brunswick",
			latitude=45.897820,
			longitude=-64.368279,
		)
