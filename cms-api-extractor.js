/**
 * CMS API Extractor
 * Pulls real Medicare/Medicaid plan data from CMS public APIs
 *
 * API Documentation: https://api.cms.gov/
 * Data: Medicare Advantage plans, Medicaid plan comparisons
 * Update frequency: Daily
 *
 * Setup:
 * 1. Get free API key at https://api.cms.gov/
 * 2. Set CMS_API_KEY environment variable
 * 3. Extractor handles retries, timeouts, error logging
 */

const axios = require('axios');
const crypto = require('crypto');

class CMSAPIExtractor {
  constructor(config = {}) {
    this.sourceName = 'CMS_API';
    this.sourceUrl = config.sourceUrl || 'https://api.cms.gov/v1';
    this.apiKey = process.env.CMS_API_KEY;
    this.timeout = config.timeout || 30000;
    this.retryAttempts = config.retryAttempts || 3;
    this.retryDelay = config.retryDelay || 1000; // milliseconds
    this.auditLogger = config.auditLogger;

    if (!this.apiKey) {
      throw new Error('CMS_API_KEY environment variable not set');
    }
  }

  /**
   * Extract Medicare Advantage plan data
   * Real data from CMS, used as baseline for all states
   */
  async extractMedicareAdvantage(state = null) {
    try {
      console.log(`[CMS Extractor] Fetching Medicare Advantage plans${state ? ` for ${state}` : ''}...`);

      const endpoint = `${this.sourceUrl}/medicareadvantage/plans`;
      const params = {};
      if (state) params.state = state;

      const plans = await this.retryWithBackoff(() =>
        axios.get(endpoint, {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Accept': 'application/json',
            'User-Agent': 'TORQ-E-Data-Ingestion/1.0'
          },
          params,
          timeout: this.timeout
        })
      );

      console.log(`[CMS Extractor] Successfully fetched ${plans.data.length || 0} Medicare Advantage plans`);

      await this.logExtraction('MEDICARE_ADVANTAGE', plans.data, true);
      return {
        source: this.sourceName,
        dataType: 'MEDICARE_ADVANTAGE',
        timestamp: new Date().toISOString(),
        recordCount: plans.data.length,
        data: plans.data
      };

    } catch (error) {
      console.error(`[CMS Extractor] Medicare Advantage extraction failed:`, error.message);
      await this.logExtraction('MEDICARE_ADVANTAGE', null, false, error);
      throw error;
    }
  }

  /**
   * Extract Medicaid state plan information
   * CMS publishes comparative data across states
   */
  async extractMedicaidPlans(state = null) {
    try {
      console.log(`[CMS Extractor] Fetching Medicaid plans${state ? ` for ${state}` : ''}...`);

      const endpoint = `${this.sourceUrl}/medicaid/plans`;
      const params = {};
      if (state) params.state = state;

      const plans = await this.retryWithBackoff(() =>
        axios.get(endpoint, {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Accept': 'application/json',
            'User-Agent': 'TORQ-E-Data-Ingestion/1.0'
          },
          params,
          timeout: this.timeout
        })
      );

      console.log(`[CMS Extractor] Successfully fetched ${plans.data.length || 0} Medicaid plans`);

      await this.logExtraction('MEDICAID', plans.data, true);
      return {
        source: this.sourceName,
        dataType: 'MEDICAID',
        timestamp: new Date().toISOString(),
        recordCount: plans.data.length,
        data: plans.data
      };

    } catch (error) {
      console.error(`[CMS Extractor] Medicaid extraction failed:`, error.message);
      await this.logExtraction('MEDICAID', null, false, error);
      throw error;
    }
  }

  /**
   * Extract plan benefits data
   * Detailed benefits matrix for each plan
   */
  async extractPlanBenefits(planId) {
    try {
      console.log(`[CMS Extractor] Fetching benefits for plan ${planId}...`);

      const endpoint = `${this.sourceUrl}/plans/${planId}/benefits`;

      const benefits = await this.retryWithBackoff(() =>
        axios.get(endpoint, {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Accept': 'application/json',
            'User-Agent': 'TORQ-E-Data-Ingestion/1.0'
          },
          timeout: this.timeout
        })
      );

      console.log(`[CMS Extractor] Successfully fetched benefits for plan ${planId}`);

      await this.logExtraction('PLAN_BENEFITS', benefits.data, true);
      return {
        source: this.sourceName,
        dataType: 'PLAN_BENEFITS',
        planId,
        timestamp: new Date().toISOString(),
        data: benefits.data
      };

    } catch (error) {
      console.error(`[CMS Extractor] Benefits extraction failed for plan ${planId}:`, error.message);
      await this.logExtraction('PLAN_BENEFITS', null, false, error);
      throw error;
    }
  }

  /**
   * Extract provider network data
   * Which providers are in-network for each plan
   */
  async extractProviderNetwork(planId) {
    try {
      console.log(`[CMS Extractor] Fetching provider network for plan ${planId}...`);

      const endpoint = `${this.sourceUrl}/plans/${planId}/providers`;

      const network = await this.retryWithBackoff(() =>
        axios.get(endpoint, {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Accept': 'application/json',
            'User-Agent': 'TORQ-E-Data-Ingestion/1.0'
          },
          params: { limit: 1000 },
          timeout: this.timeout
        })
      );

      console.log(`[CMS Extractor] Successfully fetched provider network for plan ${planId}`);

      await this.logExtraction('PROVIDER_NETWORK', network.data, true);
      return {
        source: this.sourceName,
        dataType: 'PROVIDER_NETWORK',
        planId,
        timestamp: new Date().toISOString(),
        providerCount: network.data.length,
        data: network.data
      };

    } catch (error) {
      console.error(`[CMS Extractor] Provider network extraction failed for plan ${planId}:`, error.message);
      await this.logExtraction('PROVIDER_NETWORK', null, false, error);
      throw error;
    }
  }

  /**
   * Extract all data for a specific state
   * Comprehensive extraction: plans + benefits + networks
   */
  async extractAllForState(state) {
    try {
      console.log(`[CMS Extractor] Starting comprehensive extraction for ${state}...`);

      const results = {
        state,
        timestamp: new Date().toISOString(),
        results: [],
        errors: []
      };

      // Get plans
      let medicaidResult;
      try {
        medicaidResult = await this.extractMedicaidPlans(state);
        results.results.push({
          type: 'MEDICAID_PLANS',
          success: true,
          recordCount: medicaidResult.recordCount
        });
      } catch (error) {
        results.errors.push({
          type: 'MEDICAID_PLANS',
          error: error.message
        });
      }

      // For each plan, get benefits and network
      if (medicaidResult && medicaidResult.data) {
        for (const plan of medicaidResult.data.slice(0, 10)) { // Limit to first 10 to avoid API rate limits
          try {
            await this.extractPlanBenefits(plan.plan_id);
            results.results.push({
              type: 'PLAN_BENEFITS',
              planId: plan.plan_id,
              success: true
            });
          } catch (error) {
            results.errors.push({
              type: 'PLAN_BENEFITS',
              planId: plan.plan_id,
              error: error.message
            });
          }

          try {
            await this.extractProviderNetwork(plan.plan_id);
            results.results.push({
              type: 'PROVIDER_NETWORK',
              planId: plan.plan_id,
              success: true
            });
          } catch (error) {
            results.errors.push({
              type: 'PROVIDER_NETWORK',
              planId: plan.plan_id,
              error: error.message
            });
          }
        }
      }

      console.log(`[CMS Extractor] Comprehensive extraction complete for ${state}`);
      return results;

    } catch (error) {
      console.error(`[CMS Extractor] Comprehensive extraction failed for ${state}:`, error.message);
      throw error;
    }
  }

  /**
   * Retry logic with exponential backoff
   * Handles transient API failures gracefully
   */
  async retryWithBackoff(fn, attempt = 0) {
    try {
      return await fn();
    } catch (error) {
      // Don't retry on client errors (4xx)
      if (error.response && error.response.status >= 400 && error.response.status < 500) {
        throw error;
      }

      // Retry on server errors (5xx) or network errors
      if (attempt < this.retryAttempts) {
        const delay = Math.pow(2, attempt) * this.retryDelay; // 1s, 2s, 4s, 8s, ...
        console.log(`[CMS Extractor] Retry ${attempt + 1}/${this.retryAttempts} after ${delay}ms...`);

        await new Promise(resolve => setTimeout(resolve, delay));
        return this.retryWithBackoff(fn, attempt + 1);
      }

      // All retries exhausted
      throw error;
    }
  }

  /**
   * Log extraction event to immutable audit trail
   */
  async logExtraction(dataType, rawData, success, error = null) {
    if (!this.auditLogger) {
      console.warn('[CMS Extractor] No audit logger configured, skipping log');
      return;
    }

    const logEntry = {
      timestamp: new Date().toISOString(),
      action: 'DATA_EXTRACTED',
      source: this.sourceName,
      dataType,
      recordCount: rawData ? (Array.isArray(rawData) ? rawData.length : 1) : 0,
      success,
      error: error ? error.message : null,
      rawDataHash: rawData ? this.hashData(rawData) : null
    };

    try {
      await this.auditLogger.log(logEntry);
    } catch (logError) {
      console.error('[CMS Extractor] Failed to log extraction:', logError.message);
    }
  }

  /**
   * Hash data for immutable logging
   * Allows verification that data wasn't tampered with
   */
  hashData(data) {
    const jsonString = typeof data === 'string' ? data : JSON.stringify(data);
    return crypto.createHash('sha256').update(jsonString).digest('hex');
  }

  /**
   * Health check - verify API connectivity
   */
  async healthCheck() {
    try {
      console.log('[CMS Extractor] Running health check...');

      const health = await axios.get(`${this.sourceUrl}/health`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        },
        timeout: 5000
      });

      console.log('[CMS Extractor] Health check passed');
      return { healthy: true, timestamp: new Date().toISOString() };

    } catch (error) {
      console.error('[CMS Extractor] Health check failed:', error.message);
      return { healthy: false, error: error.message, timestamp: new Date().toISOString() };
    }
  }
}

module.exports = CMSAPIExtractor;
