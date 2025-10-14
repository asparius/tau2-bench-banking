import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from tau2.domains.banking.utils import BANKING_DB_PATH
from tau2.environment.db import DB
from tau2.utils.pydantic_utils import BaseModelNoExtra

DEFAULT_START_DATE = datetime.date(2025, 1, 1)


class Address(BaseModelNoExtra):
    street: str = Field(description="Street address including house/apartment number")
    district: str = Field(description="District (ilçe) name")
    city: str = Field(description="City (il) name")
    postal_code: str = Field(description="Postal code (5 digits)")
    country: str = Field(default="Turkey", description="Country name")


class AccountType(str, Enum):
    CHECKING = "vadesiz_mevduat"  # Vadesiz mevduat hesabı
    SAVINGS = "vadeli_mevduat"    # Vadeli mevduat hesabı
    GOLD_ACCOUNT = "altin_hesabi"  # Altın hesabı
    FOREIGN_CURRENCY = "doviz_hesabi"  # Döviz hesabı
    BUSINESS_CHECKING = "ticari_mevduat"  # Ticari mevduat hesabı
    STUDENT_ACCOUNT = "ogrenci_hesabi"  # Öğrenci hesabı
    SENIOR_ACCOUNT = "emekli_hesabi"  # Emekli hesabı
    INVESTMENT = "yatirim_hesabi"  # Yatırım hesabı


class AccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"
    CLOSED = "closed"
    PENDING_APPROVAL = "pending_approval"


class TransactionType(str, Enum):
    DEPOSIT = "yatirim"  # Yatırım
    WITHDRAWAL = "cekme"  # Çekme
    TRANSFER_IN = "havale_gelen"  # Havale gelen
    TRANSFER_OUT = "havale_giden"  # Havale giden
    PAYMENT = "odeme"  # Ödeme
    FEE = "komisyon"  # Komisyon
    INTEREST = "faiz"  # Faiz
    REFUND = "iade"  # İade
    EFT = "eft"  # EFT (Electronic Fund Transfer)
    SWIFT = "swift"  # SWIFT transfer
    GOLD_PURCHASE = "altin_alim"  # Altın alım
    GOLD_SALE = "altin_satim"  # Altın satım
    FOREIGN_EXCHANGE = "doviz_cevirim"  # Döviz çevirim
    CREDIT_CARD_PAYMENT = "kredi_karti_odeme"  # Kredi kartı ödeme
    LOAN_PAYMENT = "kredi_odeme"  # Kredi ödeme


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"


class LoanType(str, Enum):
    PERSONAL = "ihtiyac_kredisi"  # İhtiyaç kredisi
    AUTO = "tasit_kredisi"  # Taşıt kredisi
    MORTGAGE = "konut_kredisi"  # Konut kredisi
    HOME_EQUITY = "ipotekli_kredi"  # İpotekli kredi
    STUDENT = "ogrenci_kredisi"  # Öğrenci kredisi
    BUSINESS = "ticari_kredi"  # Ticari kredi
    CREDIT_LINE = "kredi_limiti"  # Kredi limiti
    GOLD_LOAN = "altin_kredisi"  # Altın kredisi
    AGRICULTURAL = "tarim_kredisi"  # Tarım kredisi


class LoanStatus(str, Enum):
    ACTIVE = "active"
    PAID_OFF = "paid_off"
    DEFAULTED = "defaulted"
    IN_FORECLOSURE = "in_foreclosure"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class CustomerStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    PENDING_VERIFICATION = "pending_verification"


class Account(BaseModelNoExtra):
    account_id: str = Field(description="Unique identifier for the account")
    customer_id: str = Field(description="Customer who owns this account")
    account_type: AccountType = Field(description="Type of account")
    account_number: str = Field(description="Account number (masked for security)")
    routing_number: str = Field(description="Bank routing number")
    status: AccountStatus = Field(AccountStatus.ACTIVE, description="Current status of the account")
    balance: float = Field(0.0, description="Current account balance in USD")
    available_balance: float = Field(0.0, description="Available balance (balance minus holds) in USD")
    interest_rate: float = Field(0.0, description="Annual interest rate as a percentage")
    minimum_balance: float = Field(0.0, description="Minimum balance required to avoid fees")
    monthly_fee: float = Field(0.0, description="Monthly maintenance fee in USD")
    overdraft_limit: float = Field(0.0, description="Overdraft protection limit in USD")
    created_date: datetime.date = Field(
        DEFAULT_START_DATE,
        description="Date when the account was created (format: YYYY-MM-DD)"
    )
    last_activity_date: Optional[datetime.date] = Field(
        None,
        description="Date of last account activity (format: YYYY-MM-DD)"
    )
    freeze_reason: Optional[str] = Field(
        None,
        description="Reason for account freeze, if applicable"
    )
    freeze_date: Optional[datetime.date] = Field(
        None,
        description="Date when account was frozen (format: YYYY-MM-DD)"
    )


class Transaction(BaseModelNoExtra):
    transaction_id: str = Field(description="Unique identifier for the transaction")
    account_id: str = Field(description="Account involved in the transaction")
    transaction_type: TransactionType = Field(description="Type of transaction")
    amount: float = Field(description="Transaction amount in USD (positive for credits, negative for debits)")
    description: str = Field(description="Description of the transaction")
    status: TransactionStatus = Field(TransactionStatus.COMPLETED, description="Current status of the transaction")
    transaction_date: datetime.datetime = Field(
        description="Date and time when the transaction occurred (format: YYYY-MM-DDTHH:MM:SS, timezone: EST)"
    )
    posted_date: Optional[datetime.datetime] = Field(
        None,
        description="Date and time when the transaction was posted (format: YYYY-MM-DDTHH:MM:SS, timezone: EST)"
    )
    reference_number: Optional[str] = Field(
        None,
        description="External reference number for the transaction"
    )
    related_transaction_id: Optional[str] = Field(
        None,
        description="ID of related transaction (e.g., for transfers)"
    )
    fee_amount: float = Field(0.0, description="Fee amount associated with this transaction")
    balance_after: float = Field(description="Account balance after this transaction")


class Loan(BaseModelNoExtra):
    loan_id: str = Field(description="Unique identifier for the loan")
    customer_id: str = Field(description="Customer who has this loan")
    loan_type: LoanType = Field(description="Type of loan")
    loan_number: str = Field(description="Loan account number")
    status: LoanStatus = Field(description="Current status of the loan")
    principal_amount: float = Field(description="Original loan amount in USD")
    current_balance: float = Field(description="Current outstanding balance in USD")
    interest_rate: float = Field(description="Annual interest rate as a percentage")
    monthly_payment: float = Field(description="Monthly payment amount in USD")
    term_months: int = Field(description="Loan term in months")
    start_date: datetime.date = Field(
        description="Date when the loan was originated (format: YYYY-MM-DD)"
    )
    maturity_date: datetime.date = Field(
        description="Date when the loan matures (format: YYYY-MM-DD)"
    )
    next_payment_date: Optional[datetime.date] = Field(
        None,
        description="Next payment due date (format: YYYY-MM-DD)"
    )
    last_payment_date: Optional[datetime.date] = Field(
        None,
        description="Date of last payment received (format: YYYY-MM-DD)"
    )
    days_past_due: int = Field(0, description="Number of days the loan is past due")
    collateral_description: Optional[str] = Field(
        None,
        description="Description of collateral, if applicable"
    )


class CreditCard(BaseModelNoExtra):
    card_id: str = Field(description="Unique identifier for the credit card")
    customer_id: str = Field(description="Customer who owns this card")
    card_number: str = Field(description="Masked credit card number")
    status: AccountStatus = Field(AccountStatus.ACTIVE, description="Current status of the card")
    credit_limit: float = Field(description="Credit limit in USD")
    available_credit: float = Field(description="Available credit in USD")
    current_balance: float = Field(0.0, description="Current balance in USD")
    minimum_payment: float = Field(0.0, description="Minimum payment due in USD")
    interest_rate: float = Field(description="Annual interest rate as a percentage")
    payment_due_date: Optional[datetime.date] = Field(
        None,
        description="Next payment due date (format: YYYY-MM-DD)"
    )
    last_payment_date: Optional[datetime.date] = Field(
        None,
        description="Date of last payment received (format: YYYY-MM-DD)"
    )
    days_past_due: int = Field(0, description="Number of days past due")
    created_date: datetime.date = Field(
        DEFAULT_START_DATE,
        description="Date when the card was issued (format: YYYY-MM-DD)"
    )


class Customer(BaseModelNoExtra):
    customer_id: str = Field(description="Unique identifier for the customer")
    first_name: str = Field(description="Customer's first name (ad)")
    last_name: str = Field(description="Customer's last name (soyad)")
    date_of_birth: str = Field(
        description="Customer's date of birth for identity verification (format: YYYY-MM-DD)"
    )
    tc_no: str = Field(description="Turkish Republic Identity Number (TC Kimlik No) - masked for security")
    email: str = Field(description="Customer's email address")
    phone_number: str = Field(description="Customer's primary contact phone number (Turkish format)")
    address: Address = Field(description="Customer's primary address")
    status: CustomerStatus = Field(
        CustomerStatus.ACTIVE,
        description="Current status of the customer account"
    )
    account_ids: List[str] = Field(
        default_factory=list,
        description="Bank accounts owned by this customer"
    )
    loan_ids: List[str] = Field(
        default_factory=list,
        description="Loans associated with this customer"
    )
    credit_card_ids: List[str] = Field(
        default_factory=list,
        description="Credit cards owned by this customer"
    )
    created_date: datetime.date = Field(
        DEFAULT_START_DATE,
        description="Date when the customer account was created (format: YYYY-MM-DD)"
    )
    last_login_date: Optional[datetime.date] = Field(
        None,
        description="Date of last login (format: YYYY-MM-DD)"
    )
    kyc_verified: bool = Field(
        False,
        description="Whether customer has completed Know Your Customer verification"
    )
    risk_score: int = Field(
        500,
        description="Customer risk score (300-850, higher is better)"
    )
    occupation: Optional[str] = Field(
        None,
        description="Customer's occupation (meslek)"
    )
    monthly_income: Optional[float] = Field(
        None,
        description="Customer's monthly income in Turkish Lira (TL)"
    )
    preferred_language: str = Field(
        default="tr",
        description="Customer's preferred language (tr/en)"
    )


class BankingDB(DB):
    """Database interface for banking domain."""

    customers: List[Customer] = Field(
        default_factory=list,
        description="All customers in the system"
    )
    accounts: List[Account] = Field(
        default_factory=list,
        description="All bank accounts in the system"
    )
    transactions: List[Transaction] = Field(
        default_factory=list,
        description="All transactions in the system"
    )
    loans: List[Loan] = Field(
        default_factory=list,
        description="All loans in the system"
    )
    credit_cards: List[CreditCard] = Field(
        default_factory=list,
        description="All credit cards in the system"
    )

    def get_statistics(self) -> Dict[str, Any]:
        """Get the statistics of the database."""
        num_customers = len(self.customers)
        num_accounts = len(self.accounts)
        num_transactions = len(self.transactions)
        num_loans = len(self.loans)
        num_credit_cards = len(self.credit_cards)
        
        total_deposits = sum(
            account.balance for account in self.accounts
            if account.account_type in [AccountType.vadesiz_mevduat, AccountType.vadeli_mevduat, AccountType.doviz_hesabi]
        )
        
        total_loan_balance = sum(loan.current_balance for loan in self.loans)
        total_credit_card_balance = sum(card.current_balance for card in self.credit_cards)

        return {
            "num_customers": num_customers,
            "num_accounts": num_accounts,
            "num_transactions": num_transactions,
            "num_loans": num_loans,
            "num_credit_cards": num_credit_cards,
            "total_deposits": total_deposits,
            "total_loan_balance": total_loan_balance,
            "total_credit_card_balance": total_credit_card_balance,
        }


def get_db():
    """Get an instance of the banking database."""
    return BankingDB.load(BANKING_DB_PATH)
