from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_FILE = Path(__file__).parent.parent / "frontend" / "streamlit_app.py"


def test_form_renders():
    app = AppTest.from_file(str(APP_FILE)).run()

    assert not app.exception
    assert app.title[0].value == "AI Travel Planner"
    assert app.text_input[0].value == "Dehradun"
