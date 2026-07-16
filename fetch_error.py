import urllib.request
import urllib.error

try:
    response = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/tasks")
    print(response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print(e.read().decode())
except Exception as e:
    print("Error:", e)
