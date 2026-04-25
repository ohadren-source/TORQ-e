/**
 * TORQ-E Card 3: Programs/Plans Marketplace API
 * Backend API for member plan discovery, comparison, and enrollment
 *
 * Stack: Node.js/Express, PostgreSQL, middleware for auth and logging
 */

const express = require('express');
const router = express.Router();
const db = require('../db'); // PostgreSQL connection pool
const { hashBeneficiaryId, logAuditTrail } = require('../utils');

// ============================================================================
// API ENDPOINT: GET /api/card3/programs
// Get list of all available programs (public data, no auth required)
// ============================================================================

router.get('/programs', async (req, res) => {
  try {
    const { state, program_type, status } = req.query;

    // Build query with optional filters
    let query = 'SELECT * FROM programs WHERE 1=1';
    const params = [];

    if (state) {
      query += ' AND state = $' + (params.length + 1);
      params.push(state);
    }

    if (program_type) {
      query += ' AND type = $' + (params.length + 1);
      params.push(program_type);
    }

    if (status) {
      query += ' AND status = $' + (params.length + 1);
      params.push(status);
    }

    query += ' ORDER BY name ASC';

    const result = await db.query(query, params);

    // Return program list (no audit needed for public data)
    res.json({
      count: result.rows.length,
      programs: result.rows
    });

  } catch (error) {
    console.error('Error fetching programs:', error);
    res.status(500).json({ error: 'Failed to fetch programs' });
  }
});

// ============================================================================
// API ENDPOINT: GET /api/card3/programs/{id}
// Get full details of a specific program
// ============================================================================

router.get('/programs/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const beneficiaryId = req.user?.id; // From auth token

    // Get program details
    const programResult = await db.query(
      'SELECT * FROM programs WHERE id = $1',
      [id]
    );

    if (programResult.rows.length === 0) {
      return res.status(404).json({ error: 'Program not found' });
    }

    const program = programResult.rows[0];

    // Log the view in audit trail (if beneficiary is authenticated)
    if (beneficiaryId) {
      await logAuditTrail({
        beneficiary_id: hashBeneficiaryId(beneficiaryId),
        action: 'PROGRAM_VIEWED',
        program_id: id,
        session_id: req.session?.id,
        device_type: req.body?.device_type || 'DESKTOP',
        duration_ms: req.body?.duration_ms || 0
      });
    }

    res.json(program);

  } catch (error) {
    console.error('Error fetching program:', error);
    res.status(500).json({ error: 'Failed to fetch program' });
  }
});

// ============================================================================
// API ENDPOINT: GET /api/card3/eligible-programs
// Get programs filtered to member's eligibility
// Requires: Authentication (Card 1 OAuth token)
// ============================================================================

router.get('/eligible-programs', async (req, res) => {
  try {
    // Verify authentication
    if (!req.user?.id) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const beneficiaryId = req.user.id;

    // Query Card 1 for member eligibility data
    // (In real system, this would call Card 1 API or shared database)
    const eligibilityResult = await db.query(
      'SELECT eligibility_data FROM members WHERE id = $1',
      [beneficiaryId]
    );

    if (eligibilityResult.rows.length === 0) {
      return res.status(404).json({ error: 'Member not found' });
    }

    const memberEligibility = eligibilityResult.rows[0].eligibility_data;

    // Get all ACTIVE programs
    const programsResult = await db.query(
      'SELECT * FROM programs WHERE status = $1 ORDER BY name ASC',
      ['ACTIVE']
    );

    // Filter programs by member eligibility
    const eligiblePrograms = programsResult.rows.filter(program => {
      const criteria = program.eligibility_criteria;

      // Check age
      if (memberEligibility.age < criteria.age_min || memberEligibility.age > criteria.age_max) {
        return false;
      }

      // Check income
      if (memberEligibility.income > criteria.income_limit) {
        return false;
      }

      // Check citizenship if required
      if (criteria.citizenship_required && !memberEligibility.is_citizen) {
        return false;
      }

      // Check disability if required
      if (criteria.disability_status_required && !memberEligibility.is_disabled) {
        return false;
      }

      return true;
    });

    // Log the query (not the result, to preserve privacy)
    await logAuditTrail({
      beneficiary_id: hashBeneficiaryId(beneficiaryId),
      action: 'ELIGIBLE_PROGRAMS_QUERIED',
      session_id: req.session?.id
    });

    res.json({
      count: eligiblePrograms.length,
      programs: eligiblePrograms
    });

  } catch (error) {
    console.error('Error fetching eligible programs:', error);
    res.status(500).json({ error: 'Failed to fetch eligible programs' });
  }
});

// ============================================================================
// API ENDPOINT: POST /api/card3/programs/{id}/compare
// Compare 2-3 programs side-by-side
// ============================================================================

router.post('/programs/:id/compare', async (req, res) => {
  try {
    const { program_ids } = req.body; // Array of 2-3 program IDs to compare

    if (!Array.isArray(program_ids) || program_ids.length < 2 || program_ids.length > 3) {
      return res.status(400).json({ error: 'Provide 2-3 program IDs for comparison' });
    }

    // Fetch all programs
    const placeholders = program_ids.map((_, i) => '$' + (i + 1)).join(',');
    const result = await db.query(
      `SELECT * FROM programs WHERE id IN (${placeholders})`,
      program_ids
    );

    if (result.rows.length !== program_ids.length) {
      return res.status(404).json({ error: 'One or more programs not found' });
    }

    // Log the comparison
    if (req.user?.id) {
      await logAuditTrail({
        beneficiary_id: hashBeneficiaryId(req.user.id),
        action: 'PROGRAMS_COMPARED',
        program_ids: program_ids,
        session_id: req.session?.id
      });
    }

    // Build comparison data
    const comparisonData = {
      programs: result.rows,
      cost_comparison: buildCostComparison(result.rows),
      benefits_comparison: buildBenefitsComparison(result.rows),
      network_comparison: buildNetworkComparison(result.rows)
    };

    res.json(comparisonData);

  } catch (error) {
    console.error('Error comparing programs:', error);
    res.status(500).json({ error: 'Failed to compare programs' });
  }
});

// ============================================================================
// API ENDPOINT: POST /api/card3/enroll
// Enroll member in a program
// Requires: Authentication
// ============================================================================

router.post('/enroll', async (req, res) => {
  try {
    // Verify authentication
    if (!req.user?.id) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { program_id } = req.body;
    const beneficiaryId = req.user.id;

    // Verify program exists and is ACTIVE
    const programResult = await db.query(
      'SELECT * FROM programs WHERE id = $1 AND status = $1',
      [program_id, 'ACTIVE']
    );

    if (programResult.rows.length === 0) {
      return res.status(404).json({ error: 'Program not found or inactive' });
    }

    const program = programResult.rows[0];

    // Re-verify eligibility at enrollment time
    const memberResult = await db.query(
      'SELECT eligibility_data FROM members WHERE id = $1',
      [beneficiaryId]
    );

    const memberEligibility = memberResult.rows[0].eligibility_data;
    const criteria = program.eligibility_criteria;

    // Quick eligibility check
    if (memberEligibility.age < criteria.age_min || memberEligibility.age > criteria.age_max) {
      return res.status(400).json({ error: 'Member no longer eligible (age mismatch)' });
    }

    if (memberEligibility.income > criteria.income_limit) {
      return res.status(400).json({ error: 'Member no longer eligible (income mismatch)' });
    }

    // Create enrollment record (immutable)
    const selectionResult = await db.query(
      `INSERT INTO beneficiary_selections
        (beneficiary_id, program_id, selected_at, selection_effective_date, enrollment_status, audit_trail)
       VALUES ($1, $2, NOW(), $3, $4, $5)
       RETURNING *`,
      [
        hashBeneficiaryId(beneficiaryId),
        program_id,
        new Date().toISOString().split('T')[0], // today's date
        'PENDING',
        JSON.stringify({
          created_at: new Date().toISOString(),
          action: 'MEMBER_ENROLLED',
          method: 'online'
        })
      ]
    );

    const selection = selectionResult.rows[0];

    // Log enrollment action (immutable)
    await logAuditTrail({
      beneficiary_id: hashBeneficiaryId(beneficiaryId),
      action: 'PROGRAM_ENROLLED',
      program_id: program_id,
      enrollment_status: 'PENDING',
      handoff_token: selection.id,
      session_id: req.session?.id
    });

    // Send to Card 1 for enrollment processing
    // (In real system, call Card 1 API or trigger event)
    const handoffResult = await sendToCard1ForProcessing(beneficiaryId, program_id, selection.id);

    res.json({
      success: true,
      message: 'Enrollment successful',
      selection_id: selection.id,
      program_name: program.name,
      coverage_start_date: program.coverage_start_date,
      confirmation_token: handoffResult.token
    });

  } catch (error) {
    console.error('Error enrolling member:', error);
    res.status(500).json({ error: 'Enrollment failed' });
  }
});

// ============================================================================
// API ENDPOINT: GET /api/card3/beneficiary-selection
// Get current member's program selection and history
// Requires: Authentication
// ============================================================================

router.get('/beneficiary-selection', async (req, res) => {
  try {
    if (!req.user?.id) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const beneficiaryId = req.user.id;
    const hashedId = hashBeneficiaryId(beneficiaryId);

    // Get current selection (most recent ACTIVE or PENDING)
    const currentResult = await db.query(
      `SELECT * FROM beneficiary_selections
       WHERE beneficiary_id = $1 AND enrollment_status IN ('ACTIVE', 'PENDING')
       ORDER BY selected_at DESC
       LIMIT 1`,
      [hashedId]
    );

    // Get selection history (all selections)
    const historyResult = await db.query(
      `SELECT * FROM beneficiary_selections
       WHERE beneficiary_id = $1
       ORDER BY selected_at DESC`,
      [hashedId]
    );

    // Log the query (not the result)
    await logAuditTrail({
      beneficiary_id: hashedId,
      action: 'SELECTION_HISTORY_VIEWED',
      session_id: req.session?.id
    });

    res.json({
      current_selection: currentResult.rows[0] || null,
      history: historyResult.rows
    });

  } catch (error) {
    console.error('Error fetching selection:', error);
    res.status(500).json({ error: 'Failed to fetch selection history' });
  }
});

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function buildCostComparison(programs) {
  return programs.map(program => ({
    program_id: program.id,
    program_name: program.name,
    monthly_premium: program.cost_sharing.member_premium_monthly,
    copay_primary: program.cost_sharing.copay_primary,
    copay_specialist: program.cost_sharing.copay_specialist,
    copay_emergency: program.cost_sharing.copay_emergency,
    deductible: program.cost_sharing.deductible
  }));
}

function buildBenefitsComparison(programs) {
  return programs.map(program => ({
    program_id: program.id,
    program_name: program.name,
    benefits: program.benefits
  }));
}

function buildNetworkComparison(programs) {
  return programs.map(program => ({
    program_id: program.id,
    program_name: program.name,
    network_type: program.network_type,
    provider_directory_url: program.provider_directory_url
  }));
}

async function sendToCard1ForProcessing(beneficiaryId, programId, selectionId) {
  // In production, this would:
  // 1. Call Card 1 API: POST /api/card1/enrollment-handoff
  // 2. Include: beneficiary_id, program_id, selection_id
  // 3. Receive: confirmation token, processing status
  // 4. Log the handoff in audit trail

  // Mock implementation
  return {
    token: `tok-${selectionId}`,
    status: 'PROCESSING'
  };
}

module.exports = router;
