"""Load supported credentials from one explicit project-local dotenv file."""
import os
from pathlib import Path
import re
from .core import fail

SUPPORTED = {
    "GOOGLE_APPLICATION_CREDENTIALS", "GROWTH_GOOGLE_ACCESS_TOKEN",
    "GROWTH_APPLE_PRIVATE_KEY_PATH", "GROWTH_APPLE_ACCESS_TOKEN",
    "GROWTH_APPLE_KEY_ID", "GROWTH_APPLE_ISSUER_ID",
}
PATH_KEYS = {"GOOGLE_APPLICATION_CREDENTIALS", "GROWTH_APPLE_PRIVATE_KEY_PATH"}


def load_environment(path, required=False):
    """No shell execution or interpolation; existing process values always win."""
    path = Path(path).expanduser().absolute()
    try:
        text = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        if not required:
            return
        fail("env_file_missing", "The explicitly selected environment file does not exist.")
    except (OSError, UnicodeError):
        fail("invalid_env", "Cannot read the environment file as UTF-8.")
    values = {}
    for line_number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)", line)
        if not match:
            fail("invalid_env", f"Invalid environment assignment on line {line_number}; use KEY=VALUE.")
        key, value = match.groups()
        if value.startswith(("'", '"')):
            end = value.find(value[0], 1)
            if end == -1 or (value[end+1:].strip() and not value[end+1:].strip().startswith("#")):
                fail("invalid_env", f"Invalid quoted value on line {line_number}; use a single-line literal without escaped quotes.")
            value = value[1:end]
        else:
            value = re.split(r"\s+#", value, maxsplit=1)[0].rstrip()
            if value.startswith("#"):
                value = ""
        if "\x00" in value:
            fail("invalid_env", f"Invalid environment value on line {line_number}.")
        if key in SUPPORTED:
            if key in values:
                fail("invalid_env", f"Duplicate credential assignment on line {line_number}.")
            if key in PATH_KEYS and value:
                location = Path(value).expanduser()
                value = str(location if location.is_absolute() else path.parent / location)
            values[key] = value
    # Validate the entire file before changing the process environment.
    for key, value in values.items():
        if value:
            os.environ.setdefault(key, value)
