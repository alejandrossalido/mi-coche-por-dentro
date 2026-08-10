# -*- mode: python ; coding: utf-8 -*-


hiddenimports = [
    "uvicorn.logging",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.lifespan.on",
]

a = Analysis(
    ["desktop_launcher.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("dashboard/out", "dashboard/out"),
        ("rules/diagnostic_rules.yaml", "rules"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PyInstaller",
        "pytest",
        "ruff",
        "numpy.tests",
        "pandas.tests",
        "pyarrow.tests",
        "scipy.tests",
    ],
    noarchive=False,
    optimize=0,
)
# Algunos hooks de análisis incluyen fixtures de pruebas que no son necesarios
# para ejecutar la aplicación y pueden confundirse con telemetría de usuario.
_test_data_prefixes = (
    "numpy/tests/",
    "pandas/tests/",
    "pyarrow/tests/",
    "scipy/tests/",
)
a.datas = [
    item
    for item in a.datas
    if not item[0].replace("\\", "/").startswith(_test_data_prefixes)
]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MiCochePorDentro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MiCochePorDentro",
)
