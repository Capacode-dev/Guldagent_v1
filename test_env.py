from dotenv import load_dotenv
import os

load_dotenv()

print("MODTAGER:", os.getenv("HEMMELIG_MODTAGER"))
print("AFSENDER:", os.getenv("HEMMELIG_AFSENDER"))
print("BRIDGE USER:", os.getenv("BRIDGE_USERNAME"))
print("BRIDGE PASS:", os.getenv("BRIDGE_PASSWORD"))
