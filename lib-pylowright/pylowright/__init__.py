import os

T_TIMEOUT_SHORT = int(os.getenv("PW_TIMEOUT_SHORT", "5"))
T_TIMEOUT_DEFAULT = int(os.getenv("PW_TIMEOUT_DEFAULT", "30"))
T_TIMEOUT_LONG = int(os.getenv("PW_TIMEOUT_LONG", "120"))
