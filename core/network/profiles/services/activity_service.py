"""Activity general service."""

from .activity_reader import evaluate_activity_status
from .activity_writer import increment_active_count, update_last_request


def update_activity_state(user_id, is_active_request):
    """Update user activity counters & timestamps based on request type."""
    if is_active_request:
        increment_active_count(user_id)
    update_last_request(user_id)


def get_current_activity_status(user):
    """Public read API for views/templates."""
    return evaluate_activity_status(user)


ACTIVITY_OBJECT = {
    "swimming": {"emoji": "🏊‍♂️", "color": "text-blue-500", "status": "Swimming"},
    "resting": {"emoji": "😴", "color": "text-gray-500", "status": "Resting"},
    "exploring": {"emoji": "🧭", "color": "text-green-500", "status": "Exploring"},
    "sunbathing": {"emoji": "🌞", "color": "text-yellow-500", "status": "Sunbathing"},
    "hiding_in_shell": {
        "emoji": "🐢",
        "color": "text-slate-600",
        "status": "Hiding in shell",
    },
}


def get_activity_obj(user):
    """Return activity object."""
    status = evaluate_activity_status(user)
    if status in ACTIVITY_OBJECT:
        return ACTIVITY_OBJECT[status]
    return None
