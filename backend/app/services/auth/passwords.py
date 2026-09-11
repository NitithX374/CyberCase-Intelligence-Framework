import hashlib
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    algorithm, salt, expected = stored.split("$")
    if algorithm != "scrypt":
        raise ValueError("Unsupported password hash")
    digest = hashlib.scrypt(
        password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1
    )
    return secrets.compare_digest(digest.hex(), expected)


hashPassword = hash_password
verifyPassword = verify_password

__all__ = ["hashPassword", "hash_password", "verifyPassword", "verify_password"]
