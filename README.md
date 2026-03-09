# Namoz IM Bot

Telegram bot for prayer times based on user location.

Prayer time data source: [Aladhan Prayer Times API](https://aladhan.com/prayer-times-api).

## What was modernized
- Dependency set updated for modern Python and current Telegram API wrapper.
- `urllib3` explicitly pinned to `>=2.6.3` to address current GHSA advisories.
- Configuration supports `.env` (with backward compatibility for legacy `config.py`).
- Safer API handling: request timeout, status checks, and clear failure responses.
- Time parsing and current-prayer calculation simplified and made deterministic.
- Removed duplicate/unsafe logic and improved logging.
- Added in-bot `/settings` with language switch (`UZ`, `TR`, `RU`, `EN`) and Asr mode switch:
  - `Early Asr (Standard)` -> `school=0`
  - `Delayed Asr (Hanafi)` -> `school=1`

## Requirements
- Python 3.10+

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Create environment file:
```bash
cp .env.example .env
```
3. Fill `.env` values:
- `NAMOZ_BOT_TOKEN`: Telegram token from `@BotFather`
- `NAMOZ_ADMIN_ID`: your Telegram chat id (optional, `0` disables forwarding)

4. Run:
```bash
python3 namozimbot.py
```

## Legacy config support
If you already use a `config.py` with `namozbottoken`, `namozapibase`, `namozadmin`, it still works.

## License
MIT. See `LICENSE`.
