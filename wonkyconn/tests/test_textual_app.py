import textual.app


def test_import_textual_app() -> None:
    from wonkyconn import textual_app

    assert issubclass(textual_app.WonkyConnApp, textual.app.App)
