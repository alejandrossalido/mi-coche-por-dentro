from types import SimpleNamespace

from collector import adapter_manager as adapter_module
from collector.adapter_manager import AdapterManager
from collector.connection_state_machine import ConnectionState


def _port(device, description, hwid):
    return SimpleNamespace(
        device=device,
        description=description,
        hwid=hwid,
        manufacturer="",
    )


def test_vlinker_usb_port_is_prioritized_over_intel_amt(monkeypatch):
    monkeypatch.setattr(
        adapter_module.serial.tools.list_ports,
        "comports",
        lambda: [
            _port("COM3", "Intel(R) Active Management Technology - SOL (COM3)", "PCI\\INTEL"),
            _port("COM5", "USB Serial Port (COM5)", "USB VID:PID=0403:6015"),
        ],
    )

    ports = AdapterManager().list_available_ports()

    assert ports[0]["port"] == "COM5"
    assert ports[0]["is_obdlink"] is True
    assert ports[1]["port"] == "COM3"
    assert ports[1]["excluded"] is True


def test_retry_from_error_resets_state_and_connects(monkeypatch):
    class FakeConnection:
        def status(self):
            return "CAR_CONNECTED"

        def protocol_name(self):
            return "ISO 15765-4 (CAN 11/500)"

        def close(self):
            return None

    fake_obd = SimpleNamespace(
        OBD=lambda **kwargs: FakeConnection(),
        OBDStatus=SimpleNamespace(
            CAR_CONNECTED="CAR_CONNECTED",
            OBD_CONNECTED="OBD_CONNECTED",
        ),
    )
    monkeypatch.setattr(adapter_module, "obd", fake_obd)
    manager = AdapterManager()
    manager.state_machine.transition_to(ConnectionState.ERROR, "fallo inicial")

    assert manager.connect(com_port="COM5") is True
    assert manager.state == ConnectionState.VEHICLE_CONNECTED
    assert manager.active_port == "COM5"
    assert manager.get_status()["is_connected"] is True


def test_auto_detection_does_not_try_unrelated_com_port(monkeypatch):
    monkeypatch.setattr(
        adapter_module.serial.tools.list_ports,
        "comports",
        lambda: [
            _port("COM3", "Intel(R) Active Management Technology - SOL (COM3)", "PCI\\INTEL"),
        ],
    )
    manager = AdapterManager()

    assert manager.connect() is False
    assert manager.active_port is None
    assert manager.state == ConnectionState.ERROR


def test_adapter_retries_safe_serial_settings_until_ecu_responds(monkeypatch):
    attempts = []

    class FakeConnection:
        def __init__(self, status):
            self._status = status
            self.closed = False

        def status(self):
            return self._status

        def protocol_name(self):
            return "ISO 15765-4 (CAN 11/500)"

        def close(self):
            self.closed = True

    first = FakeConnection("OBD_CONNECTED")
    second = FakeConnection("CAR_CONNECTED")

    def build_connection(**kwargs):
        attempts.append(kwargs)
        return first if len(attempts) == 1 else second

    fake_obd = SimpleNamespace(
        OBD=build_connection,
        OBDStatus=SimpleNamespace(
            CAR_CONNECTED="CAR_CONNECTED",
            OBD_CONNECTED="OBD_CONNECTED",
        ),
    )
    monkeypatch.setattr(adapter_module, "obd", fake_obd)

    manager = AdapterManager()
    assert manager.connect(com_port="com5") is True
    assert first.closed is True
    assert attempts[0]["baudrate"] == 115200
    assert attempts[0]["fast"] is True
    assert attempts[1]["fast"] is False
    assert manager.active_port == "COM5"
    assert manager.get_status()["attempt_count"] == 2


def test_adapter_without_python_obd_never_fakes_production_connection(monkeypatch):
    monkeypatch.setattr(adapter_module, "obd", None)
    monkeypatch.setenv("APP_MODE", "production")
    manager = AdapterManager()

    assert manager.connect(com_port="COM5") is False
    assert manager.connection is None
    assert manager.get_status()["is_connected"] is False
    assert manager.state == ConnectionState.ERROR


def test_invalid_port_is_rejected_before_opening_adapter(monkeypatch):
    calls = []
    fake_obd = SimpleNamespace(
        OBD=lambda **kwargs: calls.append(kwargs),
        OBDStatus=SimpleNamespace(CAR_CONNECTED="CAR_CONNECTED", OBD_CONNECTED="OBD_CONNECTED"),
    )
    monkeypatch.setattr(adapter_module, "obd", fake_obd)
    manager = AdapterManager()

    assert manager.connect(com_port='COM5" -bad') is False
    assert calls == []
    assert manager.state == ConnectionState.ERROR
