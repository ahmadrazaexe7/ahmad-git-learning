import json
import re
from typing import List, Dict, Any
from collections import Counter

def extract_json_objects(text: str) -> List[Dict[Any, Any]]:
    """Extract top-level JSON objects from raw text."""
    # Remove trailing commas before closing brackets/braces
    text = re.sub(r',\s*([\}\]])', r'\1', text)
    
    objects = []
    depth = 0
    start = None
    in_string = False
    escape = False

    for i, char in enumerate(text):
        if not escape and char == '"':
            in_string = not in_string
        elif not in_string:
            if char == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and start is not None:
                    try:
                        obj = json.loads(text[start:i+1])
                        objects.append(obj)
                    except json.JSONDecodeError:
                        pass
        if char == '\\' and not escape:
            escape = True
        else:
            escape = False

    return objects

def detect_complexity(instruction: str) -> str:
    """Detect complexity from instruction text."""
    lower = instruction.lower()
    if "advanced" in lower:
        return "advanced"
    elif "intermediate" in lower:
        return "intermediate"
    else:
        return "basic"

def is_valid_entry(entry: Dict) -> bool:
    """Validate entry has required fields (no metadata needed)."""
    required = {"instruction", "input", "output"}
    return (
        required.issubset(entry.keys()) and
        isinstance(entry["input"], dict) and
        bool(entry.get("output", "").strip()) and
        bool(entry.get("instruction", "").strip())
    )

def clean_and_count(raw_text: str):
    candidates = extract_json_objects(raw_text)
    valid_entries = [e for e in candidates if is_valid_entry(e)]
    
    # Count by complexity from instruction text
    complexity_counts = Counter(
        detect_complexity(entry["instruction"]) for entry in valid_entries
    )
    
    return valid_entries, complexity_counts

# === MAIN EXECUTION ===
if __name__ == "__main__":
    input_path = "liqud.jsonl"
    output_path = "cleaned_3.json"

    with open(input_path, "r", encoding="utf-8") as f:
        raw = f.read()

    cleaned, counts = clean_and_count(raw)

    total = len(cleaned)
    print(f"✅ Total valid entries: {total}")
    print("\n📊 Breakdown by complexity:")
    print(f"  Basic:       {counts.get('basic', 0)}")
    print(f"  Intermediate: {counts.get('intermediate', 0)}")
    print(f"  Advanced:     {counts.get('advanced', 0)}")

    # Save cleaned data
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Cleaned dataset saved to: {output_path}")