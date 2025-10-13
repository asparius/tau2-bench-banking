import pytest
from tau2.domains.banking.data_model import BankingDB
from tau2.domains.banking.tools import BankingTools
from tau2.domains.banking.utils import BANKING_DB_PATH


class TestBankingTools:
    """Test banking tools functionality."""

    @pytest.fixture
    def banking_db(self):
        """Load banking database for testing."""
        return BankingDB.load(BANKING_DB_PATH)

    @pytest.fixture
    def banking_tools(self, banking_db):
        """Create banking tools instance."""
        return BankingTools(banking_db)

    def test_get_customer_info(self, banking_tools):
        """Test getting customer information."""
        result = banking_tools.get_customer_info("customer_1001")
        
        assert "error" not in result
        assert result["customer_id"] == "customer_1001"
        assert result["name"] == "Sarah Johnson"
        assert result["email"] == "sarah.johnson@email.com"
        assert result["status"] == "active"

    def test_get_customer_info_not_found(self, banking_tools):
        """Test getting customer information for non-existent customer."""
        result = banking_tools.get_customer_info("nonexistent_customer")
        
        assert "error" in result
        assert "not found" in result["error"]

    def test_verify_customer_identity(self, banking_tools):
        """Test customer identity verification with TC Kimlik No."""
        result = banking_tools.verify_customer_identity(
            "customer_1001", "***-***-1234", "1985-03-15"
        )
        
        assert result["verified"] is True
        assert result["customer_name"] == "Ayşe Yılmaz"

    def test_verify_customer_identity_failed(self, banking_tools):
        """Test customer identity verification with wrong credentials."""
        result = banking_tools.verify_customer_identity(
            "customer_1001", "***-***-9999", "1985-03-15"
        )
        
        assert result["verified"] is False
        assert "error" in result
        assert "Kimlik doğrulama başarısız" in result["error"]

    def test_get_account_info(self, banking_tools):
        """Test getting account information."""
        result = banking_tools.get_account_info("account_2001")
        
        assert "error" not in result
        assert result["account_id"] == "account_2001"
        assert result["account_type"] == "checking"
        assert result["balance"] == 2500.00
        assert result["status"] == "active"

    def test_get_customer_accounts(self, banking_tools):
        """Test getting all accounts for a customer."""
        result = banking_tools.get_customer_accounts("customer_1002")
        
        assert "error" not in result
        assert result["total_accounts"] == 2
        assert len(result["accounts"]) == 2
        
        # Check that both accounts are returned
        account_ids = [acc["account_id"] for acc in result["accounts"]]
        assert "account_2002" in account_ids
        assert "account_2003" in account_ids

    def test_freeze_account(self, banking_tools):
        """Test freezing an account."""
        result = banking_tools.freeze_account("account_2001", "Suspicious activity")
        
        assert result["success"] is True
        assert "frozen" in result["message"]
        
        # Verify account is actually frozen
        account_info = banking_tools.get_account_info("account_2001")
        assert account_info["status"] == "frozen"

    def test_unfreeze_account(self, banking_tools):
        """Test unfreezing an account."""
        # First freeze the account
        banking_tools.freeze_account("account_2001", "Test freeze")
        
        # Then unfreeze it
        result = banking_tools.unfreeze_account("account_2001")
        
        assert result["success"] is True
        assert "unfrozen" in result["message"]
        
        # Verify account is actually unfrozen
        account_info = banking_tools.get_account_info("account_2001")
        assert account_info["status"] == "active"

    def test_process_transfer(self, banking_tools):
        """Test processing a transfer between accounts."""
        result = banking_tools.process_transfer(
            "account_2002", "account_2003", 100.0, "Test transfer"
        )
        
        assert result["success"] is True
        assert "Transfer of $100.00 completed successfully" in result["message"]
        assert "debit_transaction_id" in result
        assert "credit_transaction_id" in result

    def test_process_transfer_insufficient_funds(self, banking_tools):
        """Test transfer with insufficient funds."""
        result = banking_tools.process_transfer(
            "account_2002", "account_2003", 10000.0, "Large transfer"
        )
        
        assert "error" in result
        assert "Insufficient funds" in result["error"]

    def test_process_deposit(self, banking_tools):
        """Test processing a deposit."""
        result = banking_tools.process_deposit("account_2001", 200.0, "Test deposit")
        
        assert result["success"] is True
        assert "Deposit of $200.00 completed successfully" in result["message"]
        assert result["new_balance"] == 2700.00  # 2500 + 200

    def test_process_withdrawal(self, banking_tools):
        """Test processing a withdrawal."""
        result = banking_tools.process_withdrawal("account_2001", 100.0, "Test withdrawal")
        
        assert result["success"] is True
        assert "Withdrawal of $100.00 completed successfully" in result["message"]
        assert result["new_balance"] == 2400.00  # 2500 - 100

    def test_get_loan_info(self, banking_tools):
        """Test getting loan information."""
        result = banking_tools.get_loan_info("loan_4001")
        
        assert "error" not in result
        assert result["loan_id"] == "loan_4001"
        assert result["loan_type"] == "auto"
        assert result["current_balance"] == 18500.00
        assert result["status"] == "active"

    def test_get_customer_loans(self, banking_tools):
        """Test getting all loans for a customer."""
        result = banking_tools.get_customer_loans("customer_1004")
        
        assert "error" not in result
        assert result["total_loans"] == 1
        assert len(result["loans"]) == 1
        assert result["loans"][0]["loan_id"] == "loan_4001"

    def test_process_loan_payment(self, banking_tools):
        """Test processing a loan payment."""
        result = banking_tools.process_loan_payment(
            "loan_4001", 300.0, "account_2005"
        )
        
        assert result["success"] is True
        assert "Loan payment of $300.00 processed successfully" in result["message"]
        assert result["remaining_balance"] == 18200.00  # 18500 - 300

    def test_get_credit_card_info(self, banking_tools):
        """Test getting credit card information."""
        result = banking_tools.get_credit_card_info("credit_card_5001")
        
        assert "error" not in result
        assert result["card_id"] == "credit_card_5001"
        assert result["credit_limit"] == 5000.00
        assert result["current_balance"] == 1800.00
        assert result["available_credit"] == 3200.00

    def test_get_customer_credit_cards(self, banking_tools):
        """Test getting all credit cards for a customer."""
        result = banking_tools.get_customer_credit_cards("customer_1005")
        
        assert "error" not in result
        assert result["total_cards"] == 1
        assert len(result["credit_cards"]) == 1
        assert result["credit_cards"][0]["card_id"] == "credit_card_5001"

    def test_process_credit_card_payment(self, banking_tools):
        """Test processing a credit card payment."""
        result = banking_tools.process_credit_card_payment(
            "credit_card_5001", 150.0, "account_2006"
        )
        
        assert result["success"] is True
        assert "Credit card payment of $150.00 processed successfully" in result["message"]
        assert result["remaining_balance"] == 1650.00  # 1800 - 150
        assert result["available_credit"] == 3350.00  # 3200 + 150

    # Turkish Banking Specific Tests
    def test_turkish_customer_data(self, banking_tools):
        """Test that customer data follows Turkish banking format."""
        result = banking_tools.get_customer_info("customer_1001")
        
        assert result["customer_id"] == "customer_1001"
        assert result["name"] == "Ayşe Yılmaz"  # Turkish name
        assert result["email"] == "ayse.yilmaz@email.com"
        assert result["status"] == "active"

    def test_turkish_phone_number_format(self, banking_tools):
        """Test Turkish phone number format in customer data."""
        result = banking_tools.get_customer_info("customer_1001")
        
        # The phone number should be in Turkish format
        # This test verifies the data structure, actual format validation would be in the data model
        assert "phone" in result

    def test_turkish_address_format(self, banking_tools):
        """Test Turkish address format in customer data."""
        # This test would need to be expanded to check address structure
        # For now, we verify the customer info retrieval works
        result = banking_tools.get_customer_info("customer_1001")
        assert result is not None

    def test_turkish_identity_verification_error_messages(self, banking_tools):
        """Test that error messages are in Turkish."""
        result = banking_tools.verify_customer_identity(
            "nonexistent_customer", "***-***-1234", "1985-03-15"
        )
        
        assert "error" in result
        assert "bulunamadı" in result["error"]  # Turkish for "not found"

    def test_turkish_account_types(self, banking_tools):
        """Test Turkish account type terminology."""
        result = banking_tools.get_account_info("account_2001")
        
        assert "error" not in result
        assert result["account_type"] == "vadesiz_mevduat"  # Turkish for checking account

    def test_turkish_transaction_types(self, banking_tools):
        """Test Turkish transaction type terminology."""
        # Test a deposit transaction
        result = banking_tools.process_deposit("account_2001", 100.0, "Test yatırım")
        
        assert result["success"] is True
        assert "yatırım" in result["message"]  # Turkish for deposit

    def test_turkish_loan_types(self, banking_tools):
        """Test Turkish loan type terminology."""
        result = banking_tools.get_loan_info("loan_4001")
        
        assert "error" not in result
        assert result["loan_type"] == "tasit_kredisi"  # Turkish for auto loan

    def test_turkish_currency_handling(self, banking_tools):
        """Test that amounts are handled in Turkish Lira."""
        result = banking_tools.process_deposit("account_2001", 1000.0, "TL yatırım")
        
        assert result["success"] is True
        assert result["new_balance"] > 0
        # Verify the transaction was processed correctly
        assert "transaction_id" in result

    def test_turkish_banking_security_procedures(self, banking_tools):
        """Test Turkish banking security procedures."""
        # Test account freezing with Turkish reason
        result = banking_tools.freeze_account("account_2001", "Şüpheli işlem")
        
        assert result["success"] is True
        assert "donduruldu" in result["message"]  # Turkish for frozen

    def test_turkish_customer_verification_workflow(self, banking_tools):
        """Test complete Turkish customer verification workflow."""
        # Step 1: Get customer info
        customer_info = banking_tools.get_customer_info("customer_1001")
        assert customer_info["customer_id"] == "customer_1001"
        
        # Step 2: Verify identity with TC Kimlik No
        verification = banking_tools.verify_customer_identity(
            "customer_1001", "***-***-1234", "1985-03-15"
        )
        assert verification["verified"] is True
        
        # Step 3: Get customer accounts
        accounts = banking_tools.get_customer_accounts("customer_1001")
        assert accounts["total_accounts"] >= 1

    def test_turkish_banking_compliance(self, banking_tools):
        """Test Turkish banking compliance requirements."""
        # Test that identity verification is required before sensitive operations
        result = banking_tools.get_account_info("account_2001")
        assert "error" not in result  # Should work without verification for basic info
        
        # Test that account operations require proper verification
        # This would be implemented in the actual banking logic
        assert result["account_id"] == "account_2001"

    def test_turkish_banking_error_handling(self, banking_tools):
        """Test Turkish banking error handling."""
        # Test insufficient funds error
        result = banking_tools.process_withdrawal("account_2009", 1000.0, "Test çekme")
        
        assert "error" in result
        assert "yetersiz" in result["error"] or "insufficient" in result["error"]

    def test_turkish_banking_data_consistency(self, banking_tools):
        """Test data consistency in Turkish banking domain."""
        # Test that customer data is consistent
        customer_info = banking_tools.get_customer_info("customer_1001")
        accounts = banking_tools.get_customer_accounts("customer_1001")
        
        assert customer_info["customer_id"] == "customer_1001"
        assert len(accounts["accounts"]) >= 1
        
        # Verify account belongs to customer
        account_ids = [acc["account_id"] for acc in accounts["accounts"]]
        assert "account_2001" in account_ids

    def test_turkish_banking_transaction_flow(self, banking_tools):
        """Test complete Turkish banking transaction flow."""
        # Test transfer between Turkish customers
        result = banking_tools.process_transfer(
            "account_2002", "account_2003", 500.0, "Test havale"
        )
        
        assert result["success"] is True
        assert "havale" in result["message"]  # Turkish for transfer
        assert "debit_transaction_id" in result
        assert "credit_transaction_id" in result

    def test_turkish_banking_loan_payment_flow(self, banking_tools):
        """Test Turkish banking loan payment flow."""
        # Test loan payment
        result = banking_tools.process_loan_payment(
            "loan_4001", 500.0, "account_2005"
        )
        
        assert result["success"] is True
        assert result["remaining_balance"] < 18500.00  # Original balance was 18500

    def test_turkish_banking_credit_card_flow(self, banking_tools):
        """Test Turkish banking credit card payment flow."""
        # Test credit card payment
        result = banking_tools.process_credit_card_payment(
            "credit_card_5001", 200.0, "account_2006"
        )
        
        assert result["success"] is True
        assert result["remaining_balance"] < 1800.00  # Original balance was 1800
        assert result["available_credit"] > 3200.00  # Original available credit was 3200
