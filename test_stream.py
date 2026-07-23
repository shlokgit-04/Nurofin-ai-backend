from dotenv import load_dotenv
import os
from stream_chat import StreamChat

load_dotenv(".env")
api_key = os.getenv("STREAM_API_KEY")
api_secret = os.getenv("STREAM_API_SECRET")

print("Key:", api_key)
if api_secret: print("Secret len:", len(api_secret))

try:
    client = StreamChat(api_key=api_key, api_secret=api_secret)
    client.upsert_user({"id": "3", "name": "Test", "role": "admin"})
    token = client.create_token("3")
    print("Success! Token:", token)
except Exception as e:
    print("Error:", str(e))
