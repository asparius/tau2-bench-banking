import pytest
from tau2.domains.banking.environment import get_tasks
from tau2.domains.banking.data_model import BankingDB
from tau2.domains.banking.utils import BANKING_DB_PATH


class TestTurkishBankingTasks:
    """Test Turkish banking tasks and scenarios."""

    @pytest.fixture
    def banking_tasks(self):
        """Load Turkish banking tasks."""
        return get_tasks()

    @pytest.fixture
    def banking_db(self):
        """Load Turkish banking database."""
        return BankingDB.load(BANKING_DB_PATH)

    def test_turkish_banking_tasks_loaded(self, banking_tasks):
        """Test that Turkish banking tasks are loaded correctly."""
        assert len(banking_tasks) > 0, "No banking tasks loaded"
        
        # Check that we have the expected number of tasks
        assert len(banking_tasks) >= 8, f"Expected at least 8 tasks, got {len(banking_tasks)}"

    def test_turkish_banking_task_structure(self, banking_tasks):
        """Test Turkish banking task structure."""
        for task in banking_tasks:
            # Check required fields
            assert hasattr(task, 'id'), f"Task {task} missing id"
            assert hasattr(task, 'description'), f"Task {task} missing description"
            assert hasattr(task, 'user_scenario'), f"Task {task} missing user_scenario"
            assert hasattr(task, 'evaluation_criteria'), f"Task {task} missing evaluation_criteria"
            
            # Check task ID format
            assert task.id.startswith("banking_"), f"Task {task.id} should start with 'banking_'"

    def test_turkish_banking_task_descriptions(self, banking_tasks):
        """Test Turkish banking task descriptions."""
        for task in banking_tasks:
            description = task.description
            
            # Check that description has required fields
            assert hasattr(description, 'purpose'), f"Task {task.id} missing purpose"
            assert description.purpose is not None, f"Task {task.id} has empty purpose"

    def test_turkish_banking_user_scenarios(self, banking_tasks):
        """Test Turkish banking user scenarios."""
        for task in banking_tasks:
            scenario = task.user_scenario
            
            # Check that scenario has required fields
            assert hasattr(scenario, 'instructions'), f"Task {task.id} missing instructions"
            
            instructions = scenario.instructions
            assert hasattr(instructions, 'task_instructions'), f"Task {task.id} missing task_instructions"
            assert hasattr(instructions, 'domain'), f"Task {task.id} missing domain"
            assert hasattr(instructions, 'reason_for_call'), f"Task {task.id} missing reason_for_call"
            assert hasattr(instructions, 'known_info'), f"Task {task.id} missing known_info"
            
            # Check domain is banking
            assert instructions.domain == "banking", f"Task {task.id} has wrong domain: {instructions.domain}"

    def test_turkish_banking_task_known_info(self, banking_tasks):
        """Test Turkish banking task known info contains Turkish data."""
        for task in banking_tasks:
            known_info = task.user_scenario.instructions.known_info
            
            # Check that known_info contains Turkish customer references
            assert "customer_" in known_info, f"Task {task.id} missing customer reference"
            assert "TC" in known_info or "tc_no" in known_info, f"Task {task.id} missing TC Kimlik No reference"

    def test_turkish_banking_evaluation_criteria(self, banking_tasks):
        """Test Turkish banking evaluation criteria."""
        for task in banking_tasks:
            criteria = task.evaluation_criteria
            
            # Check that criteria has required fields
            assert hasattr(criteria, 'actions'), f"Task {task.id} missing actions"
            assert hasattr(criteria, 'communicate_info'), f"Task {task.id} missing communicate_info"
            assert hasattr(criteria, 'nl_assertions'), f"Task {task.id} missing nl_assertions"
            
            # Check that we have evaluation criteria
            assert len(criteria.actions) > 0, f"Task {task.id} has no actions"
            assert len(criteria.communicate_info) > 0, f"Task {task.id} has no communicate_info"
            assert len(criteria.nl_assertions) > 0, f"Task {task.id} has no nl_assertions"

    def test_turkish_banking_task_actions(self, banking_tasks):
        """Test Turkish banking task actions."""
        for task in banking_tasks:
            actions = task.evaluation_criteria.actions
            
            for action in actions:
                # Check action structure
                assert hasattr(action, 'action_id'), f"Action in task {task.id} missing action_id"
                assert hasattr(action, 'description'), f"Action in task {task.id} missing description"
                
                # Check that action IDs are meaningful
                assert action.action_id is not None, f"Action in task {task.id} has empty action_id"

    def test_turkish_banking_task_initial_states(self, banking_tasks):
        """Test Turkish banking task initial states."""
        for task in banking_tasks:
            if hasattr(task, 'initial_state') and task.initial_state is not None:
                initial_state = task.initial_state
                
                # Check initial state structure
                assert hasattr(initial_state, 'initialization_data'), f"Task {task.id} missing initialization_data"
                assert hasattr(initial_state, 'initialization_actions'), f"Task {task.id} missing initialization_actions"
                assert hasattr(initial_state, 'message_history'), f"Task {task.id} missing message_history"

    def test_turkish_banking_task_customer_references(self, banking_tasks, banking_db):
        """Test that task customer references exist in database."""
        # Get all customer IDs from database
        db_customer_ids = {customer.customer_id for customer in banking_db.customers}
        
        for task in banking_tasks:
            known_info = task.user_scenario.instructions.known_info
            
            # Extract customer ID from known_info
            if "customer_" in known_info:
                # Find customer ID in known_info
                lines = known_info.split('\n')
                for line in lines:
                    if "customer_" in line and "Your customer ID is" in line:
                        customer_id = line.split("customer_")[1].split(".")[0]
                        customer_id = f"customer_{customer_id}"
                        
                        # Check that customer exists in database
                        assert customer_id in db_customer_ids, f"Task {task.id} references non-existent customer {customer_id}"

    def test_turkish_banking_task_account_references(self, banking_tasks, banking_db):
        """Test that task account references exist in database."""
        # Get all account IDs from database
        db_account_ids = {account.account_id for account in banking_db.accounts}
        
        for task in banking_tasks:
            if hasattr(task, 'initial_state') and task.initial_state is not None:
                init_data = task.initial_state.initialization_data
                
                if hasattr(init_data, 'account_id'):
                    account_id = init_data.account_id
                    assert account_id in db_account_ids, f"Task {task.id} references non-existent account {account_id}"

    def test_turkish_banking_task_loan_references(self, banking_tasks, banking_db):
        """Test that task loan references exist in database."""
        # Get all loan IDs from database
        db_loan_ids = {loan.loan_id for loan in banking_db.loans}
        
        for task in banking_tasks:
            if hasattr(task, 'initial_state') and task.initial_state is not None:
                init_data = task.initial_state.initialization_data
                
                if hasattr(init_data, 'loan_id'):
                    loan_id = init_data.loan_id
                    assert loan_id in db_loan_ids, f"Task {task.id} references non-existent loan {loan_id}"

    def test_turkish_banking_task_credit_card_references(self, banking_tasks, banking_db):
        """Test that task credit card references exist in database."""
        # Get all credit card IDs from database
        db_credit_card_ids = {card.card_id for card in banking_db.credit_cards}
        
        for task in banking_tasks:
            if hasattr(task, 'initial_state') and task.initial_state is not None:
                init_data = task.initial_state.initialization_data
                
                if hasattr(init_data, 'credit_card_id'):
                    credit_card_id = init_data.credit_card_id
                    assert credit_card_id in db_credit_card_ids, f"Task {task.id} references non-existent credit card {credit_card_id}"

    def test_turkish_banking_task_scenario_variety(self, banking_tasks):
        """Test that Turkish banking tasks cover various scenarios."""
        task_purposes = [task.description.purpose for task in banking_tasks]
        
        # Check that we have variety in task purposes
        unique_purposes = set(task_purposes)
        assert len(unique_purposes) > 1, "All tasks have the same purpose"
        
        # Check for common Turkish banking scenarios
        purpose_text = " ".join(task_purposes).lower()
        
        # These are common Turkish banking scenarios
        expected_scenarios = [
            "balance", "transfer", "payment", "deposit", "withdrawal", 
            "freeze", "loan", "credit", "identity", "verification"
        ]
        
        found_scenarios = [scenario for scenario in expected_scenarios if scenario in purpose_text]
        assert len(found_scenarios) >= 3, f"Expected at least 3 different banking scenarios, found: {found_scenarios}"

    def test_turkish_banking_task_evaluation_completeness(self, banking_tasks):
        """Test that Turkish banking tasks have complete evaluation criteria."""
        for task in banking_tasks:
            criteria = task.evaluation_criteria
            
            # Check that actions are well-defined
            for action in criteria.actions:
                assert action.action_id is not None and action.action_id != "", f"Task {task.id} has empty action_id"
                assert action.description is not None and action.description != "", f"Task {task.id} has empty action description"
            
            # Check that communication info is well-defined
            for comm_info in criteria.communicate_info:
                assert comm_info.info_id is not None and comm_info.info_id != "", f"Task {task.id} has empty info_id"
                assert comm_info.description is not None and comm_info.description != "", f"Task {task.id} has empty info description"
            
            # Check that natural language assertions are meaningful
            for assertion in criteria.nl_assertions:
                assert assertion is not None and assertion != "", f"Task {task.id} has empty nl_assertion"
                assert len(assertion) > 10, f"Task {task.id} has too short nl_assertion: {assertion}"

    def test_turkish_banking_task_consistency(self, banking_tasks):
        """Test consistency across Turkish banking tasks."""
        # Check that all tasks have consistent structure
        for task in banking_tasks:
            # All tasks should have the same basic structure
            assert hasattr(task, 'id')
            assert hasattr(task, 'description')
            assert hasattr(task, 'user_scenario')
            assert hasattr(task, 'evaluation_criteria')
            
            # All tasks should be in the banking domain
            assert task.user_scenario.instructions.domain == "banking"
            
            # All tasks should have evaluation criteria
            assert task.evaluation_criteria is not None

