/**
 * Data Transformer
 * Converts data from multiple sources into unified TORQ-E schema
 *
 * Supports:
 * - CMS API format → TORQ-E
 * - eMedNY HTML parsed data → TORQ-E
 * - Generic state API format → TORQ-E
 *
 * Every transformation is logged (audit trail)
 */

const crypto = require('crypto');

class DataTransformer {
  constructor(config = {}) {
    this.auditLogger = config.auditLogger;
    this.sourceFormat = config.sourceFormat; // CMS_API, EMEDNY, STATE_API, etc.
    this.targetFormat = 'TORQE';
  }

  /**
   * Main transform method - delegates to source-specific transformer
   */
  async transform(sourceData) {
    try {
      console.log(`[Transformer] Transforming ${this.sourceFormat} → ${this.targetFormat}...`);

      let transformedData;

      switch (this.sourceFormat) {
        case 'CMS_API':
          transformedData = sourceData.map(item => this.transformCMSData(item));
          break;
        case 'EMEDNY':
          transformedData = sourceData.map(item => this.transformEMedNYData(item));
          break;
        case 'STATE_API':
          transformedData = sourceData.map(item => this.transformStateData(item));
          break;
        default:
          throw new Error(`Unknown source format: ${this.sourceFormat}`);
      }

      console.log(`[Transformer] Transformed ${transformedData.length} records`);

      await this.logTransformation(sourceData, transformedData, true);
      return transformedData;

    } catch (error) {
      console.error(`[Transformer] Transformation failed:`, error.message);
      await this.logTransformation(sourceData, null, false, error);
      throw error;
    }
  }

  /**
   * Transform CMS API format to TORQ-E
   */
  transformCMSData(cmsPlan) {
    return {
      name: cmsPlan.plan_name || 'Unknown Plan',
      type: this.mapPlanType(cmsPlan.plan_type_code || cmsPlan.plan_type),
      state: cmsPlan.state_code || cmsPlan.state || 'US',

      eligibility_criteria: {
        age_min: parseInt(cmsPlan.min_age || 0),
        age_max: parseInt(cmsPlan.max_age || 120),
        income_limit: parseInt(cmsPlan.income_threshold || 250000),
        citizenship_required: this.parseBoolean(cmsPlan.citizenship_required, true),
        disability_status_required: this.parseBoolean(cmsPlan.disability_required, false),
        special_conditions: cmsPlan.special_conditions || []
      },

      benefits: this.transformCMSBenefits(cmsPlan.benefits_matrix || cmsPlan.benefits),

      cost_sharing: {
        member_premium_monthly: Math.max(0, parseInt(cmsPlan.monthly_premium || cmsPlan.premium || 0)),
        copay_primary: Math.max(0, parseInt(cmsPlan.copay_pcp || cmsPlan.copay_primary || 0)),
        copay_specialist: Math.max(0, parseInt(cmsPlan.copay_specialist || cmsPlan.copay_spec || 0)),
        copay_emergency: Math.max(0, parseInt(cmsPlan.copay_emergency || cmsPlan.copay_er || 0)),
        deductible: Math.max(0, parseInt(cmsPlan.deductible || cmsPlan.annual_deductible || 0))
      },

      network_type: this.mapNetworkType(cmsPlan.network_type_code || cmsPlan.network_type),
      provider_directory_url: cmsPlan.directory_url || cmsPlan.provider_directory || null,

      coverage_start_date: this.parseDate(cmsPlan.effective_date || cmsPlan.start_date),
      coverage_end_date: this.parseDate(cmsPlan.termination_date || cmsPlan.end_date) || null,

      contact_info: {
        phone: cmsPlan.customer_service_phone || cmsPlan.phone || null,
        website: cmsPlan.website || cmsPlan.url || null,
        support_hours: cmsPlan.service_hours || 'N/A'
      },

      enrollment_deadline: this.parseDate(cmsPlan.enrollment_deadline || cmsPlan.deadline),
      status: this.mapStatus(cmsPlan.is_active !== false, cmsPlan.status),

      // Metadata
      source: 'CMS_API',
      source_plan_id: cmsPlan.plan_id || cmsPlan.id,
      transformed_at: new Date().toISOString()
    };
  }

  /**
   * Transform eMedNY HTML-parsed data to TORQ-E
   */
  transformEMedNYData(emednyPlan) {
    return {
      name: emednyPlan.plan_name?.trim() || 'Unknown Plan',
      type: this.mapPlanType(emednyPlan.plan_type),
      state: 'NY',

      eligibility_criteria: {
        age_min: 0,
        age_max: 120,
        income_limit: this.extractIncomeLimitFromText(emednyPlan.benefits_html || ''),
        citizenship_required: true,
        disability_status_required: this.checkIfDisabilityRequired(emednyPlan.plan_type),
        special_conditions: []
      },

      benefits: this.transformEMedNYBenefits(emednyPlan),

      cost_sharing: this.extractCosts(emednyPlan.cost_section || emednyPlan.costs_extracted),

      network_type: this.mapNetworkType(emednyPlan.network_type),
      provider_directory_url: emednyPlan.directory_link || null,

      coverage_start_date: this.parseDate(emednyPlan.start_date),
      coverage_end_date: this.parseDate(emednyPlan.end_date) || null,

      contact_info: {
        phone: emednyPlan.phone_number || null,
        website: emednyPlan.plan_website || null,
        support_hours: 'N/A'
      },

      enrollment_deadline: this.parseDate(emednyPlan.enrollment_deadline),
      status: emednyPlan.is_available ? 'ACTIVE' : 'CLOSED',

      // Metadata
      source: 'EMEDNY',
      source_plan_id: emednyPlan.plan_id,
      transformed_at: new Date().toISOString()
    };
  }

  /**
   * Transform generic state API data to TORQ-E
   */
  transformStateData(statePlan) {
    return {
      name: statePlan.name || statePlan.plan_name || 'Unknown Plan',
      type: this.mapPlanType(statePlan.type || statePlan.plan_type),
      state: statePlan.state || statePlan.state_code,

      eligibility_criteria: {
        age_min: parseInt(statePlan.eligibility?.age_min || statePlan.age_min || 0),
        age_max: parseInt(statePlan.eligibility?.age_max || statePlan.age_max || 120),
        income_limit: parseInt(statePlan.eligibility?.income_limit || statePlan.income_limit || 250000),
        citizenship_required: this.parseBoolean(statePlan.eligibility?.citizenship_required, true),
        disability_status_required: this.parseBoolean(statePlan.eligibility?.disability_required, false),
        special_conditions: statePlan.eligibility?.special_conditions || []
      },

      benefits: statePlan.benefits || {
        primary_care: true,
        specialist_visits: true,
        emergency: true,
        hospitalization: true,
        pharmacy: true,
        mental_health: true,
        dental: false,
        vision: false,
        long_term_care: false,
        custom_benefits: []
      },

      cost_sharing: {
        member_premium_monthly: Math.max(0, parseInt(statePlan.cost_sharing?.premium || 0)),
        copay_primary: Math.max(0, parseInt(statePlan.cost_sharing?.copay_primary || 0)),
        copay_specialist: Math.max(0, parseInt(statePlan.cost_sharing?.copay_specialist || 0)),
        copay_emergency: Math.max(0, parseInt(statePlan.cost_sharing?.copay_emergency || 0)),
        deductible: Math.max(0, parseInt(statePlan.cost_sharing?.deductible || 0))
      },

      network_type: this.mapNetworkType(statePlan.network_type),
      provider_directory_url: statePlan.provider_directory_url || null,

      coverage_start_date: this.parseDate(statePlan.coverage_start_date),
      coverage_end_date: this.parseDate(statePlan.coverage_end_date) || null,

      contact_info: {
        phone: statePlan.contact?.phone || null,
        website: statePlan.contact?.website || null,
        support_hours: statePlan.contact?.hours || 'N/A'
      },

      enrollment_deadline: this.parseDate(statePlan.enrollment_deadline),
      status: this.mapStatus(statePlan.is_active !== false, statePlan.status),

      // Metadata
      source: 'STATE_API',
      source_plan_id: statePlan.id || statePlan.plan_id,
      transformed_at: new Date().toISOString()
    };
  }

  /**
   * Transform CMS benefits matrix to TORQ-E benefits
   */
  transformCMSBenefits(cmsBenefits) {
    if (!cmsBenefits) return this.defaultBenefits();

    return {
      primary_care: cmsBenefits.pcp_covered === true || cmsBenefits.primary_care === true,
      specialist_visits: cmsBenefits.specialist_covered === true || cmsBenefits.specialists === true,
      emergency: cmsBenefits.emergency_covered === true || cmsBenefits.emergency === true,
      hospitalization: cmsBenefits.inpatient_covered === true || cmsBenefits.hospitalization === true,
      pharmacy: cmsBenefits.pharmacy_covered === true || cmsBenefits.pharmacy === true,
      mental_health: cmsBenefits.mental_health_covered === true || cmsBenefits.mental_health === true,
      dental: cmsBenefits.dental_covered === true || cmsBenefits.dental === true,
      vision: cmsBenefits.vision_covered === true || cmsBenefits.vision === true,
      long_term_care: cmsBenefits.ltc_covered === true || cmsBenefits.long_term_care === true,
      custom_benefits: cmsBenefits.custom_benefits || []
    };
  }

  /**
   * Transform eMedNY benefits to TORQ-E
   */
  transformEMedNYBenefits(emednyPlan) {
    const html = emednyPlan.benefits_html || '';
    const text = html.toLowerCase();
    const extracted = emednyPlan.benefits_extracted || [];

    return {
      primary_care: text.includes('primary care') || text.includes('pcp') || extracted.some(b => b.includes('primary')),
      specialist_visits: text.includes('specialist') || extracted.some(b => b.includes('specialist')),
      emergency: text.includes('emergency') || extracted.some(b => b.includes('emergency')),
      hospitalization: text.includes('hospital') || text.includes('inpatient') || extracted.some(b => b.includes('hospital')),
      pharmacy: text.includes('pharmacy') || text.includes('prescription') || extracted.some(b => b.includes('pharmacy')),
      mental_health: text.includes('mental health') || text.includes('behavioral') || extracted.some(b => b.includes('mental')),
      dental: text.includes('dental') || extracted.some(b => b.includes('dental')),
      vision: text.includes('vision') || text.includes('eye') || extracted.some(b => b.includes('vision')),
      long_term_care: text.includes('long-term') || text.includes('nursing') || extracted.some(b => b.includes('long-term')),
      custom_benefits: []
    };
  }

  /**
   * Extract costs from HTML or cost object
   */
  extractCosts(costData) {
    const costs = {
      member_premium_monthly: 0,
      copay_primary: 0,
      copay_specialist: 0,
      copay_emergency: 0,
      deductible: 0
    };

    if (!costData) return costs;

    // If it's already parsed object
    if (costData.monthly_premium !== undefined) {
      return {
        member_premium_monthly: Math.max(0, parseInt(costData.monthly_premium || 0)),
        copay_primary: Math.max(0, parseInt(costData.copay_primary || costData.copay || 0)),
        copay_specialist: Math.max(0, parseInt(costData.copay_specialist || 25)),
        copay_emergency: Math.max(0, parseInt(costData.copay_emergency || 0)),
        deductible: Math.max(0, parseInt(costData.deductible || 0))
      };
    }

    // Parse from HTML string
    const text = typeof costData === 'string' ? costData : JSON.stringify(costData);
    const premiumMatch = text.match(/premium[:\s]+\$?([\d,]+)/i);
    const copayMatch = text.match(/copay[:\s]+\$?([\d,]+)/i);
    const deductibleMatch = text.match(/deductible[:\s]+\$?([\d,]+)/i);

    if (premiumMatch) costs.member_premium_monthly = parseInt(premiumMatch[1].replace(/,/g, ''));
    if (copayMatch) costs.copay_primary = parseInt(copayMatch[1].replace(/,/g, ''));
    if (deductibleMatch) costs.deductible = parseInt(deductibleMatch[1].replace(/,/g, ''));

    return costs;
  }

  /**
   * Helper: Map plan type codes to TORQ-E enum
   */
  mapPlanType(typeCode) {
    if (!typeCode) return 'MEDICAID';

    const typeMap = {
      'ma': 'MANAGED_CARE',
      'medicare advantage': 'MANAGED_CARE',
      'medicaid': 'MEDICAID',
      'managed care': 'MANAGED_CARE',
      'hmo': 'MANAGED_CARE',
      'ppo': 'MANAGED_CARE',
      'special needs': 'SPECIAL_NEEDS',
      'dual eligible': 'DUAL_ELIGIBLE',
      'snp': 'SPECIAL_NEEDS'
    };

    const mapped = typeMap[typeCode.toLowerCase()];
    return mapped || 'MEDICAID';
  }

  /**
   * Helper: Map network type codes
   */
  mapNetworkType(netCode) {
    if (!netCode) return 'HMO';

    const netMap = {
      'hmo': 'HMO',
      'ppo': 'PPO',
      'ffs': 'FFS',
      'fee for service': 'FFS',
      'capitated': 'CAPITATED'
    };

    const mapped = netMap[netCode.toLowerCase()];
    return mapped || 'HMO';
  }

  /**
   * Helper: Parse boolean values from various formats
   */
  parseBoolean(value, defaultValue = false) {
    if (value === null || value === undefined) return defaultValue;
    if (typeof value === 'boolean') return value;
    if (typeof value === 'string') {
      return ['true', '1', 'yes', 'y'].includes(value.toLowerCase());
    }
    return Boolean(value);
  }

  /**
   * Helper: Parse dates to ISO format
   */
  parseDate(dateValue) {
    if (!dateValue) return null;

    try {
      const date = new Date(dateValue);
      if (isNaN(date.getTime())) return null;
      return date.toISOString().split('T')[0];
    } catch {
      return null;
    }
  }

  /**
   * Helper: Extract income limit from text
   */
  extractIncomeLimitFromText(text) {
    if (!text) return 250000;
    const match = text.match(/\$?([\d,]+)\s*(month|year|annual)?/);
    if (match) {
      const amount = parseInt(match[1].replace(/,/g, ''));
      // If it looks like monthly, multiply by 12
      if (match[2] && match[2].toLowerCase() === 'month') {
        return amount * 12;
      }
      return amount;
    }
    return 250000;
  }

  /**
   * Helper: Check if plan is for disabled individuals
   */
  checkIfDisabilityRequired(planType) {
    if (!planType) return false;
    return planType.toLowerCase().includes('special') || planType.toLowerCase().includes('disability');
  }

  /**
   * Helper: Map status
   */
  mapStatus(isActive, statusCode) {
    if (statusCode) {
      const statusMap = {
        'active': 'ACTIVE',
        'pending': 'PENDING',
        'closed': 'CLOSED',
        'archived': 'ARCHIVED'
      };
      return statusMap[statusCode.toLowerCase()] || 'ACTIVE';
    }
    return isActive ? 'ACTIVE' : 'ARCHIVED';
  }

  /**
   * Default benefits (all standard benefits available)
   */
  defaultBenefits() {
    return {
      primary_care: true,
      specialist_visits: true,
      emergency: true,
      hospitalization: true,
      pharmacy: true,
      mental_health: true,
      dental: false,
      vision: false,
      long_term_care: false,
      custom_benefits: []
    };
  }

  /**
   * Log transformation to audit trail
   */
  async logTransformation(sourceData, transformedData, success, error = null) {
    if (!this.auditLogger) {
      console.warn('[Transformer] No audit logger configured, skipping log');
      return;
    }

    const logEntry = {
      timestamp: new Date().toISOString(),
      action: 'DATA_TRANSFORMED',
      sourceFormat: this.sourceFormat,
      targetFormat: this.targetFormat,
      recordCount: transformedData ? (Array.isArray(transformedData) ? transformedData.length : 1) : 0,
      success,
      error: error ? error.message : null,
      sourceDataHash: sourceData ? this.hashData(sourceData) : null,
      transformedDataHash: transformedData ? this.hashData(transformedData) : null
    };

    try {
      await this.auditLogger.log(logEntry);
    } catch (logError) {
      console.error('[Transformer] Failed to log transformation:', logError.message);
    }
  }

  /**
   * Hash data for integrity
   */
  hashData(data) {
    const jsonString = typeof data === 'string' ? data : JSON.stringify(data);
    return crypto.createHash('sha256').update(jsonString).digest('hex');
  }
}

module.exports = DataTransformer;
