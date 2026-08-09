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
