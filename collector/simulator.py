"""
Simulador de fallos y casos límite (Edge-Case Simulator).
Permite simular eventos como desconexión repentina de Bluetooth, apagado de contacto,
respuestas vacías de la ECU y corrupción de datos para validar la resiliencia del sistema.
"""
import logging
from typing import Dict, Any
from collector.adapter_manager import AdapterManager, AdapterState

logger = logging.getLogger(__name__)

class FailureSimulator:
    def __init__(self, adapter_manager: AdapterManager):
        self.adapter = adapter_manager
        self.active_fault: str = "NONE"

    def inject_fault(self, fault_type: str) -> Dict[str, Any]:
        """
        Inyecta un fallo simulado en la conexión:
        - 'BLUETOOTH_DISCONNECT': Simula pérdida de señal Bluetooth.
        - 'IGNITION_OFF': Simula apagado de contacto del motor.
        - 'CORRUPTED_FRAME': Inyecta datos nulos/vacíos.
        - 'RECOVER': Restaura la conexión normal.
        """
        self.active_fault = fault_type
        logger.info(f"Injecting simulated fault: {fault_type}")

        if fault_type == "BLUETOOTH_DISCONNECT":
            self.adapter.set_state(AdapterState.CONNECTION_LOST)
            return {"status": "fault_injected", "fault": fault_type, "state": self.adapter.state.value}

        elif fault_type == "IGNITION_OFF":
            self.adapter.set_state(AdapterState.VEHICLE_NOT_RESPONDING)
            return {"status": "fault_injected", "fault": fault_type, "state": self.adapter.state.value}

        elif fault_type == "CORRUPTED_FRAME":
            return {"status": "fault_injected", "fault": fault_type, "message": "Datos de trama nulos inyectados."}

        elif fault_type == "RECOVER":
            self.active_fault = "NONE"
            self.adapter.set_state(AdapterState.VEHICLE_CONNECTED)
            return {"status": "recovered", "fault": "NONE", "state": self.adapter.state.value}

        return {"status": "unknown_fault", "fault": fault_type}
