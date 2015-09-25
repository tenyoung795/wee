import datetime
from importlib import import_module
from django.apps import AppConfig
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.db import DatabaseError
from django.db.models import signals
from django.utils import timezone
import logging
import queue
import requests
import signal
import threading

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
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

    def ready(self):
        if self._ran_ready:
            return

        request_queue = queue.Queue()
        timers = {}

        continue_sigint = signal.getsignal(signal.SIGINT)
        def handle_sigint(signo, frame):
            request_queue.join()
            request_queue.put(None)

            # TODO: Notify users about maintenance.
            continue_sigint(signo, frame)
        signal.signal(signal.SIGINT, handle_sigint)

        PlannedUberRequest = self.get_model('PlannedUberRequest')

        def cancel_request(request):
            timers[request.id].cancel()
        def on_pre_delete(instance=None, **_):
            if instance.id in timers:
                cancel_request(instance)
        signals.pre_delete.connect(on_pre_delete,
                                   sender=PlannedUberRequest, weak=False)

        def schedule_request(request):
            interval = request.request_timestamp - timezone.now()
            timer = threading.Timer(interval.seconds, request_queue.put, (request,))
            timer.daemon = True
            timer.start()
            timers[request.id] = timer
        def on_post_save(instance=None, created=None, **_):
            if not created:
                cancel_request(instance)
            if not instance.issued:
                schedule_request(instance)
        signals.post_save.connect(on_post_save,
                                  sender=PlannedUberRequest, weak=False)

        try:
            for request in PlannedUberRequest.objects.filter(issued=False):
                schedule_request(request)
        except DatabaseError as error:
            logger.info('Hopefully, you are making or performing migrations')

        def process_requests():
            while True:
                request = request_queue.get()
                if request is None:
                    break

                try:
                    session = request.session
                    if not session:
                        # Wait until an attached session is saved.
                        continue
                    session_store = SessionStore(session_key=session.pk)
                    access_token = session_store['access_token']

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
                except:
                    logging.exception('Error processing request %s', request.id)
                    # TODO: Notify user.

                request_queue.task_done()
        threading.Thread(target=process_requests).start()

        self._ran_ready = True
