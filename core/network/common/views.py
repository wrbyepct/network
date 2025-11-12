"""View for all apps."""

from django.http import HttpResponse
from django.views.generic import View


# TODO Check if EmptyView is still needed later.
class EmptyView(View):
    """View to return empty html body on GET request."""

    def get(self, request, *args, **kwargs):
        """Return empty request on get."""
        return HttpResponse()
