import pytest
from tau2.domains.banking.data_model import BankingDB
from tau2.domains.banking.environment import get_environment, get_tasks
from tau2.domains.banking.utils import BANKING_DB_PATH


class TestTurkishBankingIntegration:
    """Test Turkish banking domain integration and environment setup."""

    @pytest.fixture
    def banking_db(self):
        """Load Turkish banking database for testing."""
        return BankingDB.load(BANKING_DB_PATH)

    @pytest.fixture
    def banking_environment(self):
        """Create Turkish banking environment."""
        return get_environment()

    def test_turkish_banking_environment_creation(self, banking_environment):
        """Test that Turkish banking environment is created correctly."""
        assert banking_environment.domain_name == "banking"
        assert banking_environment.tools is not None
        assert banking_environment.policy is not None
        assert len(banking_environment.tools.tools) > 0

    def test_turkish_banking_tools_registration(self, banking_environment):
        """Test that all Turkish banking tools are properly registered."""
        tools = banking_environment.tools.tools
        
        # Check that key Turkish banking tools are available
        expected_tools = [
            "get_customer_info",
            "verify_customer_identity", 
            "get_account_info",
            "get_customer_accounts",
            "freeze_account",
            "unfreeze_account",
            "process_transfer",
            "process_deposit",
            "process_withdrawal",
            "get_loan_info",
            "process_loan_payment",
            "get_credit_card_info",
            "process_credit_card_payment"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tools, f"Tool {tool_name} not found in banking environment"

    def test_turkish_banking_policy_content(self, banking_environment):
        """Test that Turkish banking policy contains relevant content."""
        policy = banking_environment.policy
        
        # Check that policy contains key banking terms
        assert "banking" in policy.lower()
        assert "customer" in policy.lower()
        assert "account" in policy.lower()
        assert "security" in policy.lower()

    def test_turkish_banking_tasks_loading(self):
        """Test that Turkish banking tasks are loaded correctly."""
        tasks = get_tasks()
        
        assert len(tasks) > 0, "No banking tasks loaded"
        
        # Check that tasks have proper structure
        for task in tasks:
            assert hasattr(task, 'id')
            assert hasattr(task, 'description')
            assert hasattr(task, 'user_scenario')
            assert hasattr(task, 'evaluation_criteria')

    def test_turkish_banking_database_structure(self, banking_db):
        """Test Turkish banking database structure."""
        # Check that database has all required collections
        assert hasattr(banking_db, 'customers')
        assert hasattr(banking_db, 'accounts')
        assert hasattr(banking_db, 'transactions')
        assert hasattr(banking_db, 'loans')
        assert hasattr(banking_db, 'credit_cards')
        
        # Check that we have Turkish customer data
        assert len(banking_db.customers) > 0
        assert len(banking_db.accounts) > 0

    def test_turkish_customer_data_structure(self, banking_db):
        """Test Turkish customer data structure."""
        customer = banking_db.customers[0]
        
        # Check Turkish-specific fields
        assert hasattr(customer, 'tc_no')  # Turkish Republic Identity Number
        assert hasattr(customer, 'first_name')
        assert hasattr(customer, 'last_name')
        assert hasattr(customer, 'address')
        
        # Check address structure
        address = customer.address
        assert hasattr(address, 'district')  # Turkish ilçe
        assert hasattr(address, 'city')      # Turkish il
        assert hasattr(address, 'postal_code')
        assert hasattr(address, 'country')
        
        # Verify Turkish address format
        assert address.country == "Turkey"

    def test_turkish_account_types(self, banking_db):
        """Test Turkish account types in database."""
        # Check that accounts use Turkish account types
        for account in banking_db.accounts:
            assert account.account_type in [
                "vadesiz_mevduat",    # Checking account
                "vadeli_mevduat",     # Savings account
                "altin_hesabi",       # Gold account
                "doviz_hesabi",       # Foreign currency account
                "ticari_mevduat",     # Business account
                "ogrenci_hesabi",     # Student account
                "emekli_hesabi",      # Senior account
                "yatirim_hesabi"      # Investment account
            ]

    def test_turkish_loan_types(self, banking_db):
        """Test Turkish loan types in database."""
        # Check that loans use Turkish loan types
        for loan in banking_db.loans:
            assert loan.loan_type in [
                "ihtiyac_kredisi",    # Personal loan
                "tasit_kredisi",      # Auto loan
                "konut_kredisi",      # Mortgage
                "ipotekli_kredi",     # Home equity
                "ogrenci_kredisi",    # Student loan
                "ticari_kredi",       # Business loan
                "kredi_limiti",       # Credit line
                "altin_kredisi",      # Gold loan
                "tarim_kredisi"       # Agricultural loan
            ]

    def test_turkish_transaction_types(self, banking_db):
        """Test Turkish transaction types in database."""
        # Check that transactions use Turkish transaction types
        for transaction in banking_db.transactions:
            assert transaction.transaction_type in [
                "yatirim",            # Deposit
                "cekme",              # Withdrawal
                "havale_gelen",       # Transfer in
                "havale_giden",       # Transfer out
                "odeme",              # Payment
                "komisyon",           # Fee
                "faiz",               # Interest
                "iade",               # Refund
                "eft",                # EFT
                "swift",              # SWIFT
                "altin_alim",         # Gold purchase
                "altin_satim",        # Gold sale
                "doviz_cevirim",      # Foreign exchange
                "kredi_karti_odeme",  # Credit card payment
                "kredi_odeme"         # Loan payment
            ]

    def test_turkish_banking_environment_solo_mode(self):
        """Test Turkish banking environment in solo mode."""
        env = get_environment(solo_mode=True)
        
        assert env.domain_name == "banking"
        assert env.solo_mode is True
        assert env.tools is not None

    def test_turkish_banking_database_statistics(self, banking_db):
        """Test Turkish banking database statistics."""
        stats = banking_db.get_statistics()
        
        # Check that statistics are calculated correctly
        assert "num_customers" in stats
        assert "num_accounts" in stats
        assert "num_transactions" in stats
        assert "num_loans" in stats
        assert "num_credit_cards" in stats
        
        # Check that we have data
        assert stats["num_customers"] > 0
        assert stats["num_accounts"] > 0

    def test_turkish_banking_customer_phone_formats(self, banking_db):
        """Test Turkish phone number formats in customer data."""
        for customer in banking_db.customers:
            # Check that phone numbers follow Turkish format (+90)
            assert customer.phone_number.startswith("+90")
            assert len(customer.phone_number) >= 13  # +90 + 10 digits

    def test_turkish_banking_customer_names(self, banking_db):
        """Test Turkish names in customer data."""
        turkish_names = ["Ayşe", "Mehmet", "Fatma", "Ali", "Zeynep", "Mustafa", "Elif", "Ahmet"]
        
        for customer in banking_db.customers:
            assert customer.first_name in turkish_names, f"Non-Turkish name found: {customer.first_name}"

    def test_turkish_banking_customer_cities(self, banking_db):
        """Test Turkish cities in customer addresses."""
        turkish_cities = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"]
        
        for customer in banking_db.customers:
            assert customer.address.city in turkish_cities, f"Non-Turkish city found: {customer.address.city}"

    def test_turkish_banking_postal_codes(self, banking_db):
        """Test Turkish postal code format in customer addresses."""
        for customer in banking_db.customers:
            postal_code = customer.address.postal_code
            # Turkish postal codes are 5 digits
            assert len(postal_code) == 5
            assert postal_code.isdigit()

    def test_turkish_banking_environment_tool_functionality(self, banking_environment):
        """Test that Turkish banking environment tools work correctly."""
        tools = banking_environment.tools
        
        # Test customer info retrieval
        customer_info = tools.get_customer_info("customer_1001")
        assert "error" not in customer_info
        assert customer_info["name"] == "Ayşe Yılmaz"
        
        # Test account info retrieval
        account_info = tools.get_account_info("account_2001")
        assert "error" not in account_info
        assert account_info["account_type"] == "vadesiz_mevduat"

    def test_turkish_banking_environment_error_handling(self, banking_environment):
        """Test Turkish banking environment error handling."""
        tools = banking_environment.tools
        
        # Test error handling for non-existent customer
        result = tools.get_customer_info("nonexistent_customer")
        assert "error" in result
        
        # Test error handling for non-existent account
        result = tools.get_account_info("nonexistent_account")
        assert "error" in result

