from datetime import datetime, timedelta
from dotenv import load_dotenv
import os


# settings
os.environ["NODE_OPTIONS"] = "--no-deprecation"
load_dotenv()
chrome_bin = os.getenv("CHROME_PATH")
profile_folder = os.getenv("TEMP_PROFILE_NAME", "profile")
temp_base = os.environ.get("TEMP")
TEMP_PROFILE = os.path.normpath(os.path.join(temp_base, profile_folder))
datestamp = datetime.now().strftime("%d%m")
timestamp = datetime.now().strftime("%d%m%y_%H:%M:%S")
mr_date_today = (datetime.now()).strftime("%d.%m.%Y")
mr_date_future = (datetime.now() + timedelta(days=32)).strftime("%d.%m.%Y")

