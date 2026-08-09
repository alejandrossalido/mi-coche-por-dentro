from collector.vag_kwp2000 import (
    ALL_KWP_SIGNALS,
    Tp20Transport,
    VagKwp2000Client,
    _decode_block_value,
    is_legacy_kwp_calibration,
)
from collector.vag_bkp_catalog import DOCUMENTED_GROUPS, documented_field_count


class FakePort:
    timeout = 1.0


class FakeInterface:
    def __init__(self):
        self._ELM327__port = FakePort()
        self.commands = []

    def _ELM327__send(self, command):
        text = command.decode("ascii")
        self.commands.append(text)
        responses = {
            "01C00010000301": ["201 7 01 D0 00 03 40 07 01"],
            "A00F8AFF0AFF": ["300 6 A1 0F 8A 00 4A 00"],
            "1000021089": ["300 1 B1", "300 5 10 00 02 50 89"],
            "B1": ["NO DATA"],
        }
        return responses.get(text, ["OK"])


class FakeConnection:
    def __init__(self):
        self.interface = FakeInterface()


def test_detects_03g_906_018_family_from_mode09_bytes():
    assert is_legacy_kwp_calibration(bytearray(b"3G906018FG 09"))
    assert is_legacy_kwp_calibration("03G 906 018 FG")
    assert not is_legacy_kwp_calibration("03L906022QF")


def test_tp20_opens_read_only_kwp_session():
    connection = FakeConnection()
    transport = Tp20Transport(connection)
    transport.open()
    assert transport.is_open
    assert "1000021089" in connection.interface.commands


def test_tp20_accepts_duplicate_identical_gateway_response():
    connection = FakeConnection()
    original_send = connection.interface._ELM327__send

    def duplicate_gateway_response(command):
        if command == b"01C00010000301":
            frame = "201 7 00 D0 00 03 40 07 01"
            return [frame, frame]
        return original_send(command)

    connection.interface._ELM327__send = duplicate_gateway_response
    transport = Tp20Transport(connection)

    transport.open()

    assert transport.is_open
    assert "1000021089" in connection.interface.commands


def test_signal_requires_expected_type_and_plausible_value():
    client = VagKwp2000Client(FakeConnection())
    client.read_group = lambda group, use_cache=True: {
        "success": True,
        "status": "compatible",
        "fields": [
            {"type_id": 0x01, "a": 20, "b": 200, "value": 800.0},
            {"type_id": 0x27, "a": 32, "b": 40, "value": 5.0},
            {"type_id": 0x04, "a": 100, "b": 120, "value": 7.0},
            {"type_id": 0x1A, "a": 100, "b": 186, "value": 86.0},
        ],
        "latency_ms": 12.0,
        "raw_response": "6101",
    }
    rpm = client.read_signal("RPM")
    coolant = client.read_signal("COOLANT_TEMP")
    assert rpm["success"] and rpm["value"] == 800.0
    assert coolant["success"] and coolant["value"] == 86.0


def test_signal_rejects_wrong_binary_type():
    client = VagKwp2000Client(FakeConnection())
    client.read_group = lambda group, use_cache=True: {
        "success": True,
        "fields": [{"type_id": 0x36, "a": 1, "b": 2, "value": 258.0}] * 4,
        "latency_ms": 1.0,
        "raw_response": "6101",
    }
    result = client.read_signal("RPM")
    assert not result["success"]
    assert result["status"] == "type_mismatch"


def test_ppd15_extended_eight_field_block_is_accepted():
    client = VagKwp2000Client(FakeConnection())
    response = bytes.fromhex(
        "610101EB11279810229D821A325925027A250000250000250317"
    )
    client.transport.request = lambda payload: response

    rpm = client.read_signal("RPM", use_cache=False)
    duration = client.read_signal("VAG_INJECTION_DURATION")
    coolant = client.read_signal("COOLANT_TEMP")

    assert rpm["success"] is True
    assert rpm["value"] == 799.0
    assert duration["success"] is True
    assert duration["value"] == 3.14
    assert coolant["success"] is True
    assert coolant["value"] == 39.0


def test_all_zero_placeholder_block_is_not_reported_as_real_data():
    client = VagKwp2000Client(FakeConnection())
    response = bytes.fromhex(
        "6145250000250000250000250000250000250000250000250000"
    )
    client.transport.request = lambda payload: response

    reading = client.read_signal("VAG_DPF_REGEN_STATUS", use_cache=False)

    assert reading["success"] is False
    assert reading["status"] == "unsupported"


def test_zero_injector_status_is_valid_and_means_no_detected_fault():
    client = VagKwp2000Client(FakeConnection())
    response = bytes.fromhex(
        "6112250000250000250000250000250000250000250000250000"
    )
    client.transport.request = lambda payload: response

    reading = client.read_signal("VAG_INJECTOR_STATUS_1", use_cache=False)

    assert reading["success"] is True
    assert reading["value"] == 0.0


def test_ppd_torsion_and_switch_time_binary_types_are_decoded():
    assert _decode_block_value(0x05, 115, 103) == 34.5
    assert _decode_block_value(0x16, 10, 20) == 0.2
    assert _decode_block_value(0x51, 0xFF, 0x88) == -0.5232

    client = VagKwp2000Client(FakeConnection())
    client.read_group = lambda group, use_cache=True: {
        "success": True,
        "fields": [{"type_id": 0x16, "a": 10, "b": 20, "value": 0.2}] * 4,
        "latency_ms": 2.0,
        "raw_response": "6117",
    }
    result = client.read_signal("VAG_INJECTOR_SWITCH_TIME_1")
    assert result["success"] is True
    assert result["value"] == 0.2
    assert result["unit"] == "ms"


def test_real_bkp_cooling_alternator_and_camshaft_blocks_are_named_and_decoded():
    client = VagKwp2000Client(FakeConnection())
    payloads = {
        16: bytes.fromhex("611021FF4B10FFDC36000015E435250000250000250000250000"),
        51: bytes.fromhex("61330114D2010AD2080A0310FF40250000250000250000250000"),
        62: bytes.fromhex("613E1A32671A325E0573671A325E250000250000250000250000"),
        64: bytes.fromhex("61401A32671A325E176478250000250000250000250000250000"),
    }
    client.transport.request = lambda request: payloads[request[1]]

    alternator = client.read_signal("VAG_ALTERNATOR_LOAD", use_cache=False)
    camshaft = client.read_signal("VAG_CAMSHAFT_SPEED", use_cache=False)
    radiator = client.read_signal("VAG_RADIATOR_OUTLET_TEMP", use_cache=False)
    ambient = client.read_signal("VAG_AMBIENT_TEMP")
    fan = client.read_signal("VAG_COOLING_FAN_COMMAND", use_cache=False)

    assert alternator["success"] is True and alternator["value"] == 29.4118
    assert camshaft["success"] is True and camshaft["value"] == 420.0
    assert radiator["success"] is True and radiator["value"] == 44.0
    assert ambient["success"] is True and ambient["value"] == 34.5
    assert fan["success"] is True and fan["value"] == 46.875


def test_real_ppd_group_18_status_payload_uses_status_byte():
    client = VagKwp2000Client(FakeConnection())
    client.transport.request = lambda payload: bytes.fromhex(
        "6112080A00080A00080A00080A00250000250000250000250000"
    )

    reading = client.read_signal("VAG_INJECTOR_STATUS_1", use_cache=False)

    assert reading["success"] is True
    assert reading["value"] == 0.0


def test_bkp_catalog_has_every_documented_group_and_field_once():
    assert len(DOCUMENTED_GROUPS) == 69
    assert documented_field_count() == 214
    assert len(ALL_KWP_SIGNALS) == 214
    assert len({item.pid_name for item in ALL_KWP_SIGNALS}) == 214
    assert len({(item.group, item.position) for item in ALL_KWP_SIGNALS}) == 214


def test_exhaustive_probe_reads_all_groups_and_keeps_raw_evidence():
    client = VagKwp2000Client(FakeConnection())
    visited = []
    client.open = lambda: None
    client.close = lambda: None
    client._read_identity = lambda: {"long_identification": "03G 906 018 FG"}

    def fake_group(group, use_cache=True):
        if not use_cache:
            visited.append(group)
        return {
            "success": True,
            "status": "compatible",
            "fields": [
                {"type_id": 0x1A, "a": 0, "b": 20, "value": 20.0},
                {"type_id": 0x25, "a": 0, "b": 0, "value": 0.0},
                {"type_id": 0x25, "a": 0, "b": 0, "value": 0.0},
                {"type_id": 0x25, "a": 0, "b": 0, "value": 0.0},
            ],
            "field_count": 4,
            "all_placeholders": False,
            "latency_ms": 2.0,
            "raw_response": f"61{group:02X}1A0014",
        }

    client.read_group = fake_group
    result = client.probe(exhaustive=True)

    assert visited == list(DOCUMENTED_GROUPS)
    assert result["tested_group_count"] == 69
    assert result["documented_field_count"] == 214
    assert result["live_signals"]
    assert all("raw_response" in item for item in result["live_signals"])


def test_batch_reader_requests_shared_group_only_once():
    client = VagKwp2000Client(FakeConnection())
    calls = []

    def fake_group(group, use_cache=True):
        calls.append((group, use_cache))
        return {
            "success": True,
            "status": "compatible",
            "fields": [
                {"type_id": 0x01, "a": 20, "b": 200, "value": 800.0},
                {"type_id": 0x27, "a": 32, "b": 40, "value": 5.0},
                {"type_id": 0x22, "a": 100, "b": 131, "value": 3.0},
                {"type_id": 0x1A, "a": 100, "b": 186, "value": 86.0},
            ],
            "latency_ms": 3.0,
            "raw_response": "6101",
        }

    client.read_group = fake_group
    results = client.read_signals_batch(["RPM", "VAG_INJECTION_QUANTITY", "COOLANT_TEMP"])

    assert calls == [(1, False)]
    assert results["RPM"]["value"] == 800.0
    assert results["VAG_INJECTION_QUANTITY"]["value"] == 5.0
    assert results["COOLANT_TEMP"]["value"] == 86.0
