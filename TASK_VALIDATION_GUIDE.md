# 🎯 How to Know Your Tasks Make Sense

## **1. Run the Validation Tests** ✅

The primary way to validate your tasks is through automated testing:

```bash
# Test if tasks load correctly
python -m pytest tests/test_domains/test_banking/test_turkish_banking_tasks.py -v
```

### What the Tests Check:

#### **A. Schema Validation**
- ✅ Tasks can be loaded without Pydantic errors
- ✅ All required fields are present
- ✅ Field types match expected formats
- ✅ References point to valid database entities

#### **B. Data Consistency**
- ✅ Customer IDs exist in database
- ✅ Account IDs belong to correct customers
- ✅ Loan IDs are valid
- ✅ Credit card IDs are valid

#### **C. Turkish Banking Compliance**
- ✅ Uses TC Kimlik No (not SSN)
- ✅ Uses Turkish names
- ✅ References Turkish account types
- ✅ Uses Turkish Lira (TL)

## **2. Manual Review Checklist** 📋

For each task, verify:

### **Task Structure**
- [ ] Has unique `id`
- [ ] Has `description` with purpose
- [ ] Has `user_scenario` with instructions
- [ ] Has `evaluation_criteria`

### **Turkish Banking Data**
- [ ] Customer has Turkish name
- [ ] Uses TC Kimlik No (not SSN)
- [ ] References Turkish account types (vadesiz_mevduat, vadeli_mevduat, etc.)
- [ ] Uses Turkish transaction types (yatırım, çekme, havale, etc.)
- [ ] Amounts in Turkish Lira (TL)

### **Evaluation Criteria**
- [ ] `actions`: Defines exact tool calls agent should make
- [ ] `communicate_info`: Lists info agent should tell user
- [ ] `nl_assertions`: Natural language checks

### **Realistic Scenarios**
- [ ] Scenario makes sense for Turkish banking
- [ ] Customer motivation is clear
- [ ] Expected outcome is achievable
- [ ] Follows Turkish banking policies

## **3. Common Validation Errors** ⚠️

### **Error Type 1: Schema Validation Error**
```
pydantic_core._pydantic_core.ValidationError: Field required
```
**Meaning**: Your task JSON doesn't match the expected schema

**Fix**: Check the field names and types match the Task model

### **Error Type 2: Reference Error**
```
AssertionError: Task banking_004 missing TC Kimlik No reference
```
**Meaning**: Task data doesn't match Turkish banking format

**Fix**: Update customer info to use TC Kimlik No instead of SSN

### **Error Type 3: Empty Evaluation Criteria**
```
AssertionError: Task banking_001 has no actions
```
**Meaning**: Evaluation criteria incomplete

**Fix**: Define expected agent actions

## **4. Example of Well-Defined Task** 💡

```json
{
    "id": "banking_001",
    "description": {
        "purpose": "Turkish customer wants to check account balance",
        "relevant_policies": "Turkish Account Access and Information, Turkish Identity Verification",
        "notes": "Standard Turkish banking balance inquiry"
    },
    "user_scenario": {
        "persona": null,
        "instructions": {
            "task_instructions": "You want to check your Turkish bank account balance.",
            "domain": "banking",
            "reason_for_call": "Check account balance in Turkish Lira (TL).",
            "known_info": "You are Ayşe Yılmaz. Customer ID: customer_1001. TC Kimlik No: 12345678901. DOB: 1985-03-15."
        }
    },
    "evaluation_criteria": {
        "actions": [
            {
                "action_id": "verify_identity",
                "name": "verify_customer_identity",
                "arguments": {
                    "customer_id": "customer_1001",
                    "tc_no": "12345678901",
                    "date_of_birth": "1985-03-15"
                }
            },
            {
                "action_id": "get_balance",
                "name": "get_account_info",
                "arguments": {
                    "account_id": "account_2001"
                }
            }
        ],
        "communicate_info": [
            "Agent should clearly communicate the current account balance in Turkish Lira (TL)",
            "Agent should confirm the account type (vadesiz mevduat)"
        ],
        "nl_assertions": [
            "Agent should verify Turkish customer identity using TC Kimlik No",
            "Agent should provide balance in Turkish Lira (TL)"
        ]
    }
}
```

## **5. Validation Workflow** 🔄

```
1. Write/Update Task
         ↓
2. Run Tests
         ↓
3. Fix Errors ←─┐
         ↓      │
4. Tests Pass? ─┘ (No)
         ↓ (Yes)
5. Manual Review
         ↓
6. Task is Valid! ✅
```

## **6. Current Status of Your Tasks** 📊

After running tests, you know:

- **12/15 tests passing** = Tasks are **80% valid**
- **Remaining issues**:
  1. Update task banking_004 to use TC Kimlik No
  2. Define actions for evaluation criteria
  3. Update one test for new format

## **7. Quick Validation Command** ⚡

```bash
# Full validation
source venv/bin/activate && \
python -m pytest tests/test_domains/test_banking/test_turkish_banking_tasks.py -v && \
echo "✅ All tasks valid!"
```

## **8. What "Makes Sense" Means** 🤔

A task "makes sense" when:

1. **Technically Valid**: Passes all schema validation
2. **Semantically Correct**: Scenario is realistic and achievable
3. **Culturally Appropriate**: Matches Turkish banking practices
4. **Properly Evaluated**: Has clear success criteria

Your tasks make sense when:
- ✅ Tests pass
- ✅ Agent can complete the task using available tools
- ✅ Success can be objectively measured
- ✅ Follows Turkish banking regulations

---

**Remember**: The tests are your friend! They tell you exactly what's wrong and how to fix it.
