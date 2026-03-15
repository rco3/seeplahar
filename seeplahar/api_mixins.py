"""
CustomerAwareAPIViewMixin
=========================
DRF views that use JWT auth need to set the thread-local customer context
*after* DRF has run its authentication (i.e. after request.user is known).
Django's CustomerMiddleware runs before that, so we can't rely on it alone.

This mixin overrides DRF's `initial()` (called after authentication) to push
the authenticated user's customer into the thread-local, then clears it in
`finalize_response()`.
"""
from users.customer_context import set_current_customer, clear_current_customer


class CustomerAwareAPIViewMixin:
    """
    Mix into any DRF APIView or ViewSet to ensure the thread-local customer
    context is set from request.user.customer for the duration of the request.
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.user and request.user.is_authenticated:
            set_current_customer(request.user.customer)

    def finalize_response(self, request, response, *args, **kwargs):
        clear_current_customer()
        return super().finalize_response(request, response, *args, **kwargs)
