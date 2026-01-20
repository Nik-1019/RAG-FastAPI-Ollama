import requests
import os

def test_kubernetes_query():
    response = requests.post("http://127.0.0.1:8000/query", json={"q": "What is Kubernetes?"})
    
    if response.status_code != 200:
        raise Exception(f"Server returned {response.status_code}: {response.text}")
    
    answer = response.json()["answer"]
    assert "container" in answer.lower(), "Missing 'container' keyword"
    print("✅ Kubernetes query test passed")

def test_deterministic_guard():
    # Test with word not in context - should trigger safety guard
    response = requests.post("http://127.0.0.1:8000/query", json={"q": "What is Kubernetes orchestration?"})
    
    if response.status_code != 200:
        raise Exception(f"Server returned {response.status_code}: {response.text}")
    
    answer = response.json()["answer"]
    expected = "I do not know. The information is not available in the knowledge base."
    assert answer == expected, f"Expected safety guard response, got: {answer}"
    print("✅ Deterministic guard test passed")

if __name__ == "__main__":
    # Set mock mode for testing
    os.environ["USE_MOCK_LLM"] = "1"
    
    test_kubernetes_query()
    test_deterministic_guard()
    print("All semantic tests passed!")
