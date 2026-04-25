"""
Role-Based Access Control (RBAC) for TORQ-e
Implements principle of least privilege for each user role
"""

from enum import Enum
from typing import Set, Optional


class UserRole(str, Enum):
    """User roles in the system"""
    MEMBER = "Member"
    PROVIDER = "Provider"
    PLAN_ADMIN = "PlanAdmin"
    GOVERNMENT_STAKEHOLDER = "GovernmentStakeholder"
    DATA_ANALYST = "DataAnalyst"


class DataDomain(str, Enum):
    """Data domains that require access control"""
    ENROLLMENT = "enrollment"
    CLAIMS = "claims"
    PROVIDER_DATA = "provider_data"
    GOVERNANCE = "governance"


class Permission(str, Enum):
    """Permissions that can be granted"""
    VIEW_AGGREGATE = "view:aggregate"  # View de-identified aggregate data only
    VIEW_INDIVIDUAL = "view:individual"  # View individual records with full PII
    VIEW_PII = "view:pii"  # View SSNs, member names, provider NPIs
    CREATE_INVESTIGATION = "create:investigation"
    REQUEST_CORRECTION = "request:correction"
    APPROVE_CORRECTION = "approve:correction"
    FLAG_ISSUE = "flag:issue"
    STRIKE_SOURCE = "strike:source"


class RBACProvider:
    """RBAC policy provider"""
    
    # Define permissions by role
    ROLE_PERMISSIONS = {
        UserRole.MEMBER: {
            DataDomain.ENROLLMENT: {Permission.VIEW_AGGREGATE},
            DataDomain.CLAIMS: {Permission.VIEW_AGGREGATE},
        },
        UserRole.PROVIDER: {
            DataDomain.ENROLLMENT: {Permission.VIEW_AGGREGATE},
            DataDomain.CLAIMS: {Permission.VIEW_AGGREGATE},
        },
        UserRole.PLAN_ADMIN: {
            DataDomain.ENROLLMENT: {Permission.VIEW_AGGREGATE},
            DataDomain.CLAIMS: {Permission.VIEW_AGGREGATE},
            DataDomain.PROVIDER_DATA: {Permission.VIEW_AGGREGATE},
        },
        UserRole.GOVERNMENT_STAKEHOLDER: {
            DataDomain.ENROLLMENT: {Permission.VIEW_AGGREGATE},
            DataDomain.CLAIMS: {Permission.VIEW_AGGREGATE},
            DataDomain.PROVIDER_DATA: {Permission.VIEW_AGGREGATE},
            DataDomain.GOVERNANCE: {Permission.VIEW_AGGREGATE, Permission.FLAG_ISSUE, Permission.STRIKE_SOURCE},
        },
        UserRole.DATA_ANALYST: {
            # Card 5 has FULL data access
            DataDomain.ENROLLMENT: {
                Permission.VIEW_INDIVIDUAL,
                Permission.VIEW_PII,
                Permission.CREATE_INVESTIGATION,
                Permission.REQUEST_CORRECTION,
            },
            DataDomain.CLAIMS: {
                Permission.VIEW_INDIVIDUAL,
                Permission.VIEW_PII,
                Permission.CREATE_INVESTIGATION,
                Permission.REQUEST_CORRECTION,
            },
            DataDomain.PROVIDER_DATA: {
                Permission.VIEW_INDIVIDUAL,
                Permission.VIEW_PII,
                Permission.CREATE_INVESTIGATION,
                Permission.REQUEST_CORRECTION,
            },
            DataDomain.GOVERNANCE: {
                Permission.FLAG_ISSUE,
                Permission.REQUEST_CORRECTION,
            },
        },
    }
    
    @staticmethod
    def has_permission(
        role: UserRole,
        domain: DataDomain,
        permission: Permission
    ) -> bool:
        """Check if role has permission for domain"""
        role_perms = RBACProvider.ROLE_PERMISSIONS.get(role, {})
        domain_perms = role_perms.get(domain, set())
        return permission in domain_perms
    
    @staticmethod
    def get_permissions(role: UserRole, domain: DataDomain) -> Set[Permission]:
        """Get all permissions for role in domain"""
        role_perms = RBACProvider.ROLE_PERMISSIONS.get(role, {})
        return role_perms.get(domain, set())
    
    @staticmethod
    def enforce_permission(
        role: UserRole,
        domain: DataDomain,
        permission: Permission,
        actor_id: str
    ) -> None:
        """Enforce permission check, raise exception if denied"""
        if not RBACProvider.has_permission(role, domain, permission):
            raise PermissionError(
                f"Access denied: {actor_id} ({role.value}) cannot {permission.value} in {domain.value}"
            )


# Integration helpers for use in tools
def check_data_analyst_can_query(actor_id: str, domain: DataDomain) -> bool:
    """Check if DataAnalyst can query domain"""
    try:
        RBACProvider.enforce_permission(
            UserRole.DATA_ANALYST,
            domain,
            Permission.VIEW_INDIVIDUAL,
            actor_id
        )
        return True
    except PermissionError:
        return False


def check_data_analyst_can_investigate(actor_id: str, domain: DataDomain) -> bool:
    """Check if DataAnalyst can create investigations"""
    try:
        RBACProvider.enforce_permission(
            UserRole.DATA_ANALYST,
            domain,
            Permission.CREATE_INVESTIGATION,
            actor_id
        )
        return True
    except PermissionError:
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RBAC CONFIGURATION TEST")
    print("="*80 + "\n")
    
    # Test DataAnalyst permissions
    print("DataAnalyst permissions:")
    for domain in [DataDomain.CLAIMS, DataDomain.ENROLLMENT, DataDomain.PROVIDER_DATA]:
        perms = RBACProvider.get_permissions(UserRole.DATA_ANALYST, domain)
        print(f"\n  {domain.value}:")
        for perm in sorted(perms):
            print(f"    ✅ {perm.value}")
    
    # Test permission enforcement
    print("\n\nPermission enforcement tests:")
    
    try:
        RBACProvider.enforce_permission(
            UserRole.DATA_ANALYST,
            DataDomain.CLAIMS,
            Permission.VIEW_PII,
            "carol_martinez"
        )
        print("✅ DataAnalyst can VIEW_PII in CLAIMS")
    except PermissionError as e:
        print(f"❌ {e}")
    
    try:
        RBACProvider.enforce_permission(
            UserRole.MEMBER,
            DataDomain.CLAIMS,
            Permission.VIEW_PII,
            "jane_doe"
        )
        print("✅ Member can VIEW_PII in CLAIMS")
    except PermissionError as e:
        print(f"✅ {e}")
    
    print("\n" + "="*80 + "\n")
