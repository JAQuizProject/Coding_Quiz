import secrets
import time


# Crockford's Base32 alphabet (no I, L, O, U).
_CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def generate_ulid(timestamp_ms: int | None = None) -> str:
    """Generate a ULID string (26 chars).

    Notes:
    - ULID is 128 bits: 48-bit timestamp (ms) + 80-bit randomness.
    - We generate ULIDs in Python to avoid DB-specific functions (SQLite/Postgres).
    """

    ts_ms = int(time.time() * 1000) if timestamp_ms is None else int(timestamp_ms)
    if ts_ms < 0 or ts_ms >= 2**48:
        raise ValueError("timestamp_ms out of range for ULID (must fit in 48 bits)")

    rand = secrets.token_bytes(10)  # 80 bits
    value = (ts_ms << 80) | int.from_bytes(rand, "big")

    # 128 bits -> 26 base32 chars (26 * 5 = 130 bits, leading zeros are kept).
    chars: list[str] = []
    for _ in range(26):
        chars.append(_CROCKFORD_BASE32[value & 0x1F])
        value >>= 5
    return "".join(reversed(chars))

