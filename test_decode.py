import urllib.parse
import base64
import json

s = "CAESYwHrOzAVDFJZfvLQupia7dGlfPE-0hNmA_hUw1Ep_bqBXFbjsG3Kq6okAsKTqCz6-nqbrfUYhXL4-cXuEsY8lT-kxypkWE49WVhQQbcvS78A6Fjqf4e35GRHnHH0qExze8u42w"

print("Unquote:", urllib.parse.unquote(s))
try:
    padded = s + '=' * (4 - len(s) % 4)
    b = base64.urlsafe_b64decode(padded)
    print("Base64 bytes:", b)
    print("Base64 string:", b.decode('utf-8', errors='ignore'))
except Exception as e:
    print("Base64 error:", e)
