"""
Resolutor Jerárquico de Especificaciones Técnicas (SpecResolver) con Clave Estricta (VehicleSpecKey).
Soporta las 7 categorías diagnósticas:
1. OEM_CONFIRMED (Match exacto de make + model + engine_code + fuente documentada)
2. TECHNICAL_DATABASE (Base de datos técnica profesional)
3. MANUFACTURER_SPECIFIC_PLUGIN (Plugin propietario del fabricante)
4. VEHICLE_BASELINE (Percentiles P10-P90 aprendidos históricamente del vehículo)
5. GENERIC_ENGINEERING_RANGE (Reglas genéricas conservadoras)
6. USER_DEFINED (Límites personalizados por el usuario)
7. ENGINE_IDENTIFICATION_REQUIRED / UNVERIFIED (Si el código de motor es desconocido o falto)
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel

from specifications.vag.passat_b6_bmp import VAG_PASSAT_B6_BMP_SPEC
from specifications.vag.passat_b6_bkp import VAG_PASSAT_B6_BKP_SPEC
from specifications.vag.passat_b6_cbab import VAG_PASSAT_B6_CBAB_SPEC
from specifications.opel.vectra_z19dt import OPEL_VECTRA_Z19DT_SPEC
from specifications.opel.vectra_z19dth import OPEL_VECTRA_Z19DTH_SPEC
from specifications.mazda.mazda3_15_skyactiv_d import MAZDA3_15_SKYACTIV_D_SPEC
from specifications.tesla.model3_highland import TESLA_MODEL3_HIGHLAND_SPEC
from analysis.generic_reference_ranges import get_generic_reference_ranges

class VehicleSpecKey(BaseModel):
    make: str
    model: str
    engine_code: str
    generation: Optional[str] = ""
    production_year: Optional[int] = None
    market: Optional[str] = "EU"

class SpecResolver:
    # Registro OEM mapeado por clave exacta de motorización
    OEM_REGISTRY: Dict[str, Dict[str, Any]] = {
        "opel|vectra|z19dt": OPEL_VECTRA_Z19DT_SPEC,
        "opel|vectra|z19dth": OPEL_VECTRA_Z19DTH_SPEC,
        "volkswagen|passat|bmp": VAG_PASSAT_B6_BMP_SPEC,
        "volkswagen|passat|bkp": VAG_PASSAT_B6_BKP_SPEC,
        "volkswagen|passat|cbab": VAG_PASSAT_B6_CBAB_SPEC,
        "mazda|mazda 3|s5-dpts": MAZDA3_15_SKYACTIV_D_SPEC,
        "tesla|model 3|bev": TESLA_MODEL3_HIGHLAND_SPEC,
        "tesla|model 3|highland": TESLA_MODEL3_HIGHLAND_SPEC,
    }

    @classmethod
    def build_lookup_key(cls, make: str, model: str, engine_code: str) -> str:
        """Construye la clave canónica normalizada."""
        clean_make = make.strip().lower()
        clean_model = model.strip().lower()
        model_aliases = {
            ("volkswagen", "passat b6"): "passat",
            ("opel", "vectra c"): "vectra",
            ("tesla", "model 3 highland"): "model 3",
        }
        clean_model = model_aliases.get((clean_make, clean_model), clean_model)
        return f"{clean_make}|{clean_model}|{engine_code.strip().lower()}"

    @classmethod
    def resolve_spec(cls, vehicle_id: str = "", make: str = "", model: str = "",
                     engine_code: str = "", powertrain_type: str = "gasoline",
                     learned_baseline: Optional[Dict[str, Any]] = None,
                     user_custom_limits: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Resuelve la especificación técnica aplicando el orden de prioridad estricto.
        Si falta el código de motor en un coche conocido, rechaza OEM_CONFIRMED y exige identificación.
        """
        clean_make = make.strip()
        clean_model = model.strip()
        clean_engine = engine_code.strip()

        # Si el usuario proporcionó límites personalizados
        if user_custom_limits:
            return {
                "confidence_tier": "USER_DEFINED",
                "resolved_source": "Límites de tolerancia personalizados por el usuario",
                "parameters": user_custom_limits
            }

        # Nivel 1: Búsqueda por clave estricta OEM (Make + Model + Engine Code)
        if clean_make and clean_model and clean_engine:
            lookup_key = cls.build_lookup_key(clean_make, clean_model, clean_engine)
            if lookup_key in cls.OEM_REGISTRY:
                oem_spec = cls.OEM_REGISTRY[lookup_key]
                return {
                    "confidence_tier": "OEM_CONFIRMED",
                    "resolved_source": oem_spec["metadata"].get("source_document", oem_spec["metadata"].get("source_reference", "Ficha Oficial OEM")),
                    "engine_code_confirmed": oem_spec["metadata"].get("engine_code", clean_engine),
                    "metadata": oem_spec["metadata"],
                    "parameters": oem_spec["parameters"]
                }


        # Búsqueda de conveniencia por vehicle_id si contiene el motor embebido
        vid = vehicle_id.lower()
        if vid == "vectra":
            # Opel Vectra Z19DTH
            return cls.resolve_spec(vehicle_id="vectra", make="Opel", model="Vectra", engine_code="Z19DTH", powertrain_type="diesel")
        elif vid == "passat_b6":
            # VW Passat B6 CBAB Common Rail
            return cls.resolve_spec(vehicle_id="passat_b6", make="Volkswagen", model="Passat", engine_code="CBAB", powertrain_type="diesel")
        elif vid == "mazda_3":
            # Mazda 3 S5-DPTS Skyactiv-D
            return cls.resolve_spec(vehicle_id="mazda_3", make="Mazda", model="Mazda 3", engine_code="S5-DPTS", powertrain_type="diesel")
        elif vid == "tesla_model3":
            # Tesla Model 3 Highland BEV
            return cls.resolve_spec(vehicle_id="tesla_model3", make="Tesla", model="Model 3", engine_code="BEV", powertrain_type="bev")

        # Si se conoce el modelo (ej. Passat B6) pero NO el código de motor exacto (BMP vs BKP vs CBAB)
        if clean_make and clean_model and not clean_engine:
            return {
                "confidence_tier": "ENGINE_IDENTIFICATION_REQUIRED",
                "resolved_source": f"Modelo {clean_make} {clean_model} reconocido, pero se requiere especificar el código de motor exacto (ej: BMP, BKP, CBAB o Z19DTH) para conceder OEM_CONFIRMED.",
                "metadata": {"make": clean_make, "model": clean_model, "powertrain_type": powertrain_type},
                "parameters": get_generic_reference_ranges(powertrain_type)["parameters"]
            }

        # Nivel 4: Línea base aprendida históricamente del propio vehículo (P10-P90)
        if learned_baseline and learned_baseline.get("signals"):
            return {
                "confidence_tier": "VEHICLE_BASELINE",
                "resolved_source": "Línea base histórica aprendida del propio vehículo (Percentiles P10-P90)",
                "metadata": {"vehicle_id": vehicle_id, "make": clean_make, "model": clean_model},
                "parameters": learned_baseline["signals"]
            }

        # Nivel 5: Reglas genéricas conservadoras
        generic_spec = get_generic_reference_ranges(powertrain_type)
        return {
            "confidence_tier": "GENERIC_ENGINEERING_RANGE",
            "resolved_source": "Rangos genéricos conservadores por tipo de propulsión (Cobertura OBD-II Nivel 1 - No es Ficha Oficial OEM)",
            "metadata": {
                "vehicle_id": vehicle_id,
                "make": clean_make,
                "model": clean_model,
                "powertrain_type": powertrain_type,
                "warning": "Vehículo en Cobertura Genérica OBD-II. Sin Ficha Técnica OEM confirmada."
            },
            "parameters": generic_spec["parameters"]
        }
