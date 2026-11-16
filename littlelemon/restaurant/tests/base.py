from rest_framework.views import APIView


class NoThrottleMixin:
    """
    DRF snapshots `APIView.throttle_classes` at import time, so
    `override_settings` cannot disable throttling reliably. This mixin
    clears throttles for the duration of each test instead.

    Throttling itself (5/min anon, 20/min user) stays active in
    development and production.
    """

    def setUp(self):
        super().setUp()
        self._original_throttle_classes = APIView.throttle_classes
        APIView.throttle_classes = []

    def tearDown(self):
        APIView.throttle_classes = self._original_throttle_classes
        super().tearDown()
