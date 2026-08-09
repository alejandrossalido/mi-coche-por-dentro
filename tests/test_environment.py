"""
Test de verificación del entorno de desarrollo Python y dependencias.
"""

def test_imports():
    import obd
    import fastapi
    import pydantic
    import polars
    import pyarrow
    
    assert obd.__version__ is not None
    assert fastapi.__version__ is not None
    assert pydantic.__version__ is not None
    assert polars.__version__ is not None
    assert pyarrow.__version__ is not None

def test_project_modules():
    import collector
    import backend
    import analysis
    import database
    import mcp_server
    
    assert collector is not None
    assert backend is not None
    assert analysis is not None
    assert database is not None
    assert mcp_server is not None
