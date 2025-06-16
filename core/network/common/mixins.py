"""Custom common mixins for views."""


class RefererRedirectMixin:
    """Redirect use referer first or fallback to default url."""

    def get_success_url(self):
        """Redirect to referring page after deletion."""
        referer = self.request.META.get("HTTP_REFERER")
        return referer or self.fallback_url
