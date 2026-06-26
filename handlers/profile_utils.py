from database.models import User


def format_user_profile(
    user: User,
    title: str = "👤 پروفایل شما",
    show_coins: bool = False,
) -> str:
    vip_badge = " 💎" if user.vip else ""
    lines = [
        f"{title}{vip_badge}\n",
        f"🎂 سن: {user.age or 'ثبت نشده'}",
        f"🚻 جنسیت: {user.gender or 'ثبت نشده'}",
        f"🌍 کشور: {user.country or 'ثبت نشده'}",
        f"📝 بیو:\n{user.bio or 'ثبت نشده'}",
    ]
    if show_coins:
        lines.append(f"🪙 سکه: {user.coins}")
    return "\n".join(lines)
