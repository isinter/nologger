from nologger.context import set_trace_id, get_trace_id, reset_trace_id, trace_context


def test_trace_id_basic():
    original = get_trace_id()
    assert original is None
    
    token = set_trace_id("test-123")
    assert get_trace_id() == "test-123"
    
    reset_trace_id(token)
    assert get_trace_id() is None


def test_trace_context():
    assert get_trace_id() is None
    
    with trace_context("context-456"):
        assert get_trace_id() == "context-456"
    
    assert get_trace_id() is None
