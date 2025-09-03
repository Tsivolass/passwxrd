import asyncio
from winsdk.windows.security.credentials.ui import UserConsentVerifier

async def _require_windows_hello():
    availability = await UserConsentVerifier.check_availability_async()
    if availability != 0:
        return True
    result = await UserConsentVerifier.request_verification_async("Get access to  Passwxrd")
    return result == 0

def require_windows_hello():
    return asyncio.run(_require_windows_hello())
