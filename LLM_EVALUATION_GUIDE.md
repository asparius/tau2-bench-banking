# 🤖 LLM-Based Evaluation for Turkish Banking

## The Problem We Solved

### **Issue: Substring Matching Fails for Turkish**

The original evaluation used **simple substring matching** (`communicate_info`):
```python
if "Agent should clearly communicate" in message.content.lower():
    # ❌ This fails because agent responds in Turkish!
```

**Result**: Agent performs perfectly but gets 0 reward because:
- Agent says: "Hesabınızın güncel bakiyesi: 2.500 TL" (Turkish)
- Evaluation looks for: "account balance" (English)
- ❌ No match → 0 reward

### **Solution: LLM-as-a-Judge** ✅

We switched to **NL Assertions** which uses an LLM to evaluate:
```python
# LLM evaluates if agent met the expectation, regardless of language
nl_assertion = "Agent should provide clear account balance information"
# ✅ LLM understands that Turkish response meets this criterion!
```

---

## What Changed

### **Before (Substring Matching):**
```json
{
    "evaluation_criteria": {
        "communicate_info": [
            "Agent should clearly communicate the current account balance",
            "Agent should explain recent transactions"
        ],
        "reward_basis": ["DB", "COMMUNICATE"]
    }
}
```

**How it evaluates:**
```python
# Simple string search
if "account balance" in agent_message.lower():
    ✅ Pass
else:
    ❌ Fail  # <-- Fails for Turkish!
```

### **After (LLM-Based Evaluation):**
```json
{
    "evaluation_criteria": {
        "nl_assertions": [
            "Agent should verify Turkish customer identity using TC Kimlik No",
            "Agent should provide clear account balance information in Turkish Lira",
            "Agent should explain recent Turkish banking transactions"
        ],
        "reward_basis": ["DB", "NL_ASSERTION"]
    }
}
```

**How it evaluates:**
```python
# LLM reads the conversation and evaluates semantically
llm_prompt = """
Did the agent verify customer identity using TC Kimlik No?
Did the agent provide clear account balance information?
"""
# ✅ LLM understands Turkish and semantic meaning!
```

---

## Benefits of LLM Evaluation

### **1. Language Agnostic** 🌍
- ✅ Works with Turkish responses
- ✅ Works with any language
- ✅ No need for translation

### **2. Semantic Understanding** 🧠
- ✅ Understands paraphrasing
- ✅ Recognizes equivalent information
- ✅ Evaluates intent, not exact words

### **3. Robust** 💪
- ✅ Handles different phrasings
- ✅ Handles formatting variations
- ✅ More realistic evaluation

### **4. Flexible** 🎯
- ✅ Can evaluate complex criteria
- ✅ Can check multiple aspects
- ✅ Provides reasoning for decisions

---

## Example: Real Simulation

### **Agent Response (Turkish):**
```
"Kimlik doğrulamanız başarıyla tamamlandı Ayşe Hanım.

Hesabınızın güncel bakiyesi: 2.500 TL'dir.

Son işlemlerinizden bazıları:
1. 10 Ocak 2025 – 500 TL yatırma (maaş yatırımı) – tamamlandı
2. 9 Ocak 2025 – 100 TL çekme – tamamlandı"
```

### **Evaluation with Substring Matching:**
```
Looking for: "account balance"
In message: "Hesabınızın güncel bakiyesi: 2.500 TL'dir"
❌ FAIL - "account balance" not found!
```

### **Evaluation with LLM-as-a-Judge:**
```
NL Assertion: "Agent should provide clear account balance information in Turkish Lira"
LLM Analysis: "The agent clearly states 'Hesabınızın güncel bakiyesi: 2.500 TL'
               which is the account balance in Turkish Lira."
✅ PASS - Criterion met!
```

---

## How to Run with NL Assertions

### **Default Evaluation (uses reward_basis from task):**
```bash
tau2 run --domain banking --task-ids banking_001
```

This will now use **NL_ASSERTION** evaluation because we set:
```json
"reward_basis": ["DB", "NL_ASSERTION"]
```

### **Force Specific Evaluation Type:**
```bash
# Use only NL assertions
tau2 run --domain banking --evaluation-type nl_assertions

# Use all evaluations including NL assertions
tau2 run --domain banking --evaluation-type all_with_nl_assertions
```

---

## NL Assertions in Turkish Banking

### **Our NL Assertions Check:**

#### **Banking Task 001 (Balance Inquiry)**
```json
[
    "Agent should verify Turkish customer identity using TC Kimlik No before providing account information",
    "Agent should provide clear and accurate Turkish bank account balance information in Turkish Lira (TL)",
    "Agent should explain recent Turkish banking transactions in an understandable way"
]
```

**What the LLM Evaluates:**
1. ✅ Did agent verify identity with TC Kimlik No?
2. ✅ Did agent communicate the balance in Turkish Lira?
3. ✅ Did agent explain the transactions clearly?

**The LLM can evaluate this regardless of:**
- Language (Turkish/English/Mixed)
- Phrasing (exact words don't matter)
- Format (numbers, currency symbols, etc.)

---

## Cost Considerations

### **Substring Matching (communicate_info):**
- Cost: $0 (no LLM calls)
- Speed: Instant
- Accuracy: Low (brittle, language-specific)

### **LLM Evaluation (nl_assertions):**
- Cost: ~$0.001-0.01 per evaluation (small)
- Speed: Few seconds per task
- Accuracy: High (semantic understanding)

**Recommendation:** Use LLM evaluation for production/research use cases.

---

## Summary

✅ **Changed from:** `communicate_info` (substring matching)  
✅ **Changed to:** `nl_assertions` (LLM-as-a-judge)  
✅ **Benefit:** Works with Turkish language and semantic understanding  
✅ **Trade-off:** Small cost increase, much better accuracy  

**Result:** Agent's Turkish responses will now be properly evaluated! 🇹🇷

---

## Commands to Run

```bash
# Run with NL assertions (now default for banking)
tau2 run --domain banking --task-ids banking_001

# View results
tau2 view
```

The simulation will now properly evaluate Turkish banking conversations!
