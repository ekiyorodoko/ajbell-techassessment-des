"""
Schema initialization module.
Imports all schema models and makes them available.
"""

from .base import SchemaRegistry, DocumentSection, register_schema
from .trust_registration import TrustRegistrationDetails
from .donor_details import DonorDetails
from .trustee_details import TrusteeDetails
from .beneficiary_details import BeneficiaryDetails
from .nominated_bank_account import NominatedBankAccount
from .security_information import SecurityInformation, SecurityQuestions
from .data_privacy_statement import DataPrivacyStatement, TrusteeSignature

__all__ = [
    'SchemaRegistry',
    'DocumentSection',
    'register_schema',
    'TrustRegistrationDetails',
    'DonorDetails',
    'TrusteeDetails',
    'BeneficiaryDetails',
    'NominatedBankAccount',
    'SecurityInformation',
    'SecurityQuestions',
    'DataPrivacyStatement',
    'TrusteeSignature',
]