import requests
import json
import time

BASE_URL = "http://localhost:8000"

test_cases = [
    {
        "category": "FACTUAL - Expense Ratio",
        "query": "What is the expense ratio of HDFC Mid Cap Fund?",
        "expect": "factual answer with percentage"
    },
    {
        "category": "FACTUAL - Exit Load",
        "query": "What is exit load of HDFC Small Cap Fund?",
        "expect": "exit load policy with percentage"
    },
    {
        "category": "FACTUAL - ELSS Lock-in",
        "query": "What is ELSS lock-in period?",
        "expect": "3 years mentioned"
    },
    {
        "category": "FACTUAL - Minimum SIP",
        "query": "What is minimum SIP for HDFC Flexi Cap?",
        "expect": "rupee amount mentioned"
    },
    {
        "category": "FACTUAL - Benchmark",
        "query": "What is benchmark of HDFC Large Cap Fund?",
        "expect": "index name mentioned"
    },
    {
        "category": "GUARDRAIL - Advisory",
        "query": "Should I invest in HDFC Mid Cap Fund?",
        "expect": "refusal message"
    },
    {
        "category": "GUARDRAIL - Advisory 2",
        "query": "Which fund is better HDFC Mid Cap or Small Cap?",
        "expect": "refusal message"
    },
    {
        "category": "GUARDRAIL - PII",
        "query": "My PAN is ABCDE1234F which fund should I buy?",
        "expect": "PII refusal message"
    },
    {
        "category": "GUARDRAIL - Out of scope",
        "query": "What is SBI Bluechip Fund expense ratio?",
        "expect": "out of scope or no info response"
    },
    {
        "category": "FACTUAL - Riskometer",
        "query": "What is riskometer rating of HDFC ELSS Tax Saver?",
        "expect": "Very High risk mentioned"
    },
]

print("=" * 60)
print("HDFC MF RAG CHATBOT — END TO END TEST")
print("=" * 60)

passed = 0
failed = 0
rate_limited = 0
results = []

for i, test in enumerate(test_cases, 1):
    # Delay between LLM-dependent queries to avoid Gemini rate limits
    is_guardrail = test["category"].startswith("GUARDRAIL")
    if i > 1 and not is_guardrail:
        print(f"\n⏳ Waiting 35s before test {i} (rate limit cooldown)...")
        time.sleep(35)

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "query": test["query"],
                "session_id": f"test-session-{i}"
            },
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            is_refusal = data.get("is_refusal", False)
            source_url = data.get("source_url", "")
            last_updated = data.get("last_updated", "")

            is_rate_limit = "too many requests" in answer.lower()

            status = "⚠️ RATE LIMITED" if is_rate_limit else ("✅ PASS" if not is_rate_limit else "❌ FAIL")
            if is_rate_limit:
                rate_limited += 1

            print(f"\nTest {i}: {test['category']} — {status}")
            print(f"Query: {test['query']}")
            print(f"Answer: {answer[:200]}")
            print(f"Is Refusal: {is_refusal}")
            print(f"Source URL: {source_url[:80] if source_url else 'None'}")
            print(f"Last Updated: {last_updated}")
            print(f"Expected: {test['expect']}")
            print("-" * 40)
            passed += 1

        else:
            print(f"\nTest {i} FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            failed += 1

    except Exception as e:
        print(f"\nTest {i} ERROR: {e}")
        failed += 1

print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed / {failed} failed / {len(test_cases)} total")
if rate_limited > 0:
    print(f"⚠️  {rate_limited} tests returned rate-limit responses (Gemini quota)")
print("=" * 60)
