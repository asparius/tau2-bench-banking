import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from tau2.domains.banking.data_model import (
    Account,
    AccountStatus,
    AccountType,
    BankingDB,
    CreditCard,
    Customer,
    CustomerStatus,
    Loan,
    LoanStatus,
    LoanType,
    Transaction,
    TransactionStatus,
    TransactionType,
)
from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool


class IDGenerator:
    """Generates unique IDs for banking entities."""
    
    def __init__(self):
        self.id_counter = {
            "customer": 1000,
            "account": 2000,
            "transaction": 3000,
            "loan": 4000,
            "credit_card": 5000,
        }
    
    def generate_id(self, id_type: str) -> str:
        """Generate a unique ID for the given type."""
        self.id_counter[id_type] += 1
        return f"{id_type}_{self.id_counter[id_type]}"


class BankingTools(ToolKitBase):
    """Tools for banking operations."""

    def __init__(self, db: BankingDB):
        super().__init__()
        self.db = db
        self.id_generator = IDGenerator()

    # Customer Management Tools
    @is_tool(ToolType.READ)
    def find_customer_by_name(self, first_name: str, last_name: str) -> Dict[str, Any]:
        """Find customer ID by first and last name."""
        customers = [
            c for c in self.db.customers 
            if c.first_name.lower() == first_name.lower() and c.last_name.lower() == last_name.lower()
        ]
        
        if not customers:
            return {"error": f"Müşteri {first_name} {last_name} bulunamadı"}
        
        if len(customers) > 1:
            return {
                "error": "Birden fazla müşteri bulundu",
                "customers": [
                    {
                        "customer_id": c.customer_id,
                        "name": f"{c.first_name} {c.last_name}",
                        "email": c.email
                    }
                    for c in customers
                ]
            }
        
        customer = customers[0]
        return {
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "email": customer.email,
        }
    
    @is_tool(ToolType.READ)
    def find_customer_by_tc_no(self, tc_no: str) -> Dict[str, Any]:
        """Find customer ID by TC Kimlik No (Turkish ID number)."""
        customer = next((c for c in self.db.customers if c.tc_no == tc_no), None)
        
        if not customer:
            return {"error": f"TC Kimlik No {tc_no} ile müşteri bulunamadı"}
        
        return {
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "email": customer.email,
        }
    
    @is_tool(ToolType.READ)
    def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """Get customer information by customer ID."""
        customer = next((c for c in self.db.customers if c.customer_id == customer_id), None)
        if not customer:
            return {"error": f"Customer {customer_id} not found"}
        
        return {
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "email": customer.email,
            "phone": customer.phone_number,
            "status": customer.status.value,
            "kyc_verified": customer.kyc_verified,
            "risk_score": customer.risk_score,
            "created_date": customer.created_date.isoformat(),
        }

    @is_tool(ToolType.READ)
    def verify_customer_identity(self, customer_id: str, tc_no: str, date_of_birth: str) -> Dict[str, Any]:
        """Verify customer identity using TC Kimlik No and date of birth.
        
        Accepts date in multiple formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, etc.
        """
        from datetime import datetime
        
        customer = next((c for c in self.db.customers if c.customer_id == customer_id), None)
        if not customer:
            return {"error": f"Müşteri {customer_id} bulunamadı"}
        
        # Normalize date formats for comparison
        def normalize_date(date_str):
            """Convert various date formats to YYYY-MM-DD for comparison."""
            date_formats = [
                '%Y-%m-%d',      # 1985-03-15
                '%d/%m/%Y',      # 15/03/1985
                '%d-%m-%Y',      # 15-03-1985
                '%d.%m.%Y',      # 15.03.1985
                '%m/%d/%Y',      # 03/15/1985
            ]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return date_str  # Return as-is if no format matches
        
        customer_dob_normalized = normalize_date(customer.date_of_birth)
        provided_dob_normalized = normalize_date(date_of_birth)
        
        if customer.tc_no == tc_no and customer_dob_normalized == provided_dob_normalized:
            return {"verified": True, "customer_name": f"{customer.first_name} {customer.last_name}"}
        else:
            return {"verified": False, "error": "Kimlik doğrulama başarısız"}

    # Account Management Tools
    @is_tool(ToolType.READ)
    def get_account_info(self, account_id: str) -> Dict[str, Any]:
        """Get account information by account ID."""
        account = next((a for a in self.db.accounts if a.account_id == account_id), None)
        if not account:
            return {"error": f"Account {account_id} not found"}
        
        return {
            "account_id": account.account_id,
            "account_number": account.account_number,
            "account_type": account.account_type.value,
            "status": account.status.value,
            "balance": account.balance,
            "available_balance": account.available_balance,
            "interest_rate": account.interest_rate,
            "minimum_balance": account.minimum_balance,
            "monthly_fee": account.monthly_fee,
            "overdraft_limit": account.overdraft_limit,
            "created_date": account.created_date.isoformat(),
        }

    @is_tool(ToolType.READ)
    def get_customer_accounts(self, customer_id: str) -> Dict[str, Any]:
        """Get all accounts for a customer."""
        customer = next((c for c in self.db.customers if c.customer_id == customer_id), None)
        if not customer:
            return {"error": f"Customer {customer_id} not found"}
        
        accounts = [a for a in self.db.accounts if a.account_id in customer.account_ids]
        account_list = []
        for account in accounts:
            account_list.append({
                "account_id": account.account_id,
                "account_number": account.account_number,
                "account_type": account.account_type.value,
                "status": account.status.value,
                "balance": account.balance,
                "available_balance": account.available_balance,
            })
        
        return {"accounts": account_list, "total_accounts": len(account_list)}

    @is_tool(ToolType.WRITE)
    def freeze_account(self, account_id: str, reason: str) -> Dict[str, Any]:
        """Freeze an account with a specified reason."""
        account = next((a for a in self.db.accounts if a.account_id == account_id), None)
        if not account:
            return {"error": f"Account {account_id} not found"}
        
        if account.status == AccountStatus.FROZEN:
            return {"error": "Account is already frozen"}
        
        account.status = AccountStatus.FROZEN
        account.freeze_reason = reason
        account.freeze_date = datetime.date.today()
        
        return {"success": True, "message": f"Account {account_id} has been frozen. Reason: {reason}"}

    @is_tool(ToolType.WRITE)
    def unfreeze_account(self, account_id: str) -> Dict[str, Any]:
        """Unfreeze an account."""
        account = next((a for a in self.db.accounts if a.account_id == account_id), None)
        if not account:
            return {"error": f"Account {account_id} not found"}
        
        if account.status != AccountStatus.FROZEN:
            return {"error": "Account is not frozen"}
        
        account.status = AccountStatus.ACTIVE
        account.freeze_reason = None
        account.freeze_date = None
        
        return {"success": True, "message": f"Account {account_id} has been unfrozen"}

    # Transaction Tools
    @is_tool(ToolType.READ)
    def get_account_transactions(self, account_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get recent transactions for an account."""
        account = next((a for a in self.db.accounts if a.account_id == account_id), None)
        if not account:
            return {"error": f"Account {account_id} not found"}
        
        transactions = [t for t in self.db.transactions if t.account_id == account_id]
        transactions.sort(key=lambda x: x.transaction_date, reverse=True)
        
        transaction_list = []
        for transaction in transactions[:limit]:
            transaction_list.append({
                "transaction_id": transaction.transaction_id,
                "type": transaction.transaction_type.value,
                "amount": transaction.amount,
                "description": transaction.description,
                "status": transaction.status.value,
                "date": transaction.transaction_date.isoformat(),
                "balance_after": transaction.balance_after,
            })
        
        return {"transactions": transaction_list, "total_transactions": len(transactions)}

    @is_tool(ToolType.WRITE)
    def process_transfer(self, from_account_id: str, to_account_id: str, amount: float, description: str = "") -> Dict[str, Any]:
        """Process a transfer between accounts."""
        from_account = next((a for a in self.db.accounts if a.account_id == from_account_id), None)
        to_account = next((a for a in self.db.accounts if a.account_id == to_account_id), None)
        
        if not from_account:
            return {"error": f"Source account {from_account_id} not found"}
        if not to_account:
            return {"error": f"Destination account {to_account_id} not found"}
        
        if from_account.status != AccountStatus.ACTIVE:
            return {"error": f"Source account {from_account_id} is not active"}
        if to_account.status != AccountStatus.ACTIVE:
            return {"error": f"Destination account {to_account_id} is not active"}
        
        if amount <= 0:
            return {"error": "Transfer amount must be positive"}
        
        if from_account.available_balance < amount:
            return {"error": "Insufficient funds for transfer"}
        
        # Create transfer transactions
        now = datetime.datetime.now()
        
        # Debit transaction
        debit_transaction = Transaction(
            transaction_id=self.id_generator.generate_id("transaction"),
            account_id=from_account_id,
            transaction_type=TransactionType.TRANSFER_OUT,
            amount=-amount,
            description=f"Transfer to {to_account.account_number}: {description}",
            status=TransactionStatus.COMPLETED,
            transaction_date=now,
            posted_date=now,
            balance_after=from_account.balance - amount,
        )
        
        # Credit transaction
        credit_transaction = Transaction(
            transaction_id=self.id_generator.generate_id("transaction"),
            account_id=to_account_id,
            transaction_type=TransactionType.TRANSFER_IN,
            amount=amount,
            description=f"Transfer from {from_account.account_number}: {description}",
            status=TransactionStatus.COMPLETED,
            transaction_date=now,
            posted_date=now,
            balance_after=to_account.balance + amount,
        )
        
        # Link transactions
        debit_transaction.related_transaction_id = credit_transaction.transaction_id
        credit_transaction.related_transaction_id = debit_transaction.transaction_id
        
        # Update account balances
        from_account.balance -= amount
        from_account.available_balance -= amount
        to_account.balance += amount
        to_account.available_balance += amount
        
        # Add transactions to database
        self.db.transactions.append(debit_transaction)
        self.db.transactions.append(credit_transaction)
        
        return {
            "success": True,
            "message": f"Transfer of ${amount:.2f} completed successfully",
            "debit_transaction_id": debit_transaction.transaction_id,
            "credit_transaction_id": credit_transaction.transaction_id,
        }

    @is_tool(ToolType.WRITE)
    def process_deposit(self, account_id: str, amount: float, description: str = "") -> Dict[str, Any]:
        """Process a deposit to an account."""
        account = next((a for a in self.db.accounts if a.account_id == account_id), None)
        if not account:
            return {"error": f"Account {account_id} not found"}
        
        if account.status != AccountStatus.ACTIVE:
            return {"error": f"Account {account_id} is not active"}
        
        if amount <= 0:
            return {"error": "Deposit amount must be positive"}
        
        now = datetime.datetime.now()
        
        transaction = Transaction(
            transaction_id=self.id_generator.generate_id("transaction"),
            account_id=account_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            description=description or "Deposit",
            status=TransactionStatus.COMPLETED,
            transaction_date=now,
            posted_date=now,
            balance_after=account.balance + amount,
        )
        
        # Update account balance
        account.balance += amount
        account.available_balance += amount
        account.last_activity_date = datetime.date.today()
        
        # Add transaction to database
        self.db.transactions.append(transaction)
        
        return {
            "success": True,
            "message": f"Deposit of ${amount:.2f} completed successfully",
            "transaction_id": transaction.transaction_id,
            "new_balance": account.balance,
        }

    @is_tool(ToolType.WRITE)
    def process_withdrawal(self, account_id: str, amount: float, description: str = "") -> Dict[str, Any]:
        """Process a withdrawal from an account."""
        account = next((a for a in self.db.accounts if a.account_id == account_id), None)
        if not account:
            return {"error": f"Account {account_id} not found"}
        
        if account.status != AccountStatus.ACTIVE:
            return {"error": f"Account {account_id} is not active"}
        
        if amount <= 0:
            return {"error": "Withdrawal amount must be positive"}
        
        # Check available balance (including overdraft protection)
        available_with_overdraft = account.available_balance + account.overdraft_limit
        if available_with_overdraft < amount:
            return {"error": "Insufficient funds for withdrawal"}
        
        now = datetime.datetime.now()
        
        transaction = Transaction(
            transaction_id=self.id_generator.generate_id("transaction"),
            account_id=account_id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=-amount,
            description=description or "Withdrawal",
            status=TransactionStatus.COMPLETED,
            transaction_date=now,
            posted_date=now,
            balance_after=account.balance - amount,
        )
        
        # Update account balance
        account.balance -= amount
        account.available_balance -= amount
        account.last_activity_date = datetime.date.today()
        
        # Add transaction to database
        self.db.transactions.append(transaction)
        
        return {
            "success": True,
            "message": f"Withdrawal of ${amount:.2f} completed successfully",
            "transaction_id": transaction.transaction_id,
            "new_balance": account.balance,
        }

    # Loan Management Tools
    @is_tool(ToolType.READ)
    def get_loan_info(self, loan_id: str) -> Dict[str, Any]:
        """Get loan information by loan ID."""
        loan = next((l for l in self.db.loans if l.loan_id == loan_id), None)
        if not loan:
            return {"error": f"Loan {loan_id} not found"}
        
        return {
            "loan_id": loan.loan_id,
            "loan_number": loan.loan_number,
            "loan_type": loan.loan_type.value,
            "status": loan.status.value,
            "principal_amount": loan.principal_amount,
            "current_balance": loan.current_balance,
            "interest_rate": loan.interest_rate,
            "monthly_payment": loan.monthly_payment,
            "term_months": loan.term_months,
            "start_date": loan.start_date.isoformat(),
            "maturity_date": loan.maturity_date.isoformat(),
            "next_payment_date": loan.next_payment_date.isoformat() if loan.next_payment_date else None,
            "days_past_due": loan.days_past_due,
        }

    @is_tool(ToolType.READ)
    def get_customer_loans(self, customer_id: str) -> Dict[str, Any]:
        """Get all loans for a customer."""
        customer = next((c for c in self.db.customers if c.customer_id == customer_id), None)
        if not customer:
            return {"error": f"Customer {customer_id} not found"}
        
        loans = [l for l in self.db.loans if l.loan_id in customer.loan_ids]
        loan_list = []
        for loan in loans:
            loan_list.append({
                "loan_id": loan.loan_id,
                "loan_number": loan.loan_number,
                "loan_type": loan.loan_type.value,
                "status": loan.status.value,
                "current_balance": loan.current_balance,
                "monthly_payment": loan.monthly_payment,
                "next_payment_date": loan.next_payment_date.isoformat() if loan.next_payment_date else None,
                "days_past_due": loan.days_past_due,
            })
        
        return {"loans": loan_list, "total_loans": len(loan_list)}

    @is_tool(ToolType.WRITE)
    def process_loan_payment(self, loan_id: str, payment_amount: float, payment_account_id: str) -> Dict[str, Any]:
        """Process a loan payment."""
        loan = next((l for l in self.db.loans if l.loan_id == loan_id), None)
        if not loan:
            return {"error": f"Loan {loan_id} not found"}
        
        account = next((a for a in self.db.accounts if a.account_id == payment_account_id), None)
        if not account:
            return {"error": f"Payment account {payment_account_id} not found"}
        
        if loan.status != LoanStatus.ACTIVE:
            return {"error": f"Loan {loan_id} is not active"}
        
        if account.status != AccountStatus.ACTIVE:
            return {"error": f"Payment account {payment_account_id} is not active"}
        
        if payment_amount <= 0:
            return {"error": "Payment amount must be positive"}
        
        if account.available_balance < payment_amount:
            return {"error": "Insufficient funds for loan payment"}
        
        now = datetime.datetime.now()
        
        # Create payment transaction
        payment_transaction = Transaction(
            transaction_id=self.id_generator.generate_id("transaction"),
            account_id=payment_account_id,
            transaction_type=TransactionType.PAYMENT,
            amount=-payment_amount,
            description=f"Loan payment for {loan.loan_number}",
            status=TransactionStatus.COMPLETED,
            transaction_date=now,
            posted_date=now,
            balance_after=account.balance - payment_amount,
        )
        
        # Update account balance
        account.balance -= payment_amount
        account.available_balance -= payment_amount
        
        # Update loan balance
        loan.current_balance -= payment_amount
        loan.last_payment_date = datetime.date.today()
        
        # Check if loan is paid off
        if loan.current_balance <= 0:
            loan.status = LoanStatus.PAID_OFF
            loan.current_balance = 0
        
        # Add transaction to database
        self.db.transactions.append(payment_transaction)
        
        return {
            "success": True,
            "message": f"Loan payment of ${payment_amount:.2f} processed successfully",
            "transaction_id": payment_transaction.transaction_id,
            "remaining_balance": loan.current_balance,
        }

    # Credit Card Tools
    @is_tool(ToolType.READ)
    def get_credit_card_info(self, card_id: str) -> Dict[str, Any]:
        """Get credit card information by card ID."""
        card = next((c for c in self.db.credit_cards if c.card_id == card_id), None)
        if not card:
            return {"error": f"Credit card {card_id} not found"}
        
        return {
            "card_id": card.card_id,
            "card_number": card.card_number,
            "status": card.status.value,
            "credit_limit": card.credit_limit,
            "available_credit": card.available_credit,
            "current_balance": card.current_balance,
            "minimum_payment": card.minimum_payment,
            "interest_rate": card.interest_rate,
            "payment_due_date": card.payment_due_date.isoformat() if card.payment_due_date else None,
            "days_past_due": card.days_past_due,
        }

    @is_tool(ToolType.READ)
    def get_customer_credit_cards(self, customer_id: str) -> Dict[str, Any]:
        """Get all credit cards for a customer."""
        customer = next((c for c in self.db.customers if c.customer_id == customer_id), None)
        if not customer:
            return {"error": f"Customer {customer_id} not found"}
        
        cards = [c for c in self.db.credit_cards if c.card_id in customer.credit_card_ids]
        card_list = []
        for card in cards:
            card_list.append({
                "card_id": card.card_id,
                "card_number": card.card_number,
                "status": card.status.value,
                "credit_limit": card.credit_limit,
                "available_credit": card.available_credit,
                "current_balance": card.current_balance,
                "minimum_payment": card.minimum_payment,
                "payment_due_date": card.payment_due_date.isoformat() if card.payment_due_date else None,
            })
        
        return {"credit_cards": card_list, "total_cards": len(card_list)}

    @is_tool(ToolType.WRITE)
    def process_credit_card_payment(self, card_id: str, payment_amount: float, payment_account_id: str) -> Dict[str, Any]:
        """Process a credit card payment."""
        card = next((c for c in self.db.credit_cards if c.card_id == card_id), None)
        if not card:
            return {"error": f"Credit card {card_id} not found"}
        
        account = next((a for a in self.db.accounts if a.account_id == payment_account_id), None)
        if not account:
            return {"error": f"Payment account {payment_account_id} not found"}
        
        if card.status != AccountStatus.ACTIVE:
            return {"error": f"Credit card {card_id} is not active"}
        
        if account.status != AccountStatus.ACTIVE:
            return {"error": f"Payment account {payment_account_id} is not active"}
        
        if payment_amount <= 0:
            return {"error": "Payment amount must be positive"}
        
        if payment_amount > card.current_balance:
            return {"error": "Payment amount cannot exceed current balance"}
        
        if account.available_balance < payment_amount:
            return {"error": "Insufficient funds for credit card payment"}
        
        now = datetime.datetime.now()
        
        # Create payment transaction
        payment_transaction = Transaction(
            transaction_id=self.id_generator.generate_id("transaction"),
            account_id=payment_account_id,
            transaction_type=TransactionType.PAYMENT,
            amount=-payment_amount,
            description=f"Credit card payment for {card.card_number}",
            status=TransactionStatus.COMPLETED,
            transaction_date=now,
            posted_date=now,
            balance_after=account.balance - payment_amount,
        )
        
        # Update account balance
        account.balance -= payment_amount
        account.available_balance -= payment_amount
        
        # Update credit card balance
        card.current_balance -= payment_amount
        card.available_credit += payment_amount
        card.last_payment_date = datetime.date.today()
        
        # Add transaction to database
        self.db.transactions.append(payment_transaction)
        
        return {
            "success": True,
            "message": f"Credit card payment of ${payment_amount:.2f} processed successfully",
            "transaction_id": payment_transaction.transaction_id,
            "remaining_balance": card.current_balance,
            "available_credit": card.available_credit,
        }
