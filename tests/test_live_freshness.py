import backend.main as backend_main


class _ActivePoller:
    is_running = True
    abort_reason = None

    def __init__(self, *, age: float, busy: bool, poll_age: float):
        self.age = age
        self.busy = busy
        self.poll_age = poll_age

    def get_metrics(self):
        return {
            "last_valid_age_sec": self.age,
            "poll_in_progress": self.busy,
            "poll_age_sec": self.poll_age,
            "elapsed_sec": 30.0,
        }


def test_long_active_query_is_not_reported_as_disconnection(monkeypatch):
    monkeypatch.setattr(backend_main, "active_poller", _ActivePoller(age=7.6, busy=True, poll_age=7.6))
    monkeypatch.setattr(backend_main, "active_session_id", "session")
    with backend_main.live_samples_lock:
        backend_main.live_samples.clear()

    snapshot = backend_main.get_live_snapshot()

    assert snapshot["data_stale"] is False


def test_real_idle_communication_is_reported_after_grace_period(monkeypatch):
    monkeypatch.setattr(backend_main, "active_poller", _ActivePoller(age=21.0, busy=False, poll_age=0.0))
    monkeypatch.setattr(backend_main, "active_session_id", "session")
    with backend_main.live_samples_lock:
        backend_main.live_samples.clear()

    snapshot = backend_main.get_live_snapshot()

    assert snapshot["data_stale"] is True
