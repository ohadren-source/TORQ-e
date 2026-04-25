/**
 * TORQ-E Card 3: Programs/Plans Marketplace
 * PostgreSQL Database Schema
 *
 * Tables:
 * 1. programs - Available Medicaid programs/plans
 * 2. beneficiary_selections - Member enrollment records (immutable)
 * 3. program_views_audit - Member activity audit trail (immutable, append-only)
 */

-- ============================================================================
-- TABLE: programs
-- Stores all available programs/plans in the state
-- Updated daily from state data source
-- ============================================================================

CREATE TABLE IF NOT EXISTS programs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Basic info
  name VARCHAR(255) NOT NULL,
  type ENUM ('MEDICAID', 'MANAGED_CARE', 'SPECIAL_NEEDS', 'DUAL_ELIGIBLE'),
  state VARCHAR(2) NOT NULL,

  -- Eligibility criteria (JSONB for flexibility)
  eligibility_criteria JSONB NOT NULL,
  -- Structure:
  -- {
  --   "age_min": 0,
  --   "age_max": 120,
  --   "income_limit": 250000,
  --   "citizenship_required": true,
  --   "disability_status_required": false,
  --   "special_conditions": []
  -- }

  -- Benefits (JSONB)
  benefits JSONB NOT NULL,
  -- Structure:
  -- {
  --   "primary_care": true,
  --   "specialist_visits": true,
  --   "emergency": true,
  --   "hospitalization": true,
  --   "pharmacy": true,
  --   "mental_health": true,
  --   "dental": true,
  --   "vision": true,
  --   "long_term_care": false,
  --   "custom_benefits": []
  -- }

  -- Cost sharing (JSONB)
  cost_sharing JSONB NOT NULL,
  -- Structure:
  -- {
  --   "member_premium_monthly": 0,
  --   "copay_primary": 0,
  --   "copay_specialist": 25,
  --   "copay_emergency": 0,
  --   "deductible": 0
  -- }

  -- Network info
  network_type ENUM ('HMO', 'PPO', 'FFS', 'CAPITATED'),
  provider_directory_url VARCHAR(500),

  -- Coverage dates
  coverage_start_date DATE NOT NULL,
  coverage_end_date DATE,  -- NULL = ongoing

  -- Status
  status ENUM ('ACTIVE', 'PENDING', 'CLOSED', 'ARCHIVED') NOT NULL DEFAULT 'ACTIVE',

  -- Contact info (JSONB)
  contact_info JSONB,
  -- Structure:
  -- {
  --   "phone": "1-800-XXX-XXXX",
  --   "website": "https://...",
  --   "support_hours": "Mon-Fri 8AM-6PM ET"
  -- }

  -- Enrollment deadline
  enrollment_deadline DATE,

  -- Audit trail
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  last_modified_by VARCHAR(255),
  change_log JSONB,  -- Array of changes

  -- Indexes for fast querying
  INDEX idx_state (state),
  INDEX idx_type (type),
  INDEX idx_status (status),
  INDEX idx_coverage_start (coverage_start_date)
);

-- ============================================================================
-- TABLE: beneficiary_selections
-- Member enrollment records
-- IMMUTABLE: Once inserted, records are never modified or deleted
-- This creates audit trail of who chose what, when
-- ============================================================================

CREATE TABLE IF NOT EXISTS beneficiary_selections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Member (hashed, never plaintext)
  beneficiary_id UUID NOT NULL,  -- Hashed in application layer

  -- Program choice
  program_id UUID NOT NULL REFERENCES programs(id),

  -- When they selected it
  selected_at TIMESTAMP NOT NULL DEFAULT NOW(),

  -- When coverage becomes effective
  selection_effective_date DATE NOT NULL,

  -- Enrollment status
  enrollment_status ENUM ('PENDING', 'CONFIRMED', 'ACTIVE', 'TERMINATED') NOT NULL DEFAULT 'PENDING',

  -- If terminated, why
  termination_reason VARCHAR(255),

  -- Immutable audit trail (JSONB array)
  audit_trail JSONB NOT NULL,
  -- Structure:
  -- [
  --   {
  --     "timestamp": "2026-04-25T10:20:00Z",
  --     "action": "CREATED",
  --     "status": "PENDING"
  --   },
  --   {
  --     "timestamp": "2026-04-26T09:15:00Z",
  --     "action": "CONFIRMED",
  --     "status": "CONFIRMED"
  --   }
  -- ]

  -- Timestamps
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

  -- Immutability: This table is INSERT ONLY
  -- Application layer enforces: no UPDATE, no DELETE
  -- To change enrollment, INSERT a new record (don't modify old)

  -- Indexes
  INDEX idx_beneficiary_id (beneficiary_id),
  INDEX idx_program_id (program_id),
  INDEX idx_enrollment_status (enrollment_status),
  INDEX idx_selected_at (selected_at)
);

-- ============================================================================
-- TABLE: program_views_audit
-- IMMUTABLE APPEND-ONLY LOG
-- Tracks every view, comparison, and interaction in Card 3
-- Used for fraud detection, user behavior analysis, audit compliance
--
-- Immutability enforcement:
-- - Application never reads from this table (no SELECT)
-- - Application only writes to this table (INSERT only)
-- - Database trigger prevents any UPDATE or DELETE
-- - This becomes the source of truth for activity history
-- ============================================================================

CREATE TABLE IF NOT EXISTS program_views_audit (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Who (hashed)
  beneficiary_id UUID NOT NULL,  -- Hashed

  -- What action
  action ENUM ('BROWSE', 'COMPARE', 'DETAIL_VIEW', 'ENROLL', 'SEARCH', 'FILTER') NOT NULL,

  -- Which program(s)
  program_id UUID,
  program_ids JSONB,  -- Array for COMPARE action

  -- When
  viewed_at TIMESTAMP NOT NULL DEFAULT NOW(),

  -- Context
  device_type ENUM ('DESKTOP', 'MOBILE', 'TABLET') NOT NULL DEFAULT 'DESKTOP',
  session_id VARCHAR(255),
  hashed_ip_address VARCHAR(255),

  -- How long did they stay
  duration_ms INTEGER,

  -- Search/filter context
  search_query VARCHAR(255),
  filters_applied JSONB,  -- {state: "NY", type: "MANAGED_CARE"}

  -- Immutability constraint: This is WRITE-ONCE
  -- No updates, no deletes, ever

  -- Index for fraud queries
  INDEX idx_beneficiary_id (beneficiary_id),
  INDEX idx_action (action),
  INDEX idx_viewed_at (viewed_at),
  INDEX idx_program_id (program_id)
);

-- ============================================================================
-- TRIGGERS: Enforce immutability of audit tables
-- ============================================================================

-- Trigger: Prevent updates to beneficiary_selections
CREATE TRIGGER IF NOT EXISTS beneficiary_selections_no_update
BEFORE UPDATE ON beneficiary_selections
FOR EACH ROW
EXECUTE FUNCTION raise_immutability_error('beneficiary_selections');

-- Trigger: Prevent deletes from beneficiary_selections
CREATE TRIGGER IF NOT EXISTS beneficiary_selections_no_delete
BEFORE DELETE ON beneficiary_selections
FOR EACH ROW
EXECUTE FUNCTION raise_immutability_error('beneficiary_selections');

-- Trigger: Prevent updates to program_views_audit
CREATE TRIGGER IF NOT EXISTS program_views_audit_no_update
BEFORE UPDATE ON program_views_audit
FOR EACH ROW
EXECUTE FUNCTION raise_immutability_error('program_views_audit');

-- Trigger: Prevent deletes from program_views_audit
CREATE TRIGGER IF NOT EXISTS program_views_audit_no_delete
BEFORE DELETE ON program_views_audit
FOR EACH ROW
EXECUTE FUNCTION raise_immutability_error('program_views_audit');

-- Function: Raise immutability error
CREATE OR REPLACE FUNCTION raise_immutability_error(table_name TEXT)
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Table % is immutable. No modifications allowed.', table_name;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INDEXES: Performance optimization
-- ============================================================================

-- Program lookup by state (most common query)
CREATE INDEX IF NOT EXISTS idx_programs_state_status ON programs(state, status);

-- Program lookup by type
CREATE INDEX IF NOT EXISTS idx_programs_type ON programs(type);

-- Beneficiary selection history (recent selections for member dashboard)
CREATE INDEX IF NOT EXISTS idx_selections_beneficiary_recent ON beneficiary_selections(beneficiary_id, selected_at DESC);

-- Audit trail queries by date range (for compliance reports)
CREATE INDEX IF NOT EXISTS idx_audit_viewed_at_range ON program_views_audit(viewed_at DESC);

-- Fraud detection: Find all views/selections by member
CREATE INDEX IF NOT EXISTS idx_audit_beneficiary_action ON program_views_audit(beneficiary_id, action, viewed_at DESC);

-- ============================================================================
-- SAMPLE DATA: For testing and development
-- ============================================================================

-- Insert sample programs (NY Medicaid example)
INSERT INTO programs (name, type, state, eligibility_criteria, benefits, cost_sharing, network_type, coverage_start_date, status)
VALUES
  (
    'NY Medicaid - Managed Care Plan A',
    'MANAGED_CARE',
    'NY',
    '{"age_min": 0, "age_max": 120, "income_limit": 250000, "citizenship_required": true, "disability_status_required": false}'::jsonb,
    '{"primary_care": true, "specialist_visits": true, "emergency": true, "hospitalization": true, "pharmacy": true, "mental_health": true, "dental": true, "vision": true, "long_term_care": false}'::jsonb,
    '{"member_premium_monthly": 0, "copay_primary": 0, "copay_specialist": 25, "copay_emergency": 0, "deductible": 0}'::jsonb,
    'HMO',
    '2026-01-01',
    'ACTIVE'
  ),
  (
    'NY Medicaid - PPO Plan B',
    'MANAGED_CARE',
    'NY',
    '{"age_min": 0, "age_max": 120, "income_limit": 250000, "citizenship_required": true, "disability_status_required": false}'::jsonb,
    '{"primary_care": true, "specialist_visits": true, "emergency": true, "hospitalization": true, "pharmacy": true, "mental_health": true, "dental": false, "vision": false, "long_term_care": false}'::jsonb,
    '{"member_premium_monthly": 15, "copay_primary": 10, "copay_specialist": 50, "copay_emergency": 250, "deductible": 500}'::jsonb,
    'PPO',
    '2026-01-01',
    'ACTIVE'
  ),
  (
    'NY Medicaid - Special Needs Plan C',
    'SPECIAL_NEEDS',
    'NY',
    '{"age_min": 0, "age_max": 120, "income_limit": 250000, "citizenship_required": true, "disability_status_required": true}'::jsonb,
    '{"primary_care": true, "specialist_visits": true, "emergency": true, "hospitalization": true, "pharmacy": true, "mental_health": true, "dental": true, "vision": true, "long_term_care": true}'::jsonb,
    '{"member_premium_monthly": 0, "copay_primary": 0, "copay_specialist": 0, "copay_emergency": 0, "deductible": 0}'::jsonb,
    'HMO',
    '2026-01-01',
    'ACTIVE'
  );

-- ============================================================================
-- VIEWS: For reporting and analysis (Card 4, Card 5)
-- ============================================================================

-- View: Daily enrollment summary (for Card 4)
CREATE OR REPLACE VIEW daily_enrollment_summary AS
SELECT
  DATE(selected_at) as enrollment_date,
  program_id,
  COUNT(*) as enrollment_count,
  COUNT(CASE WHEN enrollment_status = 'ACTIVE' THEN 1 END) as active_enrollments,
  COUNT(CASE WHEN enrollment_status = 'TERMINATED' THEN 1 END) as terminated_enrollments
FROM beneficiary_selections
GROUP BY DATE(selected_at), program_id
ORDER BY enrollment_date DESC, program_id;

-- View: Member activity summary (for Card 5 fraud detection)
CREATE OR REPLACE VIEW member_activity_summary AS
SELECT
  beneficiary_id,
  COUNT(*) as total_actions,
  COUNT(DISTINCT program_id) as programs_viewed,
  COUNT(CASE WHEN action = 'ENROLL' THEN 1 END) as enrollments,
  COUNT(CASE WHEN action = 'COMPARE' THEN 1 END) as comparisons,
  MAX(viewed_at) as last_action_at
FROM program_views_audit
GROUP BY beneficiary_id;

-- View: Program popularity (for Card 4)
CREATE OR REPLACE VIEW program_popularity AS
SELECT
  p.id,
  p.name,
  COUNT(bs.id) as total_enrollments,
  COUNT(CASE WHEN bs.enrollment_status = 'ACTIVE' THEN 1 END) as active_members,
  COUNT(CASE WHEN bs.enrollment_status = 'TERMINATED' THEN 1 END) as terminated_members
FROM programs p
LEFT JOIN beneficiary_selections bs ON p.id = bs.program_id
WHERE p.status = 'ACTIVE'
GROUP BY p.id, p.name
ORDER BY total_enrollments DESC;

-- ============================================================================
-- END Card 3 Database Schema
-- ============================================================================
