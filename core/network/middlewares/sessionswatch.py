"""Custom Session Watch middleware."""


class SessionWatchMiddleware:
    def __init__(self, next_mw):
        print("My custom session watch middleware start...")
        self.next_mw = next_mw  # what is this?

    def __call__(self, request):
        response = self.next_mw(request)

        if hasattr(request, "session"):
            print("## ↓↓↓↓↓ from SSessionWatchMiddleware ↓↓↓↓↓ ###")
            print("Session is modified", request.session.modified)
            print("Response set-cookie header", response.cookies.get("sessionid"))
            print("## ↑↑↑↑↑ from SSessionWatchMiddleware ↑↑↑↑↑ ###")
        return response
