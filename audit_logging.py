"""
HIPAA-Compliant Audit Logging Service
Immutable audit trail for all Card 4/5 operations
WHO/WHAT/WHEN/WHY with complete justification
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import hashlib

Base = declarative_base()


class AuditActionType(str, Enum):
    """HIPAA audit action types"""
    QUERY_CLAIMS = "QUERY_CLAIMS"
    DETECT_OUTLIERS = "DETECT_OUTLIERS"
    NAVIGATE_NETWORK = "NAVIGATE_NETWORK"
    CREATE_INVESTIGATION = "CREATE_INVESTIGATION"
    REQUEST_CORRECTION = "REQUEST_CORRECTION"
    APPROVE_CORRECTION = "APPROVE_CORRECTION"
    FLAG_ISSUE = "FLAG_ISSUE"
    STRIKE_SOURCE = "STRIKE_SOURCE"
    VIEW_GOVERNANCE_LOG = "VIEW_GOVERNANCE_LOG"


class AuditTrailEntry(Base):
    """Immutable audit trail record"""
    __tablename__ = "audit_trail"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(String(255), nullable=False, index=True)
    actor_role = Column(String(100), nullable=False)
    action_type = Column(String(100), nullable=False, index=True)
    card_number = Column(Integer, nullable=False, index=True)
    tool_name = Column(String(255), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    justification = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)
    domain = Column(String(100), nullable=False, index=True)
    affected_entity_type = Column(String(100), nullable=True)
    affected_entity_id = Column(String(255), nullable=True, index=True)
    parameters_hash = Column(String(64), nullable=True)
    parameters_summary = Column(Text, nullable=True)
    result_status = Column(String(50), nullable=False)
    confidence_score = Column(String(10), nullable=True)
    immutable = Column(String(5), default="true", nullable=False)


class HIPAAAuditLogger:
    """HIPAA-compliant audit logging service"""
    
    def __init__(self, db_url: str = "sqlite:///audit_trail.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def log_action(self, actor_id: str, actor_role: str, action_type: AuditActionType,
                   card_number: int, tool_name: str, domain: str, justification: str,
                   evidence: List[str], affected_entity_type: Optional[str] = None,
                   affected_entity_id: Optional[str] = None, parameters: Optional[Dict] = None,
                   result_status: str = "SUCCESS", confidence_score: Optional[float] = None):
        session = self.Session()
        try:
            params_hash = None
            params_summary = None
            if parameters:
                params_json = json.dumps(parameters, sort_keys=True, default=str)
                params_hash = hashlib.sha256(params_json.encode()).hexdigest()
                params_summary = "; ".join([f"{k}: <{len(str(v))} chars>" for k, v in parameters.items()])
            
            entry = AuditTrailEntry(
                actor_id=actor_id, actor_role=actor_role, action_type=action_type.value,
                card_number=card_number, tool_name=tool_name, domain=domain,
                justification=justification, evidence=json.dumps(evidence),
                affected_entity_type=affected_entity_type, affected_entity_id=affected_entity_id,
                parameters_hash=params_hash, parameters_summary=params_summary,
                result_status=result_status, confidence_score=str(confidence_score) if confidence_score else None,
                immutable="true"
            )
            
            session.add(entry)
            session.commit()
            print(f"✅ Audit logged: {actor_id} {action_type.value}")
            return entry
        except Exception as e:
            session.rollback()
            print(f"❌ Audit logging failed: {e}")
            raise
        finally:
            session.close()
