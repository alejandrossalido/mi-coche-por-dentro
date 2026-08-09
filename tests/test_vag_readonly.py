import time

from collector.poller import TelemetryPoller
from collector.vag_readonly import (
    ENGINE_REQUEST_HEADER,
    VagReadOnlyClient,
    VagSignalDefinition,
)


class FakeResponse:
    def __init__(self, data_hex=None):
        self.value = [] if data_hex is None else [{"tx_id": 0x7E8, "data": data_hex, "raw": data_hex}]

    def is_null(self):
        return not self.value


class FakeUdsConnection:
    def __init__(self, responses):
        self.responses = responses
        self.commands = []

    def query(self, command, force=False):
        self.commands.append((command, force))
        return FakeResponse(self.responses.get(command.command.decode("ascii").upper()))


class InMemoryStore:
    def __init__(self):
        self.samples = []

    def save_samples(self, session_id, samples):
        self.samples.extend(samples)
        return "memory"


def test_vag_client_only_sends_read_data_by_identifier():
    connection = FakeUdsConnection({"22F187": "62F18730334C3930363032325144"})
    client = VagReadOnlyClient(connection, definitions=[])

    identity = client.identify_ecu()

    assert identity[0]["value"] == "03L906022QD"
    assert all(command.command.startswith(b"22") for command, _ in connection.commands)
    assert all(command.header == ENGINE_REQUEST_HEADER for command, _ in connection.commands)
    assert all(force is True for _, force in connection.commands)


def test_vag_client_decodes_only_a_whitelisted_definition():
    definition = VagSignalDefinition(
        pid_name="VAG_OIL_TEMP",
        label="Temperatura del aceite",
        unit="°C",
        did=0x1234,
        byte_offset=0,
        byte_length=2,
        scale=0.1,
        value_offset=-40,
        minimum=-40,
        maximum=180,
    )
    connection = FakeUdsConnection({"221234": "62123403E8"})
    client = VagReadOnlyClient(connection, definitions=[definition])

    reading = client.read_signal("VAG_OIL_TEMP")
    blocked = client.read_signal("VAG_UNKNOWN")

    assert reading["success"] is True
    assert reading["value"] == 60.0
    assert reading["data_source"] == "measured_vag_uds"
    assert blocked["status"] == "mapping_required"


def test_negative_uds_response_is_explained_without_becoming_a_value():
    definition = VagSignalDefinition(
        pid_name="VAG_OIL_TEMP",
        label="Temperatura del aceite",
        unit="°C",
        did=0x1234,
        byte_offset=0,
        byte_length=1,
    )
    client = VagReadOnlyClient(FakeUdsConnection({"221234": "7F2231"}), definitions=[definition])

    reading = client.read_signal("VAG_OIL_TEMP")

    assert reading["success"] is False
    assert reading["status"] == "negative_response"
    assert reading["reason"] == "IDENTIFICADOR_FUERA_DE_RANGO"
    assert "value" not in reading


def test_poller_persists_verified_vag_measurements(monkeypatch):
    class OemReader:
        signal_names = {"VAG_OIL_TEMP"}

        def read_signal(self, pid_name):
            return {
                "pid": pid_name,
                "success": True,
                "value": 91.5,
                "unit": "°C",
                "latency_ms": 8.0,
                "raw_response": "62ABCD0523",
            }

    monkeypatch.setenv("APP_MODE", "production")
    store = InMemoryStore()
    poller = TelemetryPoller(
        session_id="vag-test",
        telemetry_store=store,
        pids=["VAG_OIL_TEMP"],
        oem_reader=OemReader(),
    )
    poller.start(poll_interval_ms=5)
    deadline = time.monotonic() + 1.0
    while poller.sample_count < 3 and time.monotonic() < deadline:
        time.sleep(0.01)
    poller.stop()

    assert store.samples
    assert all(sample["value"] == 91.5 for sample in store.samples)
    assert all(sample["data_source"] == "measured_vag_uds" for sample in store.samples)
    assert poller.invalid_sample_count == 0


def test_poller_captures_every_requested_oem_signal_in_first_batch(monkeypatch):
    class BatchReader:
        signal_names = {"OEM_A", "OEM_B", "OEM_C"}

        def __init__(self):
            self.calls = []

        def read_signals_batch(self, pid_names):
            self.calls.append(list(pid_names))
            return {
                pid: {
                    "pid": pid,
                    "success": True,
                    "value": float(index + 1),
                    "unit": "valor",
                    "latency_ms": 1.0,
                    "raw_response": "61AA",
                    "data_source": "measured_vag_kwp2000",
                }
                for index, pid in enumerate(pid_names)
            }

        def close(self):
            pass

    monkeypatch.setenv("APP_MODE", "production")
    store = InMemoryStore()
    reader = BatchReader()
    requested = ["OEM_A", "OEM_B", "OEM_C"]
    poller = TelemetryPoller(
        session_id="batch-test",
        telemetry_store=store,
        pids=requested,
        oem_reader=reader,
    )
    poller.start(poll_interval_ms=5)
    deadline = time.monotonic() + 1.0
    while poller.sample_count < len(requested) and time.monotonic() < deadline:
        time.sleep(0.01)
    poller.stop()

    metrics = poller.get_metrics()
    assert reader.calls
    assert set(reader.calls[0]) == set(requested)
    assert metrics["requested_signal_count"] == 3
    assert metrics["captured_signal_count"] == 3
    assert metrics["missing_signal_count"] == 0
    assert metrics["capture_coverage_percent"] == 100.0
