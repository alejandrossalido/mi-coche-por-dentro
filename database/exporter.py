"""
Módulo de exportación e importación de copias de seguridad en formato ZIP.
Empaqueta el expediente completo del vehículo, sesiones, DTCs y archivos Parquet.
"""
import os
import json
import zipfile
from typing import Dict, Any, Optional
from database.db import DatabaseManager
from database.parquet_store import TelemetryStore

class VehicleBackupExporter:
    def __init__(self, db_manager: Optional[DatabaseManager] = None, telemetry_store: Optional[TelemetryStore] = None):
        self.db = db_manager or DatabaseManager()
        self.store = telemetry_store or TelemetryStore()

    def export_vehicle_zip(self, vehicle_id: str, output_zip_path: str) -> str:
        """Exporta el historial del vehículo y sus archivos Parquet a un ZIP."""
        vehicle = self.db.get_vehicle(vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehículo con ID {vehicle_id} no encontrado.")

        sessions = self.db.list_sessions(vehicle_id)
        repairs = self.db.list_repair_actions(vehicle_id)

        manifest = {
            "vehicle": vehicle,
            "sessions": sessions,
            "repairs": repairs,
            "version": "1.0.0"
        }

        os.makedirs(os.path.dirname(os.path.abspath(output_zip_path)), exist_ok=True)

        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))

            for s in sessions:
                s_id = s["id"]
                pq_path = self.store.get_session_file_path(s_id)
                if os.path.exists(pq_path):
                    zf.write(pq_path, arcname=f"telemetry/session_{s_id}.parquet")

        return output_zip_path

    def import_vehicle_zip(self, zip_path: str) -> Dict[str, Any]:
        """Importa un vehículo respaldado desde un paquete ZIP."""
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Archivo ZIP {zip_path} no existe.")

        with zipfile.ZipFile(zip_path, "r") as zf:
            manifest_data = zf.read("manifest.json")
            manifest = json.loads(manifest_data.decode("utf-8"))

            v_info = manifest["vehicle"]
            new_v = self.db.create_vehicle(
                display_name=v_info.get("display_name", "Vehículo Importado"),
                make=v_info.get("make", ""),
                model=v_info.get("model", ""),
                year=v_info.get("year"),
                engine=v_info.get("engine", ""),
                fuel_type=v_info.get("fuel_type", ""),
                powertrain_type=v_info.get("powertrain_type", "gasoline"),
                generation=v_info.get("generation", ""),
                variant=v_info.get("variant", ""),
                engine_code=v_info.get("engine_code", ""),
                market=v_info.get("market", "EU"),
            )

            # Extraer archivos Parquet de telemetría
            for item in zf.namelist():
                if item.startswith("telemetry/") and item.endswith(".parquet"):
                    file_name = os.path.basename(item)
                    target_path = os.path.join(self.store.base_dir, file_name)
                    with open(target_path, "wb") as f_out:
                        f_out.write(zf.read(item))

            return {"status": "success", "imported_vehicle_id": new_v["id"], "sessions_count": len(manifest.get("sessions", []))}
