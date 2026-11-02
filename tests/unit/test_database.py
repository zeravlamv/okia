from django.conf import settings


def test_the_local_sqlite_settings_allow_a_read_during_a_write():
    options = settings.DATABASES["default"]["OPTIONS"]
    assert options["init_command"] == "PRAGMA journal_mode=WAL"
    assert options["timeout"] == 20
