from stellar.models import get_unique_hash


def test_get_unique_hash():
    assert get_unique_hash()
    assert get_unique_hash() != get_unique_hash()
    assert len(get_unique_hash()) == 32
