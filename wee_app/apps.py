import datetime
from importlib import import_module
from django.apps import AppConfig
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.db.models import signals
from django.utils import timezone
import logging
import requests
import signal
import threading

logger = logging.getLogger(__name__)

def _simulate_request_progress(access_token, request_id):
    def set_status(status):
        requests.put(
            settings.UBER_API_HOST + '/v1/sandbox/requests/' + request_id,
            json={'status': status},
            headers={
                'Authorization': 'Bearer ' + access_token
            }).raise_for_status()

        response = requests.get(
            settings.UBER_API_HOST + '/v1/requests/' + request_id,
            headers={
                'Authorization': 'Bearer ' + access_token
            })
        response.raise_for_status()
        assert response.json()['status'] == status

        logger.info('Request %s is now %s', request_id, status)

    def drive():
        set_status('in_progress')
        threading.Timer(1, set_status, ('completed',)).start()

    def pickup():
        set_status('arriving')
        threading.Timer(1, drive).start()

    def accept():
        set_status('accepted')
        threading.Timer(1, pickup).start()

    threading.Timer(1, accept).start()

class WeeAppConfig(AppConfig):
    name = 'wee_app'

    _ran_ready = False
    _request_ids_to_timers = {}

    @staticmethod
    def _send_request(request):
        session = request.session
        if not session:
            # Wait until an attached session is saved.
            return
        SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
        access_token = SessionStore(session_key=session.pk)['access_token']

        # TODO: Actually check for using the refresh token.
        product_response = requests.post(
            settings.UBER_API_HOST + '/v1/requests',
            json={
                'product_id': request.product_id,
                'start_latitude': request.pickup.latitude,
                'start_longitude': request.pickup.longitude,
                'end_latitude': request.destination.latitude,
                'end_longitude': request.destination.longitude,
            },
            headers={'Authorization': 'Bearer ' + access_token})
        # TODO: Somehow notify user of a failure.
        product_response.raise_for_status()
        request_id = product_response.json()['request_id']

        request.issued = True
        request.save()

        logger.info('Issued request %s', request_id)

        if settings.DEBUG:
            _simulate_request_progress(access_token, request_id)

    def _cancel_request(self, request):
        self._request_ids_to_timers[request.id].cancel()
        del self._request_ids_to_timers[request.id]

    def _schedule_request(self, request):
        interval = request.request_timestamp - timezone.now()
        timer = threading.Timer(interval.seconds,
                                self._send_request, (request,))
        timer.start()
        self._request_ids_to_timers[request.id] = timer

    def _on_request_pre_delete(self, instance=None, **_):
        if instance.id in self._request_ids_to_timers:
            self._cancel_request(instance)

    def _on_request_post_save(self, instance=None, created=None, **_):
        if not created:
            self._cancel_request(instance)
        if not instance.issued:
            self._schedule_request(instance)

    def ready(self):
        if self._ran_ready:
            return

        PlannedUberRequest = self.get_model('PlannedUberRequest')

        # Django handles SIGINT so guaranteed not-None.
        continue_sigint = signal.getsignal(signal.SIGINT)
        def disconnect(signo, frame):
            for timer in self._request_ids_to_timers.values():
                timer.cancel()
            continue_sigint(signo, frame)
        signal.signal(signal.SIGINT, disconnect)

        signals.pre_delete.connect(self._on_request_pre_delete,
                                   sender=PlannedUberRequest, weak=False)
        signals.post_save.connect(self._on_request_post_save,
                                  sender=PlannedUberRequest, weak=False)
        for request in PlannedUberRequest.objects.filter(issued=False):
            self._schedule_request(request)

        self._ran_ready = True
