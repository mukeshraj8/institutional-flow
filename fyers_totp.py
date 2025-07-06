import CredentialManager as cm
credentials = cm.CredentialManager()
totp_key=credentials.get_totp_object()

import time
import pyotp as tp
t=tp.TOTP(totp_key).now()
print(t)



