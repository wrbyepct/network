"""Post Service."""


def get_like_stat(like_count, liked):
    """Return dynamic like stat string to display at the frontend."""
    if like_count == 0:
        return ""

    if liked:
        if like_count == 1:
            return "You"
        return f"You and {like_count - 1} others"

    return like_count
