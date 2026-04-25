# TORQ-E Data Ingestion Implementation
## Internal Design Repository (DR)

---

## Overview

**What we're building:** The actual code that executes the ETL pipeline.

**Components:**
1. Extractors — Pull data from public sources (CMS, eMedNY, state APIs)
2. Transformers — Convert source formats to TORQ-E schema
3. Validators — Check data quality, completeness, accuracy
4. Loaders — Insert/update data in Card 3 database
5. Orchestrator — Schedule and coordinate everything
6. Error Handler — Deal with failures gracefully

**Technology Stack:**
- **Language:** Node.js / JavaScript (same as backend)
- **Database:** PostgreSQL (already specified in Card 3 schema)
- **Scheduler:** node-cron (for daily runs)
- **HTTP Client:** axios (for API calls)
- **Web Scraping:** cheerio + puppeteer (for HTML parsing)
- **Logging:** winston (immutable audit logs)
- **Validation:** joi (schema validation)

---

## Architecture: Component Structure

```
ingestion-pipeline/
├── extractors/
│   ├── cms-api-extractor.js       (CMS API client)
│   ├── emedny-scraper.js          (eMedNY web scraper)
│   ├── state-api-extractor.js     (Generic state API client)
│   └── base-extractor.js          (Base class for all extractors)
├── transformers/
│   ├── cms-transformer.js         (CMS format → TORQ-E)
│   ├── emedny-transformer.js      (eMedNY format → TORQ-E)
│   ├── state-transformer.js       (State format → TORQ-E)
│   └── base-transformer.js        (Base class, common logic)
├── validators/
│   ├── program-validator.js       (Validate program schema)
│   ├── benefit-validator.js       (Validate benefits)
│   ├── cost-validator.js          (Validate costs)
│   └── rules-engine.js            (Data quality rules)
├── loaders/
│   ├── postgres-loader.js         (Load to database)
│   ├── deduplication-engine.js    (Handle duplicate programs)
│   └── archive-engine.js          (Archive old programs)
├── orchestrator/
│   ├── pipeline-orchestrator.js   (Coordinate ETL flow)
│   ├── scheduler.js               (Cron jobs)
│   └── error-handler.js           (Failure recovery)
├── logging/
│   ├── audit-logger.js            (Immutable audit trail)
│   └── error-logger.js            (Error tracking)
└── config/
    ├── sources-config.json        (Data source definitions)
    ├── transformation-map.json    (Field mappings)
    └── validation-rules.json      (Quality rules)
```

---

## Extractors: Pull Data from Sources

### Base Extractor (Abstract)

```javascript
class BaseExtractor {
  constructor(sourceConfig) {
    this.sourceName = sourceConfig.name;
    this.sourceUrl = sourceConfig.url;
    this.updateFrequency = sourceConfig.updateFrequency;
    this.timeout = sourceConfig.timeout || 30000;
    this.retryAttempts = sourceConfig.retryAttempts || 3;
  }

  async extract() {
    // Override in subclasses
    throw new Error('extract() must be implemented');
  }

  async retryWithBackoff(fn, attempt = 0) {
    // Retry with exponential backoff: 1s, 2s, 4s, 8s, ...
    try {
      return await fn();
    } catch (error) {
      if (attempt < this.retryAttempts) {
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.retryWithBackoff(fn, attempt + 1);
      }
      throw error;
    }
  }

  async logExtraction(rawData, success, error = null) {
    // Log to immutable audit trail
    await AuditLogger.log({
      timestamp: new Date().toISOString(),
      action: 'DATA_EXTRACTED',
      source: this.sourceName,
      recordCount: rawData?.length || 0,
      success,
      error: error?.message,
      rawDataHash: hashData(rawData)
    });
  }
}
```

### CMS API Extractor

```javascript
class CMSAPIExtractor extends BaseExtractor {
  constructor() {
    super({
      name: 'CMS_API',
      url: 'https://api.cms.gov/v1/medicaid/plans',
      updateFrequency: 'daily'
    });
    this.apiKey = process.env.CMS_API_KEY;
  }

  async extract() {
    try {
      const plans = await this.retryWithBackoff(() =>
        axios.get(this.sourceUrl, {
          headers: { 'Authorization': `Bearer ${this.apiKey}` },
          timeout: this.timeout
        })
      );

      await this.logExtraction(plans.data, true);
      return plans.data;
    } catch (error) {
      await this.logExtraction(null, false, error);
      throw error;
    }
  }
}
```

### eMedNY Web Scraper

```javascript
class EMedNYScraper extends BaseExtractor {
  constructor() {
    super({
      name: 'EMEDNY_SCRAPER',
      url: 'https://www.emedny.org/plans',
      updateFrequency: 'daily'
    });
  }

  async extract() {
    let browser;
    try {
      // Use Puppeteer for JavaScript-rendered content
      browser = await puppeteer.launch();
      const page = await browser.newPage();
      
      await page.goto(this.sourceUrl, { waitUntil: 'networkidle2', timeout: this.timeout });

      // Extract plan list
      const rawData = await page.evaluate(() => {
        const plans = [];
        document.querySelectorAll('[data-plan-id]').forEach(el => {
          plans.push({
            plan_id: el.getAttribute('data-plan-id'),
            plan_name: el.querySelector('[data-name]')?.textContent,
            plan_type: el.getAttribute('data-type'),
            benefits_html: el.querySelector('[data-benefits]')?.innerHTML,
            cost_section: el.querySelector('[data-costs]')?.innerHTML,
            network_type: el.getAttribute('data-network'),
            // ... other fields
          });
        });
        return plans;
      });

      await this.logExtraction(rawData, true);
      return rawData;
    } catch (error) {
      await this.logExtraction(null, false, error);
      throw error;
    } finally {
      if (browser) await browser.close();
    }
  }
}
```

### State API Extractor (Generic)

```javascript
class StateAPIExtractor extends BaseExtractor {
  constructor(stateCode, config) {
    super({
      name: `STATE_API_${stateCode}`,
      url: config.apiUrl,
      updateFrequency: config.updateFrequency || 'weekly'
    });
    this.stateCode = stateCode;
    this.apiKey = process.env[`${stateCode}_API_KEY`];
    this.apiVersion = config.apiVersion;
  }

  async extract() {
    try {
      const plans = await this.retryWithBackoff(() =>
        axios.get(this.sourceUrl, {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'X-API-Version': this.apiVersion
          },
          timeout: this.timeout
        })
      );

      await this.logExtraction(plans.data, true);
      return plans.data;
    } catch (error) {
      await this.logExtraction(null, false, error);
      throw error;
    }
  }
}
```

---

## Transformers: Convert to TORQ-E Schema

### Base Transformer (Abstract)

```javascript
class BaseTransformer {
  constructor(sourceFormat, targetFormat = 'TORQE') {
    this.sourceFormat = sourceFormat;
    this.targetFormat = targetFormat;
  }

  async transform(rawData) {
    // Override in subclasses
    throw new Error('transform() must be implemented');
  }

  mapField(sourceValue, fieldMapping) {
    // Apply field transformation (rename, convert, extract)
    if (fieldMapping.type === 'direct') {
      return sourceValue;
    }
    if (fieldMapping.type === 'map') {
      return fieldMapping.mapping[sourceValue] || null;
    }
    if (fieldMapping.type === 'extract') {
      return this.extractValue(sourceValue, fieldMapping.path);
    }
    if (fieldMapping.type === 'calculate') {
      return fieldMapping.fn(sourceValue);
    }
    return null;
  }

  extractValue(obj, path) {
    // Navigate nested objects: 'benefits.primary_care' → obj.benefits.primary_care
    return path.split('.').reduce((curr, prop) => curr?.[prop], obj);
  }

  async logTransformation(sourceData, transformedData, success, error = null) {
    await AuditLogger.log({
      timestamp: new Date().toISOString(),
      action: 'DATA_TRANSFORMED',
      sourceFormat: this.sourceFormat,
      targetFormat: this.targetFormat,
      recordCount: transformedData?.length || 0,
      success,
      error: error?.message,
      sourceDataHash: hashData(sourceData),
      transformedDataHash: hashData(transformedData)
    });
  }
}
```

### CMS Transformer

```javascript
class CMSTransformer extends BaseTransformer {
  constructor() {
    super('CMS_API');
    this.fieldMap = require('./cms-field-map.json');
  }

  async transform(cmsPlans) {
    try {
      const torqePlans = cmsPlans.map(plan => ({
        name: this.mapField(plan.plan_name, this.fieldMap.name),
        type: this.mapField(plan.plan_type_code, this.fieldMap.type),
        state: this.mapField(plan.state_code, this.fieldMap.state),
        eligibility_criteria: {
          age_min: this.mapField(plan.min_age, this.fieldMap.eligibility.age_min),
          age_max: this.mapField(plan.max_age, this.fieldMap.eligibility.age_max),
          income_limit: this.mapField(plan.income_threshold, this.fieldMap.eligibility.income_limit),
          citizenship_required: this.mapField(plan.citizenship_flag, this.fieldMap.eligibility.citizenship),
          disability_status_required: this.mapField(plan.disability_flag, this.fieldMap.eligibility.disability),
          special_conditions: plan.special_conditions || []
        },
        benefits: this.transformBenefits(plan.benefits_matrix),
        cost_sharing: this.transformCosts(plan.cost_data),
        network_type: this.mapField(plan.network_type_code, this.fieldMap.network_type),
        provider_directory_url: this.mapField(plan.directory_url, this.fieldMap.provider_directory),
        coverage_start_date: this.mapField(plan.effective_date, this.fieldMap.coverage_start),
        coverage_end_date: this.mapField(plan.termination_date, this.fieldMap.coverage_end),
        contact_info: {
          phone: plan.customer_service_phone,
          website: plan.website,
          support_hours: plan.service_hours || 'N/A'
        },
        enrollment_deadline: this.mapField(plan.enrollment_deadline, this.fieldMap.enrollment_deadline),
        status: plan.is_active ? 'ACTIVE' : 'ARCHIVED'
      }));

      await this.logTransformation(cmsPlans, torqePlans, true);
      return torqePlans;
    } catch (error) {
      await this.logTransformation(cmsPlans, null, false, error);
      throw error;
    }
  }

  transformBenefits(cmsBenefits) {
    return {
      primary_care: cmsBenefits?.pcp_covered || false,
      specialist_visits: cmsBenefits?.specialist_covered || false,
      emergency: cmsBenefits?.emergency_covered || false,
      hospitalization: cmsBenefits?.inpatient_covered || false,
      pharmacy: cmsBenefits?.pharmacy_covered || false,
      mental_health: cmsBenefits?.mental_health_covered || false,
      dental: cmsBenefits?.dental_covered || false,
      vision: cmsBenefits?.vision_covered || false,
      long_term_care: cmsBenefits?.ltc_covered || false,
      custom_benefits: cmsBenefits?.custom_benefits || []
    };
  }

  transformCosts(cmsCosts) {
    return {
      member_premium_monthly: Math.max(0, cmsCosts?.monthly_premium || 0),
      copay_primary: Math.max(0, cmsCosts?.copay_pcp || 0),
      copay_specialist: Math.max(0, cmsCosts?.copay_specialist || 0),
      copay_emergency: Math.max(0, cmsCosts?.copay_emergency || 0),
      deductible: Math.max(0, cmsCosts?.deductible || 0)
    };
  }
}
```

### eMedNY Transformer

```javascript
class EMedNYTransformer extends BaseTransformer {
  constructor() {
    super('EMEDNY_PORTAL');
  }

  async transform(emednyPlans) {
    try {
      const torqePlans = emednyPlans.map(plan => ({
        name: plan.plan_name?.trim(),
        type: this.parseType(plan.plan_type),
        state: 'NY',
        eligibility_criteria: this.parseEligibility(plan),
        benefits: this.parseBenefits(plan.benefits_html),
        cost_sharing: this.parseCosts(plan.cost_section),
        network_type: this.parseNetworkType(plan.network_type),
        provider_directory_url: plan.directory_link,
        coverage_start_date: this.parseDate(plan.start_date),
        coverage_end_date: this.parseDate(plan.end_date) || null,
        contact_info: {
          phone: plan.phone_number?.trim(),
          website: plan.plan_website?.trim(),
          support_hours: plan.support_hours || 'N/A'
        },
        enrollment_deadline: this.parseDate(plan.enrollment_deadline),
        status: plan.is_available ? 'ACTIVE' : 'CLOSED'
      }));

      await this.logTransformation(emednyPlans, torqePlans, true);
      return torqePlans;
    } catch (error) {
      await this.logTransformation(emednyPlans, null, false, error);
      throw error;
    }
  }

  parseType(planTypeStr) {
    const typeMap = {
      'managed care': 'MANAGED_CARE',
      'hmo': 'MANAGED_CARE',
      'ppo': 'MANAGED_CARE',
      'special needs': 'SPECIAL_NEEDS',
      'dual eligible': 'DUAL_ELIGIBLE',
      'medicaid': 'MEDICAID'
    };
    return typeMap[planTypeStr?.toLowerCase()] || 'MEDICAID';
  }

  parseEligibility(plan) {
    // Parse eligibility from HTML text
    return {
      age_min: 0,
      age_max: 120,
      income_limit: this.extractIncomeLimitFromText(plan.eligibility_text),
      citizenship_required: plan.eligibility_text?.includes('citizen') || true,
      disability_status_required: plan.eligibility_text?.includes('disability') || false,
      special_conditions: []
    };
  }

  parseBenefits(benefitsHtml) {
    // Parse benefits from HTML
    const benefits = {
      primary_care: benefitsHtml?.includes('primary care') || false,
      specialist_visits: benefitsHtml?.includes('specialist') || false,
      emergency: benefitsHtml?.includes('emergency') || false,
      hospitalization: benefitsHtml?.includes('hospital') || false,
      pharmacy: benefitsHtml?.includes('pharmacy') || false,
      mental_health: benefitsHtml?.includes('mental health') || false,
      dental: benefitsHtml?.includes('dental') || false,
      vision: benefitsHtml?.includes('vision') || false,
      long_term_care: benefitsHtml?.includes('long-term') || false,
      custom_benefits: []
    };
    return benefits;
  }

  parseCosts(costHtml) {
    // Parse costs from HTML
    const premiumMatch = costHtml?.match(/premium.*?\$(\d+)/i);
    const copayMatch = costHtml?.match(/copay.*?\$(\d+)/i);
    
    return {
      member_premium_monthly: premiumMatch ? parseInt(premiumMatch[1]) : 0,
      copay_primary: copayMatch ? parseInt(copayMatch[1]) : 0,
      copay_specialist: 25,
      copay_emergency: 0,
      deductible: 0
    };
  }

  parseNetworkType(networkStr) {
    const netMap = {
      'hmo': 'HMO',
      'ppo': 'PPO',
      'ffs': 'FFS',
      'fee for service': 'FFS'
    };
    return netMap[networkStr?.toLowerCase()] || 'HMO';
  }

  parseDate(dateStr) {
    if (!dateStr) return null;
    try {
      return new Date(dateStr).toISOString().split('T')[0];
    } catch {
      return null;
    }
  }

  extractIncomeLimitFromText(text) {
    const match = text?.match(/\$?([\d,]+)/);
    return match ? parseInt(match[1].replace(/,/g, '')) : 250000;
  }
}
```

---

## Validators: Check Data Quality

```javascript
class ProgramValidator {
  constructor() {
    this.schema = joi.object({
      name: joi.string().required().max(255),
      type: joi.string().valid('MEDICAID', 'MANAGED_CARE', 'SPECIAL_NEEDS', 'DUAL_ELIGIBLE').required(),
      state: joi.string().length(2).uppercase().required(),
      eligibility_criteria: joi.object({
        age_min: joi.number().integer().min(0).max(120).required(),
        age_max: joi.number().integer().min(0).max(120).required(),
        income_limit: joi.number().positive().required(),
        citizenship_required: joi.boolean().required(),
        disability_status_required: joi.boolean().required(),
        special_conditions: joi.array().items(joi.string())
      }).required(),
      benefits: joi.object({
        primary_care: joi.boolean(),
        specialist_visits: joi.boolean(),
        emergency: joi.boolean(),
        hospitalization: joi.boolean(),
        pharmacy: joi.boolean(),
        mental_health: joi.boolean(),
        dental: joi.boolean(),
        vision: joi.boolean(),
        long_term_care: joi.boolean(),
        custom_benefits: joi.array().items(joi.string())
      }).required(),
      cost_sharing: joi.object({
        member_premium_monthly: joi.number().min(0).required(),
        copay_primary: joi.number().min(0).required(),
        copay_specialist: joi.number().min(0).required(),
        copay_emergency: joi.number().min(0).required(),
        deductible: joi.number().min(0).required()
      }).required(),
      network_type: joi.string().valid('HMO', 'PPO', 'FFS', 'CAPITATED').required(),
      provider_directory_url: joi.string().uri().allow(null),
      coverage_start_date: joi.date().required(),
      coverage_end_date: joi.date().allow(null),
      contact_info: joi.object({
        phone: joi.string().allow(null),
        website: joi.string().uri().allow(null),
        support_hours: joi.string().allow(null)
      }),
      enrollment_deadline: joi.date().allow(null),
      status: joi.string().valid('ACTIVE', 'PENDING', 'CLOSED', 'ARCHIVED').required()
    });
  }

  validate(program) {
    const { error, value } = this.schema.validate(program, { abortEarly: false });
    
    if (error) {
      return {
        valid: false,
        errors: error.details.map(d => ({
          field: d.path.join('.'),
          message: d.message,
          type: d.type
        }))
      };
    }

    // Additional business logic validation
    if (value.eligibility_criteria.age_min >= value.eligibility_criteria.age_max) {
      return {
        valid: false,
        errors: [{ field: 'eligibility_criteria', message: 'age_min must be less than age_max', type: 'business_rule' }]
      };
    }

    if (value.coverage_end_date && value.coverage_start_date > value.coverage_end_date) {
      return {
        valid: false,
        errors: [{ field: 'coverage_dates', message: 'start_date must be before end_date', type: 'business_rule' }]
      };
    }

    return { valid: true, errors: [] };
  }

  async validateBatch(programs) {
    const results = {
      total: programs.length,
      valid: 0,
      invalid: 0,
      errors: []
    };

    for (const program of programs) {
      const result = this.validate(program);
      if (result.valid) {
        results.valid++;
      } else {
        results.invalid++;
        results.errors.push({
          program: program.name,
          validationErrors: result.errors
        });
      }
    }

    return results;
  }
}
```

---

## Loaders: Insert into Database

```javascript
class PostgreSQLLoader {
  constructor(dbPool) {
    this.db = dbPool;
  }

  async loadPrograms(transformedPrograms, sourceMetadata) {
    const validatedPrograms = await this.validateBatch(transformedPrograms);
    
    if (validatedPrograms.invalid > 0) {
      throw new Error(`Validation failed: ${validatedPrograms.invalid} programs invalid`);
    }

    const results = {
      inserted: 0,
      updated: 0,
      archived: 0,
      errors: []
    };

    for (const program of validatedPrograms.valid) {
      try {
        // Check if program already exists (by name + state)
        const existing = await this.db.query(
          'SELECT id FROM programs WHERE name = $1 AND state = $2',
          [program.name, program.state]
        );

        if (existing.rows.length > 0) {
          // Update existing program
          await this.db.query(
            `UPDATE programs SET
              type = $1, eligibility_criteria = $2, benefits = $3,
              cost_sharing = $4, network_type = $5, provider_directory_url = $6,
              coverage_start_date = $7, coverage_end_date = $8,
              contact_info = $9, enrollment_deadline = $10, status = $11,
              updated_at = NOW()
            WHERE id = $12`,
            [
              program.type, JSON.stringify(program.eligibility_criteria),
              JSON.stringify(program.benefits), JSON.stringify(program.cost_sharing),
              program.network_type, program.provider_directory_url,
              program.coverage_start_date, program.coverage_end_date,
              JSON.stringify(program.contact_info), program.enrollment_deadline,
              program.status, existing.rows[0].id
            ]
          );
          results.updated++;
        } else {
          // Insert new program
          await this.db.query(
            `INSERT INTO programs
            (name, type, state, eligibility_criteria, benefits, cost_sharing,
             network_type, provider_directory_url, coverage_start_date,
             coverage_end_date, contact_info, enrollment_deadline, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)`,
            [
              program.name, program.type, program.state,
              JSON.stringify(program.eligibility_criteria),
              JSON.stringify(program.benefits),
              JSON.stringify(program.cost_sharing),
              program.network_type, program.provider_directory_url,
              program.coverage_start_date, program.coverage_end_date,
              JSON.stringify(program.contact_info),
              program.enrollment_deadline, program.status
            ]
          );
          results.inserted++;
        }

        // Log to audit trail
        await AuditLogger.log({
          timestamp: new Date().toISOString(),
          action: 'PROGRAM_LOADED',
          program_name: program.name,
          state: program.state,
          source: sourceMetadata.source,
          operation: existing.rows.length > 0 ? 'UPDATE' : 'INSERT'
        });

      } catch (error) {
        results.errors.push({
          program: program.name,
          error: error.message
        });
      }
    }

    return results;
  }

  async archiveOldPrograms(cutoffDate) {
    // Archive programs no longer available
    const result = await this.db.query(
      'UPDATE programs SET status = $1, updated_at = NOW() WHERE coverage_end_date < $2 AND status = $3',
      ['ARCHIVED', cutoffDate, 'ACTIVE']
    );

    await AuditLogger.log({
      timestamp: new Date().toISOString(),
      action: 'PROGRAMS_ARCHIVED',
      count: result.rowCount,
      cutoff_date: cutoffDate
    });

    return result.rowCount;
  }

  async deduplicatePrograms() {
    // Find duplicates (same name + state, keep most recent)
    const duplicates = await this.db.query(
      `SELECT name, state, COUNT(*) as cnt FROM programs
       GROUP BY name, state HAVING COUNT(*) > 1`
    );

    let deduplicatedCount = 0;

    for (const dup of duplicates.rows) {
      const toDelete = await this.db.query(
        `SELECT id FROM programs WHERE name = $1 AND state = $2
         ORDER BY updated_at DESC OFFSET 1`,
        [dup.name, dup.state]
      );

      for (const prog of toDelete.rows) {
        await this.db.query('DELETE FROM programs WHERE id = $1', [prog.id]);
        deduplicatedCount++;
      }
    }

    return deduplicatedCount;
  }
}
```

---

## Orchestrator: Coordinate ETL

```javascript
class PipelineOrchestrator {
  constructor(config) {
    this.config = config;
    this.extractors = [];
    this.transformers = [];
    this.loaders = [];
  }

  async runPipeline() {
    const pipelineStart = new Date();
    const results = {
      startTime: pipelineStart,
      stages: [],
      totalSuccess: false,
      errors: []
    };

    try {
      // STAGE 1: Extract
      results.stages.push(await this.extractStage());

      // STAGE 2: Transform
      results.stages.push(await this.transformStage(results.stages[0].data));

      // STAGE 3: Validate
      results.stages.push(await this.validateStage(results.stages[1].data));

      // STAGE 4: Deduplicate
      results.stages.push(await this.deduplicateStage(results.stages[2].data));

      // STAGE 5: Load
      results.stages.push(await this.loadStage(results.stages[3].data));

      // STAGE 6: Verify
      results.stages.push(await this.verifyStage());

      results.totalSuccess = true;
      results.endTime = new Date();
      results.duration = results.endTime - pipelineStart;

    } catch (error) {
      results.totalSuccess = false;
      results.errors.push({
        stage: error.stage,
        message: error.message,
        timestamp: new Date().toISOString()
      });
    }

    await this.logPipelineCompletion(results);
    return results;
  }

  async extractStage() {
    const data = [];
    const errors = [];

    for (const extractor of this.extractors) {
      try {
        const extracted = await extractor.extract();
        data.push({
          source: extractor.sourceName,
          records: extracted
        });
      } catch (error) {
        errors.push({
          extractor: extractor.sourceName,
          error: error.message
        });
      }
    }

    return { stage: 'EXTRACT', success: errors.length === 0, data, errors };
  }

  async transformStage(extractedData) {
    const data = [];
    const errors = [];

    for (const extracted of extractedData) {
      const transformer = this.transformers.find(t => t.sourceFormat === extracted.source);
      if (!transformer) {
        errors.push({ source: extracted.source, error: 'No transformer found' });
        continue;
      }

      try {
        const transformed = await transformer.transform(extracted.records);
        data.push({
          source: extracted.source,
          records: transformed
        });
      } catch (error) {
        errors.push({
          source: extracted.source,
          error: error.message
        });
      }
    }

    return { stage: 'TRANSFORM', success: errors.length === 0, data, errors };
  }

  async validateStage(transformedData) {
    const validator = new ProgramValidator();
    const validData = [];
    const invalidData = [];

    for (const transformed of transformedData) {
      const result = await validator.validateBatch(transformed.records);
      validData.push({
        source: transformed.source,
        valid: result.valid,
        records: transformed.records.filter((_, i) => !result.errors.some(e => e.index === i))
      });
      invalidData.push(...result.errors);
    }

    return {
      stage: 'VALIDATE',
      success: invalidData.length === 0,
      data: validData,
      errors: invalidData,
      summary: { valid: validData.reduce((sum, v) => sum + v.valid, 0), invalid: invalidData.length }
    };
  }

  async deduplicateStage(validatedData) {
    // Merge all sources, deduplicate by name + state
    const allPrograms = [];
    for (const validated of validatedData) {
      allPrograms.push(...validated.records);
    }

    const deduped = [];
    const seen = new Map();

    for (const program of allPrograms) {
      const key = `${program.name}|${program.state}`;
      if (!seen.has(key)) {
        deduped.push(program);
        seen.set(key, program);
      } else {
        // Keep most recent (by updated_at or source priority)
        if (program.updated_at > seen.get(key).updated_at) {
          deduped[deduped.indexOf(seen.get(key))] = program;
          seen.set(key, program);
        }
      }
    }

    return {
      stage: 'DEDUPLICATE',
      success: true,
      data: deduped,
      summary: { original: allPrograms.length, deduplicated: deduped.length, removed: allPrograms.length - deduped.length }
    };
  }

  async loadStage(deduplicatedData) {
    const loader = new PostgreSQLLoader(this.dbPool);
    const results = await loader.loadPrograms(deduplicatedData, {
      source: 'PIPELINE',
      timestamp: new Date().toISOString()
    });

    return {
      stage: 'LOAD',
      success: results.errors.length === 0,
      data: results,
      summary: { inserted: results.inserted, updated: results.updated, archived: results.archived, errors: results.errors.length }
    };
  }

  async verifyStage() {
    // Verify data was loaded correctly
    const count = await this.dbPool.query('SELECT COUNT(*) as cnt FROM programs WHERE status = $1', ['ACTIVE']);
    const totalPrograms = count.rows[0].cnt;

    return {
      stage: 'VERIFY',
      success: totalPrograms > 0,
      data: { total_programs: totalPrograms },
      summary: { programs_in_database: totalPrograms }
    };
  }

  async logPipelineCompletion(results) {
    await AuditLogger.log({
      timestamp: new Date().toISOString(),
      action: 'PIPELINE_COMPLETED',
      success: results.totalSuccess,
      duration_ms: results.duration,
      stages: results.stages.map(s => ({ stage: s.stage, success: s.success })),
      summary: {
        inserted: results.stages[4]?.data?.inserted || 0,
        updated: results.stages[4]?.data?.updated || 0,
        archived: results.stages[4]?.data?.archived || 0,
        errors: results.errors.length
      }
    });
  }
}
```

---

## Scheduler: Run Daily

```javascript
class IngestionScheduler {
  constructor(config) {
    this.config = config;
    this.orchestrator = new PipelineOrchestrator(config);
  }

  scheduleDaily() {
    // Run every day at 2 AM ET
    cron.schedule('0 2 * * *', async () => {
      console.log('[Scheduler] Starting daily ingestion pipeline...');
      try {
        const results = await this.orchestrator.runPipeline();
        console.log('[Scheduler] Pipeline completed:', results);
      } catch (error) {
        console.error('[Scheduler] Pipeline failed:', error);
        await this.alertOnFailure(error);
      }
    });

    console.log('[Scheduler] Daily ingestion scheduled for 2 AM ET');
  }

  async alertOnFailure(error) {
    // Send alert (email, Slack, etc.)
    await NotificationService.alert({
      subject: 'Data Ingestion Pipeline Failed',
      message: error.message,
      severity: 'HIGH'
    });
  }
}
```

---

## Immutable Audit Logger

```javascript
class AuditLogger {
  static async log(entry) {
    const logEntry = {
      id: generateUUID(),
      timestamp: entry.timestamp || new Date().toISOString(),
      action: entry.action,
      ...entry,
      hash: hashEntry(entry)  // Prevent tampering
    };

    // Write to immutable append-only log
    await db.query(
      `INSERT INTO data_ingestion_audit_log
      (id, timestamp, action, entry_json, hash)
      VALUES ($1, $2, $3, $4, $5)`,
      [logEntry.id, logEntry.timestamp, logEntry.action, JSON.stringify(logEntry), logEntry.hash]
    );

    return logEntry.id;
  }

  static async getLog(filters = {}) {
    // Query immutable log
    let query = 'SELECT * FROM data_ingestion_audit_log WHERE 1=1';
    const params = [];

    if (filters.action) {
      query += ' AND action = $' + (params.length + 1);
      params.push(filters.action);
    }

    if (filters.startDate) {
      query += ' AND timestamp >= $' + (params.length + 1);
      params.push(filters.startDate);
    }

    if (filters.endDate) {
      query += ' AND timestamp <= $' + (params.length + 1);
      params.push(filters.endDate);
    }

    query += ' ORDER BY timestamp DESC';

    const result = await db.query(query, params);
    return result.rows;
  }
}
```

---

End of Data Ingestion Implementation (DR)
