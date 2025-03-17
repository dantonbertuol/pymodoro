from dotenv import load_dotenv
import os
import platform

load_dotenv()

MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_USER = os.getenv("MONGODB_USER")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
IS_DEV = False

# Se estivermos no ambiente de desenvolvimento do VSCode
if "vscode" in os.environ.get("TERM_PROGRAM", ""):
    ICON_PATH = "utils/pymodoro_icon.ico"
    ICON_PATH_RUNNING = "utils/pymodoro_icon_running.ico"
    ICON_PATH_PAUSE = "utils/pymodoro_icon_pause.ico"
    DARKMODE_PATH = "utils/pymodoro_darkmode.qss"
    LIGHTMODE_PATH = "utils/pymodoro_lightmode.qss"
    NOTIFICATION_SOUND_PATH = "utils/notification.wav"
    SETTINGS_PATH = "utils/pymodoro_settings.json"
    SQLITE_DATABASE_PATH = "utils/pymodoro.db"
    IS_DEV = True
else:
    if platform.system() == "Linux":
        from pwd import getpwnam  # type: ignore

        HOME_PATH = getpwnam(os.getlogin()).pw_dir
        UTILS_PATH = f"{HOME_PATH}/.local/bin/pymodoro_utils"
        ICON_PATH = f"{UTILS_PATH}/pymodoro_icon.ico"
        ICON_PATH_RUNNING = f"{UTILS_PATH}/pymodoro_icon_running.ico"
        ICON_PATH_PAUSE = f"{UTILS_PATH}/pymodoro_icon_pause.ico"
        DARKMODE_PATH = f"{UTILS_PATH}/pymodoro_darkmode.qss"
        LIGHTMODE_PATH = f"{UTILS_PATH}/pymodoro_lightmode.qss"
        NOTIFICATION_SOUND_PATH = f"{UTILS_PATH}/notification.wav"
        SETTINGS_PATH = f"{UTILS_PATH}/pymodoro_settings.json"
        SQLITE_DATABASE_PATH = f"{UTILS_PATH}/pymodoro.db"
    elif platform.system() == "Windows":
        UTILS_PATH = f"C:/Users/{os.getenv('USERNAME')}/AppData/Local/Pymodoro/pymodoro_utils"
        ICON_PATH = f"{UTILS_PATH}/pymodoro_icon.ico"
        ICON_PATH_RUNNING = f"{UTILS_PATH}/pymodoro_icon_running.ico"
        ICON_PATH_PAUSE = f"{UTILS_PATH}/pymodoro_icon_pause.ico"
        DARKMODE_PATH = f"{UTILS_PATH}/pymodoro_darkmode.qss"
        LIGHTMODE_PATH = f"{UTILS_PATH}/pymodoro_lightmode.qss"
        NOTIFICATION_SOUND_PATH = f"{UTILS_PATH}/notification.wav"
        SETTINGS_PATH = f"{UTILS_PATH}/pymodoro_settings.json"
        SQLITE_DATABASE_PATH = f"{UTILS_PATH}/pymodoro.db"
    elif platform.system() == "Darwin":
        HOME_PATH = os.getenv("HOME")
        UTILS_PATH = f"{HOME_PATH}/.config/pymodoro"
        ICON_PATH = f"{UTILS_PATH}/pymodoro_icon.ico"
        ICON_PATH_RUNNING = f"{UTILS_PATH}/pymodoro_icon_running.ico"
        ICON_PATH_PAUSE = f"{UTILS_PATH}/pymodoro_icon_pause.ico"
        DARKMODE_PATH = f"{UTILS_PATH}/pymodoro_darkmode.qss"
        LIGHTMODE_PATH = f"{UTILS_PATH}/pymodoro_lightmode.qss"
        NOTIFICATION_SOUND_PATH = f"{UTILS_PATH}/notification.wav"
        SETTINGS_PATH = f"{UTILS_PATH}/pymodoro_settings.json"
        SQLITE_DATABASE_PATH = f"{UTILS_PATH}/pymodoro.db"
    else:
        raise NotImplementedError("Sistema operacional não suportado")
