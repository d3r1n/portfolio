# TODO

- [ ] Implement browser sessions
    - [ ] need a database to store the session data (ip, device, location)
    - [ ] have a blacklist store
- [ ] Implement rate limiting
- [ ] Put frequent rate limiters to blacklisted ips
- [ ] add a scraper/ai deterer (anubis)
- [ ] mini analytics (basic information only for monitoring activity) \
       country, device platform (mobile, desktop, etc.), visit count, average interaction interval

---

- [x] What database to select?
    > requirements: lightweight, easily deployable for containers, SQL, easy to use, modern \
    > verdict: use redis for security and sessions, sqlite (or a modern equivalent) for analytics
