"""
strava_auth.py
──────────────
One-time script to get a Strava refresh token with activity:read_all scope.

Run once:  python strava_auth.py
It will open your browser, ask you to authorize, then save the new
refresh token into your .env file automatically.
"""

import http.server
import os
import threading
import urllib.parse
import webbrowser
from pathlib import Path

import requests
from dotenv import load_dotenv, set_key

load_dotenv()

CLIENT_ID     = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
ENV_PATH      = Path(__file__).parent / ".env"

REDIRECT_URI  = "http://localhost:8765/callback"
SCOPE         = "activity:read_all"

auth_code = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family:monospace;padding:40px">
                <h2>Authorization successful!</h2>
                <p>You can close this tab and return to the terminal.</p>
                </body></html>
            """)
        else:
            error = params.get("error", ["unknown"])[0]
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body>Error: {error}</body></html>".encode())

    def log_message(self, format, *args):
        pass  # suppress server logs


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise SystemExit("Missing STRAVA_CLIENT_ID or STRAVA_CLIENT_SECRET in .env")

    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&approval_prompt=force"
        f"&scope={SCOPE}"
    )

    # Start local callback server in background thread
    server = http.server.HTTPServer(("localhost", 8765), CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()

    print("Opening Strava authorization in your browser...")
    print(f"If the browser doesn't open, visit:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    thread.join(timeout=120)

    if not auth_code:
        raise SystemExit("No authorization code received. Did you approve access in the browser?")

    print("Exchanging code for tokens...")
    resp = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code":          auth_code,
            "grant_type":    "authorization_code",
        },
    )
    resp.raise_for_status()
    data = resp.json()

    refresh_token = data["refresh_token"]
    athlete = data.get("athlete", {})
    name = f"{athlete.get('firstname', '')} {athlete.get('lastname', '')}".strip()

    # Save new refresh token to .env
    set_key(str(ENV_PATH), "STRAVA_REFRESH_TOKEN", refresh_token)

    print(f"\nAuthorized as: {name or 'unknown'}")
    print(f"Scope: {data.get('scope', '')}")
    print(f"Refresh token saved to .env")
    print("\nYou can now run:  python update_strava.py")


if __name__ == "__main__":
    main()
