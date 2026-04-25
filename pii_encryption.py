"""
PII Encryption Service
Encrypts/decrypts sensitive data (SSNs, member names, provider NPIs)
Uses Fernet (AES-128) for encryption
"""

from cryptography.fernet import Fernet
from typing import Optional
import os
import re


class PIIEncryption:
    """PII encryption service for sensitive data protection"""
    
    # In production, load from environment or secure key management service
    # For now, generate a test key
    _encryption_key = os.environ.get(
        'TORQ_E_ENCRYPTION_KEY',
        Fernet.generate_key()  # Generate if not set
    )
    
    _cipher = Fernet(_encryption_key)
    
    # PII patterns to detect
    SSN_PATTERN = re.compile(r'\d{3}-\d{2}-\d{4}')
    NPI_PATTERN = re.compile(r'\d{10}')
    MEMBER_NAME_PATTERN = re.compile(r'^[A-Z][a-z]+ [A-Z][a-z]+$')
    
    @classmethod
    def encrypt_ssn(cls, ssn: str) -> str:
        """Encrypt SSN, return encrypted value"""
        if not ssn or not cls.SSN_PATTERN.match(ssn):
            return ssn
        encrypted = cls._cipher.encrypt(ssn.encode())
        return encrypted.decode()  # Return as string
    
    @classmethod
    def decrypt_ssn(cls, encrypted_ssn: str) -> str:
        """Decrypt SSN (requires authorization)"""
        try:
            decrypted = cls._cipher.decrypt(encrypted_ssn.encode())
            return decrypted.decode()
        except Exception:
            return "[DECRYPTION FAILED]"
    
    @classmethod
    def encrypt_member_name(cls, name: str) -> str:
        """Encrypt member name"""
        if not name:
            return name
        encrypted = cls._cipher.encrypt(name.encode())
        return encrypted.decode()
    
    @classmethod
    def decrypt_member_name(cls, encrypted_name: str) -> str:
        """Decrypt member name (requires authorization)"""
        try:
            decrypted = cls._cipher.decrypt(encrypted_name.encode())
            return decrypted.decode()
        except Exception:
            return "[DECRYPTION FAILED]"
    
    @classmethod
    def encrypt_npi(cls, npi: str) -> str:
        """Encrypt provider NPI"""
        if not npi or not cls.NPI_PATTERN.match(npi):
            return npi
        encrypted = cls._cipher.encrypt(npi.encode())
        return encrypted.decode()
    
    @classmethod
    def decrypt_npi(cls, encrypted_npi: str) -> str:
        """Decrypt provider NPI (requires authorization)"""
        try:
            decrypted = cls._cipher.decrypt(encrypted_npi.encode())
            return decrypted.decode()
        except Exception:
            return "[DECRYPTION FAILED]"
    
    @classmethod
    def mask_ssn(cls, ssn: str) -> str:
        """Mask SSN for non-authorized display: XXX-XX-1234"""
        if not ssn or not cls.SSN_PATTERN.match(ssn):
            return ssn
        parts = ssn.split('-')
        return f"XXX-XX-{parts[2]}"
    
    @classmethod
    def mask_npi(cls, npi: str) -> str:
        """Mask NPI for non-authorized display: *****7890"""
        if not npi or not cls.NPI_PATTERN.match(npi):
            return npi
        return f"*****{npi[-4:]}"
    
    @classmethod
    def mask_name(cls, name: str) -> str:
        """Mask name for non-authorized display: J*** D***"""
        if not name or len(name) < 3:
            return name
        parts = name.split()
        masked = []
        for part in parts:
            masked.append(f"{part[0]}***")
        return " ".join(masked)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("PII ENCRYPTION TEST")
    print("="*80 + "\n")
    
    # Test SSN
    ssn = "123-45-6789"
    print(f"Original SSN: {ssn}")
    encrypted_ssn = PIIEncryption.encrypt_ssn(ssn)
    print(f"Encrypted: {encrypted_ssn[:50]}...")
    decrypted_ssn = PIIEncryption.decrypt_ssn(encrypted_ssn)
    print(f"Decrypted: {decrypted_ssn}")
    print(f"Masked: {PIIEncryption.mask_ssn(ssn)}")
    
    # Test Member Name
    print("\n")
    name = "Jane Doe"
    print(f"Original name: {name}")
    encrypted_name = PIIEncryption.encrypt_member_name(name)
    print(f"Encrypted: {encrypted_name[:50]}...")
    decrypted_name = PIIEncryption.decrypt_member_name(encrypted_name)
    print(f"Decrypted: {decrypted_name}")
    print(f"Masked: {PIIEncryption.mask_name(name)}")
    
    # Test NPI
    print("\n")
    npi = "1234567890"
    print(f"Original NPI: {npi}")
    encrypted_npi = PIIEncryption.encrypt_npi(npi)
    print(f"Encrypted: {encrypted_npi[:50]}...")
    decrypted_npi = PIIEncryption.decrypt_npi(encrypted_npi)
    print(f"Decrypted: {decrypted_npi}")
    print(f"Masked: {PIIEncryption.mask_npi(npi)}")
    
    print("\n" + "="*80 + "\n")
