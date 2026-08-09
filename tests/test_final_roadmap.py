"""
Tests unitarios finales para CaptureProfiles, Protocols y FailureSimulator.
"""
from collector.capture_profiles import CaptureProfileManager
from analysis.protocols import ProtocolManager
from collector.adapter_manager import AdapterManager, AdapterState
from collector.simulator import FailureSimulator

def test_capture_profiles():
    profiles = CaptureProfileManager.list_profiles()
    assert len(profiles) >= 4
    cold_start = CaptureProfileManager.get_profile("COLD_START")
    assert cold_start["name"] == "Arranque en Frío"
    assert "RPM" in cold_start["pids"]

def test_protocol_manager():
    proto = ProtocolManager.get_protocol("COLD_START")
    assert "checklist" in proto
    assert len(proto["checklist"]) > 0

def test_failure_simulator():
    adapter = AdapterManager()
    sim = FailureSimulator(adapter)
    
    res1 = sim.inject_fault("BLUETOOTH_DISCONNECT")
    assert res1["state"] == AdapterState.CONNECTION_LOST.value

    res2 = sim.inject_fault("IGNITION_OFF")
    assert res2["state"] == AdapterState.VEHICLE_NOT_RESPONDING.value

    res3 = sim.inject_fault("RECOVER")
    assert res3["state"] == AdapterState.VEHICLE_CONNECTED.value
