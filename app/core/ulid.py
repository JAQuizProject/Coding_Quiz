import secrets

from ulid import ULID


def is_valid_ulid(value: str) -> bool:
    if not isinstance(value, str) or len(value) != 26:
        return False
    try:
        ULID().decode(value)
    except (TypeError, ValueError):
        return False
    return True


def generate_ulid(timestamp_ms: int | None = None) -> str:
    """Generate a ULID string."""

    if timestamp_ms is None:
        return ULID().generate()

    ts_ms = int(timestamp_ms)
    if ts_ms < 0 or ts_ms >= 2**48:
        raise ValueError("timestamp_ms out of range for ULID (must fit in 48 bits)")

    # Compose a 128-bit ULID value and encode it via py-ulid.
    rand80 = secrets.randbits(80)
    value = (ts_ms << 80) | rand80
    return ULID().encode(value)
