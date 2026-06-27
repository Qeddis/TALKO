def parse_referrer_id(start_args: str | None) -> int | None:
    if not start_args:
        return None
    raw = start_args.strip()
    if raw.startswith("ref") and raw[3:].isdigit():
        return int(raw[3:])
    if raw.isdigit():
        return int(raw)
    return None


def referral_link(bot_username: str, user_id: int) -> str:
    return f"https://t.me/{bot_username}?start=ref{user_id}"
