"""Exercise the real SDK request format without sending paid API requests."""
import json
import runpy
from pathlib import Path

import httpx
import openai
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ["scripts/03_generate_openai_news.py", "rag/rag_chatbot.py"]


@pytest.mark.parametrize("script", SCRIPTS)
@pytest.mark.parametrize("configured_model", ["", "test-model-override"])
@pytest.mark.parametrize("status", ["completed", "incomplete", "empty"])
def test_model_request_and_output(monkeypatch, capsys, script, configured_model, status):
    requests = []
    writes = []
    text = "검증용 답변 2.45 m/s [F-1]"

    def handle(request):
        assert request.url.path == "/v1/responses"
        payload = json.loads(request.content)
        requests.append(payload)
        assert payload["model"] == (configured_model or "gpt-5.6-terra")
        assert payload["reasoning"] == {"effort": "medium"}
        assert "2.45" in payload["input"]
        return httpx.Response(200, json={
            "id": "resp_test", "object": "response", "created_at": 0,
            "model": payload["model"],
            "status": "incomplete" if status == "incomplete" else "completed",
            "incomplete_details": {"reason": "max_output_tokens"} if status == "incomplete" else None,
            "output": [] if status == "empty" else [{
                "type": "message", "id": "msg_test", "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": text, "annotations": []}],
            }],
            "usage": {"input_tokens": 10, "output_tokens": 10, "total_tokens": 20},
        })

    client = openai.OpenAI(
        api_key="test-only", base_url="https://example.invalid/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handle)),
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    monkeypatch.setenv("OPENAI_MODEL", configured_model)
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(openai, "OpenAI", lambda **kwargs: client)
    monkeypatch.setattr("builtins.input", lambda prompt: "서울 평균 풍속은?")
    monkeypatch.setattr(Path, "write_text", lambda path, data, **kwargs: writes.append((path, data)))

    if script.startswith("scripts/") and status != "completed":
        with pytest.raises(SystemExit):
            runpy.run_path(str(ROOT / script), run_name="__main__")
    else:
        runpy.run_path(str(ROOT / script), run_name="__main__")

    assert len(requests) == 1
    if script.startswith("scripts/") and status == "completed":
        assert writes == [(ROOT / "articles/04_ai_news_draft.txt", text)]
    else:
        assert writes == []
    if script.startswith("rag/"):
        output = capsys.readouterr().out
        assert ("=== RAG 챗봇 답변 ===" in output) == (status == "completed")
        assert "F-1" in output
    client.close()


def test_no_evidence_skips_api(monkeypatch, capsys):
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr("builtins.input", lambda prompt: "등록되지 않은 질문")

    def unexpected_client(**kwargs):
        pytest.fail("No evidence must not create an API client")

    monkeypatch.setattr(openai, "OpenAI", unexpected_client)
    runpy.run_path(str(ROOT / "rag/rag_chatbot.py"), run_name="__main__")
    assert "제공된 자료로는 확인할 수 없습니다" in capsys.readouterr().out
