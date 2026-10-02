"""Pure helpers shared by PanicStick and its tests; no macOS imports required."""
import copy
import re
from collections import deque

_EVENT_ID = re.compile(r"^[A-Za-z0-9_-]{1,32}$")


def validate_message(message, protocol="panicstick", version=1, minimum_hold_ms=2000, maximum_hold_ms=60000):
    """Accept only bounded messages that match the documented serial protocol."""
    if not isinstance(message, dict):
        return False
    if message.get("protocol") != protocol or message.get("version") != version:
        return False
    event = message.get("event")
    if event == "hello":
        return (
            isinstance(message.get("device", ""), str)
            and len(message.get("device", "")) <= 64
            and isinstance(message.get("firmware", ""), str)
            and len(message.get("firmware", "")) <= 32
            and isinstance(message.get("button_gpio", 0), int)
            and not isinstance(message.get("button_gpio", 0), bool)
            and 0 <= message.get("button_gpio", 0) <= 29
        )
    hold_ms = message.get("hold_ms")
    if not isinstance(hold_ms, int) or isinstance(hold_ms, bool) or hold_ms < 0:
        return False
    if event == "released":
        return hold_ms <= maximum_hold_ms * 10
    if event != "trigger" or not minimum_hold_ms <= hold_ms <= maximum_hold_ms:
        return False
    event_id = message.get("event_id")
    return isinstance(event_id, str) and bool(_EVENT_ID.fullmatch(event_id))


def _clean_names(value, key):
    if not isinstance(value, list) or len(value) > 30:
        raise ValueError(f"{key} must be a list of at most 30 app names")
    names = []
    for name in value:
        if not isinstance(name, str):
            raise ValueError(f"{key} entries must be text")
        name = name.strip()
        if not name or len(name) > 120 or any(ord(char) < 32 for char in name):
            raise ValueError(f"{key} contains an empty, overlong, or control-character name")
        if name not in names:
            names.append(name)
    return names


def normalize_config(config, defaults, allowed_actions):
    """Validate persisted settings and return a fresh, allow-listed copy."""
    if not isinstance(config, dict):
        raise ValueError("settings must be a JSON object")
    if config.get("version") != defaults["version"]:
        raise ValueError("unsupported settings version")
    actions = config.get("actions")
    if not isinstance(actions, list) or not actions or len(actions) > len(allowed_actions):
        raise ValueError("choose between one and the available number of actions")
    clean_actions = []
    seen = set()
    for item in actions:
        if not isinstance(item, dict):
            raise ValueError("each action must be an object")
        action_id = item.get("id")
        if not isinstance(action_id, str) or action_id not in allowed_actions:
            raise ValueError("settings include an unsupported action")
        if action_id not in seen:
            clean_actions.append({"id": action_id})
            seen.add(action_id)
    clean = copy.deepcopy(defaults)
    clean["actions"] = clean_actions
    mode = config.get("confirmation_mode", defaults.get("confirmation_mode", "before_run"))
    if mode not in ("before_run", "unattended"):
        raise ValueError("confirmation_mode must be before_run or unattended")
    clean["confirmation_mode"] = mode
    checkpoints = config.get("confirm_before", defaults.get("confirm_before", []))
    if not isinstance(checkpoints, list) or len(checkpoints) > len(allowed_actions):
        raise ValueError("confirm_before must be a list of action IDs")
    selected_ids = {item["id"] for item in clean_actions}
    clean["confirm_before"] = []
    for checkpoint in checkpoints:
        if not isinstance(checkpoint, str) or checkpoint not in allowed_actions:
            raise ValueError("confirm_before includes an unsupported action")
        if checkpoint in selected_ids and checkpoint not in clean["confirm_before"]:
            clean["confirm_before"].append(checkpoint)
    for key in ("on_insertion", "on_button_hold"):
        value = config.get(key, defaults[key])
        if not isinstance(value, bool):
            raise ValueError(f"{key} must be true or false")
        clean[key] = value
    clean["selected_apps"] = _clean_names(config.get("selected_apps", []), "selected_apps")
    clean["vm_apps"] = _clean_names(config.get("vm_apps", []), "vm_apps")
    shortcut = config.get("shortcut_name", defaults.get("shortcut_name", ""))
    if not isinstance(shortcut, str) or len(shortcut) > 120 or any(ord(c) < 32 for c in shortcut):
        raise ValueError("shortcut_name must be at most 120 characters")
    clean["shortcut_name"] = shortcut.strip()
    return clean


def ordered_actions(actions, order):
    """Return a stable copy with safety-critical steps (like shutdown) last."""
    return sorted(actions, key=lambda item: order.get(item["id"], 999))


class EventIdCache:
    """Bounded insertion-ordered de-duplication cache for serial trigger IDs."""

    def __init__(self, capacity=512):
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._queue = deque()
        self._ids = set()

    def add(self, event_id):
        """Return True for a new ID; False when it was seen in the retained window."""
        if event_id in self._ids:
            return False
        self._queue.append(event_id)
        self._ids.add(event_id)
        if len(self._queue) > self.capacity:
            self._ids.remove(self._queue.popleft())
        return True
