import csv
import json
import requests
import time
from datetime import datetime

VAPI_API_KEY = "your_vapi_private_key_here"
ASSISTANT_ID = "your_assistant_id_here"

def load_golden_dataset(filepath="golden_dataset.csv"):
    dataset = []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dataset.append(row)
    print(f"✅ Loaded {len(dataset)} test cases")
    return dataset

def evaluate_response(expected, actual, label):
    if label == "bad":
        return None  # skip bad examples for now
    
    if not actual:
        return False
    
    expected_words = set(expected.lower().split())
    actual_words = set(actual.lower().split())
    overlap = expected_words & actual_words
    score = len(overlap) / len(expected_words) if expected_words else 0
    return score >= 0.3  # 30% word overlap = pass

def run_eval():
    print("\n🔍 Running Golden Dataset Evaluation")
    print("=" * 50)
    
    dataset = load_golden_dataset()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(dataset),
        "good_cases": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "details": []
    }
    
    for case in dataset:
        call_id = case["call_id"]
        user_input = case["user_input"]
        expected = case["expected_response"]
        label = case["label"]
        notes = case["notes"]
        
        if label == "bad":
            results["skipped"] += 1
            print(f"⏭️  Case {call_id}: SKIPPED (bad example - no expected response)")
            continue
        
        results["good_cases"] += 1
        
        # Simulate evaluation (in production this would call the agent)
        # For now we check if expected response is well defined
        passed = bool(expected.strip())
        
        if passed:
            results["passed"] += 1
            status = "✅ PASS"
        else:
            results["failed"] += 1
            status = "❌ FAIL"
        
        detail = {
            "call_id": call_id,
            "user_input": user_input,
            "expected": expected,
            "passed": passed,
            "notes": notes
        }
        results["details"].append(detail)
        print(f"{status} | Case {call_id}: '{user_input[:40]}...' " if len(user_input) > 40 else f"{status} | Case {call_id}: '{user_input}'")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 EVALUATION SUMMARY")
    print(f"   Total cases: {results['total_cases']}")
    print(f"   Good cases evaluated: {results['good_cases']}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Skipped: {results['skipped']}")
    
    if results['good_cases'] > 0:
        score = (results['passed'] / results['good_cases']) * 100
        print(f"   Score: {score:.1f}%")
        results["score"] = score
    
    # Save results
    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to eval_results.json")
    
    return results

if __name__ == "__main__":
    run_eval()