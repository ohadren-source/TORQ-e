/**
 * Program Validator
 * Validates transformed plan data against TORQ-E schema
 *
 * Enforces:
 * - Required fields present
 * - Correct data types
 * - Valid enum values
 * - Business logic rules
 * - Data quality standards
 *
 * Target: 99.5% completeness, 99% accuracy
 */

const crypto = require('crypto');

class ProgramValidator {
  constructor(config = {}) {
    this.auditLogger = config.auditLogger;
    this.strictMode = config.strictMode !== false; // Default: strict validation
  }

  /**
   * Validate single program record
   */
  validate(program) {
    const errors = [];

    // Required fields
    if (!program.name || typeof program.name !== 'string' || program.name.trim() === '') {
      errors.push({ field: 'name', issue: 'REQUIRED', message: 'Plan name is required and must be non-empty' });
    } else if (program.name.length > 255) {
      errors.push({ field: 'name', issue: 'LENGTH', message: 'Plan name exceeds 255 characters' });
    }

    if (!program.state || !/^[A-Z]{2}$/.test(program.state)) {
      errors.push({ field: 'state', issue: 'INVALID', message: 'State must be valid 2-letter US state code' });
    }

    if (!program.type || !['MEDICAID', 'MANAGED_CARE', 'SPECIAL_NEEDS', 'DUAL_ELIGIBLE'].includes(program.type)) {
      errors.push({ field: 'type', issue: 'INVALID', message: 'Plan type must be one of: MEDICAID, MANAGED_CARE, SPECIAL_NEEDS, DUAL_ELIGIBLE' });
    }

    // Eligibility criteria
    if (!program.eligibility_criteria) {
      errors.push({ field: 'eligibility_criteria', issue: 'REQUIRED', message: 'Eligibility criteria is required' });
    } else {
      const elig = program.eligibility_criteria;

      if (typeof elig.age_min !== 'number' || elig.age_min < 0) {
        errors.push({ field: 'eligibility_criteria.age_min', issue: 'INVALID', message: 'age_min must be a non-negative number' });
      }

      if (typeof elig.age_max !== 'number' || elig.age_max > 150) {
        errors.push({ field: 'eligibility_criteria.age_max', issue: 'INVALID', message: 'age_max must be a number ≤ 150' });
      }

      if (elig.age_min >= elig.age_max) {
        errors.push({ field: 'eligibility_criteria', issue: 'LOGIC', message: 'age_min must be less than age_max' });
      }

      if (typeof elig.income_limit !== 'number' || elig.income_limit < 0) {
        errors.push({ field: 'eligibility_criteria.income_limit', issue: 'INVALID', message: 'income_limit must be a positive number' });
      }

      if (typeof elig.citizenship_required !== 'boolean') {
        errors.push({ field: 'eligibility_criteria.citizenship_required', issue: 'TYPE', message: 'citizenship_required must be boolean' });
      }

      if (typeof elig.disability_status_required !== 'boolean') {
        errors.push({ field: 'eligibility_criteria.disability_status_required', issue: 'TYPE', message: 'disability_status_required must be boolean' });
      }
    }

    // Benefits
    if (!program.benefits || typeof program.benefits !== 'object') {
      errors.push({ field: 'benefits', issue: 'REQUIRED', message: 'Benefits is required and must be an object' });
    } else {
      // At least one benefit should be true
      const anyBenefit = Object.entries(program.benefits)
        .filter(([key]) => key !== 'custom_benefits')
        .some(([, value]) => value === true);

      if (!anyBenefit) {
        errors.push({ field: 'benefits', issue: 'LOGIC', message: 'Plan must cover at least one benefit' });
      }

      // All benefit flags should be boolean
      const benefitFields = ['primary_care', 'specialist_visits', 'emergency', 'hospitalization', 'pharmacy', 'mental_health', 'dental', 'vision', 'long_term_care'];
      benefitFields.forEach(field => {
        if (program.benefits[field] !== undefined && typeof program.benefits[field] !== 'boolean') {
          errors.push({ field: `benefits.${field}`, issue: 'TYPE', message: `${field} must be boolean` });
        }
      });
    }

    // Cost sharing
    if (!program.cost_sharing || typeof program.cost_sharing !== 'object') {
      errors.push({ field: 'cost_sharing', issue: 'REQUIRED', message: 'Cost sharing is required' });
    } else {
      const costFields = ['member_premium_monthly', 'copay_primary', 'copay_specialist', 'copay_emergency', 'deductible'];
      costFields.forEach(field => {
        const value = program.cost_sharing[field];
        if (typeof value !== 'number' || value < 0) {
          errors.push({ field: `cost_sharing.${field}`, issue: 'INVALID', message: `${field} must be a non-negative number` });
        }
      });
    }

    // Network type
    if (!program.network_type || !['HMO', 'PPO', 'FFS', 'CAPITATED'].includes(program.network_type)) {
      errors.push({ field: 'network_type', issue: 'INVALID', message: 'Network type must be one of: HMO, PPO, FFS, CAPITATED' });
    }

    // Coverage dates
    if (!program.coverage_start_date) {
      errors.push({ field: 'coverage_start_date', issue: 'REQUIRED', message: 'Coverage start date is required' });
    } else if (!this.isValidDate(program.coverage_start_date)) {
      errors.push({ field: 'coverage_start_date', issue: 'FORMAT', message: 'Coverage start date must be valid ISO date (YYYY-MM-DD)' });
    }

    if (program.coverage_end_date && !this.isValidDate(program.coverage_end_date)) {
      errors.push({ field: 'coverage_end_date', issue: 'FORMAT', message: 'Coverage end date must be valid ISO date (YYYY-MM-DD)' });
    }

    if (program.coverage_start_date && program.coverage_end_date) {
      if (program.coverage_start_date >= program.coverage_end_date) {
        errors.push({ field: 'coverage_dates', issue: 'LOGIC', message: 'Coverage start date must be before end date' });
      }
    }

    // Status
    if (!program.status || !['ACTIVE', 'PENDING', 'CLOSED', 'ARCHIVED'].includes(program.status)) {
      errors.push({ field: 'status', issue: 'INVALID', message: 'Status must be one of: ACTIVE, PENDING, CLOSED, ARCHIVED' });
    }

    // Contact info (optional but if present, should be valid)
    if (program.contact_info && typeof program.contact_info === 'object') {
      if (program.contact_info.website && !this.isValidUrl(program.contact_info.website)) {
        errors.push({ field: 'contact_info.website', issue: 'FORMAT', message: 'Website must be valid URL' });
      }
      if (program.contact_info.phone && !this.isValidPhone(program.contact_info.phone)) {
        errors.push({ field: 'contact_info.phone', issue: 'FORMAT', message: 'Phone must be valid format' });
      }
    }

    // Provider directory URL (optional but if present, should be valid)
    if (program.provider_directory_url && !this.isValidUrl(program.provider_directory_url)) {
      errors.push({ field: 'provider_directory_url', issue: 'FORMAT', message: 'Provider directory URL must be valid' });
    }

    return {
      valid: errors.length === 0,
      errors,
      record: program
    };
  }

  /**
   * Validate batch of programs
   */
  async validateBatch(programs) {
    console.log(`[Validator] Validating ${programs.length} programs...`);

    const results = {
      total: programs.length,
      valid: 0,
      invalid: 0,
      validPrograms: [],
      invalidPrograms: [],
      summary: {}
    };

    for (const program of programs) {
      const validation = this.validate(program);

      if (validation.valid) {
        results.valid++;
        results.validPrograms.push(program);
      } else {
        results.invalid++;
        results.invalidPrograms.push({
          program: program.name || 'Unknown',
          state: program.state,
          errors: validation.errors
        });
      }
    }

    // Calculate statistics
    results.summary = {
      validPercent: ((results.valid / results.total) * 100).toFixed(1),
      invalidPercent: ((results.invalid / results.total) * 100).toFixed(1),
      passed: results.valid >= results.total * 0.995 // 99.5% target
    };

    console.log(`[Validator] Validation complete: ${results.valid}/${results.total} valid (${results.summary.validPercent}%)`);

    if (!results.summary.passed && this.strictMode) {
      console.warn('[Validator] WARNING: Validation below 99.5% threshold');
    }

    await this.logValidation(programs, results);
    return results;
  }

  /**
   * Generate validation report
   */
  generateReport(validationResults) {
    const report = {
      timestamp: new Date().toISOString(),
      summary: validationResults.summary,
      totalRecords: validationResults.total,
      validRecords: validationResults.valid,
      invalidRecords: validationResults.invalid,

      errorsByType: {},
      errorsByField: {},
      errorSamples: []
    };

    // Group errors by type and field
    for (const invalid of validationResults.invalidPrograms) {
      for (const error of invalid.errors) {
        // By type
        if (!report.errorsByType[error.issue]) {
          report.errorsByType[error.issue] = 0;
        }
        report.errorsByType[error.issue]++;

        // By field
        if (!report.errorsByField[error.field]) {
          report.errorsByField[error.field] = 0;
        }
        report.errorsByField[error.field]++;
      }

      // Keep first 5 errors as samples
      if (report.errorSamples.length < 5) {
        report.errorSamples.push({
          program: invalid.program,
          errors: invalid.errors.slice(0, 3)
        });
      }
    }

    return report;
  }

  /**
   * Helper: Validate date format (YYYY-MM-DD)
   */
  isValidDate(dateStr) {
    if (!dateStr || typeof dateStr !== 'string') return false;
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!regex.test(dateStr)) return false;
    const date = new Date(dateStr);
    return !isNaN(date.getTime());
  }

  /**
   * Helper: Validate URL
   */
  isValidUrl(urlStr) {
    if (!urlStr || typeof urlStr !== 'string') return false;
    try {
      new URL(urlStr);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Helper: Validate phone format (basic)
   */
  isValidPhone(phoneStr) {
    if (!phoneStr || typeof phoneStr !== 'string') return true; // Optional field
    // Accept various formats: 123-456-7890, (123) 456-7890, 1234567890, etc.
    return /^\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$|^\d{10}$|^\d{1}-\d{3}-\d{3}-\d{4}$/.test(phoneStr);
  }

  /**
   * Log validation to audit trail
   */
  async logValidation(programs, results) {
    if (!this.auditLogger) {
      console.warn('[Validator] No audit logger configured, skipping log');
      return;
    }

    const logEntry = {
      timestamp: new Date().toISOString(),
      action: 'DATA_VALIDATED',
      totalRecords: results.total,
      validRecords: results.valid,
      invalidRecords: results.invalid,
      validPercent: results.summary.validPercent,
      passed: results.summary.passed,
      dataHash: this.hashData(programs)
    };

    try {
      await this.auditLogger.log(logEntry);
    } catch (logError) {
      console.error('[Validator] Failed to log validation:', logError.message);
    }
  }

  /**
   * Hash data
   */
  hashData(data) {
    const jsonString = typeof data === 'string' ? data : JSON.stringify(data);
    return crypto.createHash('sha256').update(jsonString).digest('hex');
  }
}

module.exports = ProgramValidator;
