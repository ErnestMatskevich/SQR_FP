from app.api import *
pytest_plugins = ('pytest_asyncio',)


def test_read_text_from_prompt_file():
    file_path = "test_file.txt"
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("This is a test text")

    result = read_text_from_prompt_file(file_path)

    assert result == "This is a test text"


def test_delete_spec_symbols():
    test_str = "some' test ""text"
    result = delete_spec_symbols(test_str)

    assert result == "some test text"


def test_send_prompt(event_loop):
    test_question = "What is test?"
    test_prompt = "Answer with your knowledge"
    result = event_loop.run_until_complete(
        send_prompt(test_question, test_prompt)
    )
    assert isinstance(result, str)
    assert result != ""

