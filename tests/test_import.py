def test_package_contract():
    """Foundation smoke test; data systems are tested separately."""
    import src.phoenix

    assert src.phoenix.__version__ == "0.1.0"
