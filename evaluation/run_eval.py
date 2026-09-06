"""
run_eval.py

Runs every test case through the core decision pipeline (chaining
node functions directly, same pattern as our individual node tests),
compares actual outcomes against expected ones, and reports accuracy.
"""

from nodes.classify_email import classify_email
from nodes.understand_problem import understand_problem
from nodes.search_crm import search_crm
from nodes.search_knowledge_base import search_knowledge_base
from nodes.determine_resolution import determine_resolution
from nodes.risk_evaluation import risk_evaluation

from evaluation.test_cases import TEST_CASES


def run_pipeline(email_text: str, customer_id: str) -> dict:
    """
    Chains the core nodes together manually -- same pattern as the
    graph, but run directly in Python (no LangGraph machinery needed
    for evaluation purposes).
    """
    state = {"email_text": email_text, "customer_id": customer_id}

    state.update(classify_email(state))
    state.update(understand_problem(state))
    state.update(search_crm(state))
    state.update(search_knowledge_base(state))
    state.update(determine_resolution(state))
    state.update(risk_evaluation(state))

    return state


def run_evaluation():
    results = []

    for case in TEST_CASES:
        print(f"\n{'='*60}")
        print(f"Running: {case['name']}")
        print('='*60)

        final_state = run_pipeline(case["email_text"], case["customer_id"])

        category_correct = final_state["category"] == case["expected_category"]
        risk_correct = final_state["risk_flag"] == case["expected_risk_flag"]

        results.append({
            "name": case["name"],
            "category_correct": category_correct,
            "risk_correct": risk_correct,
            "actual_category": final_state["category"],
            "expected_category": case["expected_category"],
            "actual_risk": final_state["risk_flag"],
            "expected_risk": case["expected_risk_flag"],
        })

    total = len(results)
    category_accuracy = sum(r["category_correct"] for r in results) / total
    risk_accuracy = sum(r["risk_correct"] for r in results) / total

    print(f"\n\n{'='*60}")
    print("EVALUATION SUMMARY")
    print('='*60)
    for r in results:
        cat_mark = "PASS" if r["category_correct"] else "FAIL"
        risk_mark = "PASS" if r["risk_correct"] else "FAIL"
        print(f"{r['name']}:")
        print(f"  Category [{cat_mark}] expected={r['expected_category']} actual={r['actual_category']}")
        print(f"  Risk     [{risk_mark}] expected={r['expected_risk']} actual={r['actual_risk']}")

    print(f"\nClassification accuracy: {category_accuracy*100:.1f}% ({sum(r['category_correct'] for r in results)}/{total})")
    print(f"Risk evaluation accuracy: {risk_accuracy*100:.1f}% ({sum(r['risk_correct'] for r in results)}/{total})")


if __name__ == "__main__":
    run_evaluation()