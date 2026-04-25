/**
 * Pipeline Orchestrator
 * Coordinates the entire ETL pipeline
 *
 * Workflow:
 * 1. EXTRACT - Pull from all sources
 * 2. TRANSFORM - Convert to unified format
 * 3. VALIDATE - Check quality
 * 4. DEDUPLICATE - Remove duplicates
 * 5. LOAD - Insert into database
 * 6. VERIFY - Confirm success
 * 7. REPORT - Log and report results
 *
 * Runs daily at 2 AM ET via scheduler
 */

const cron = require('node-cron');
const CMSAPIExtractor = require('./cms-api-extractor');
const EMedNYScraper = require('./emedny-scraper');
const DataTransformer = require('./data-transformer');
const ProgramValidator = require('./program-validator');
const PostgreSQLLoader = require('./postgres-loader');
const AuditLogger = require('./audit-logger'); // Immutable logging

class PipelineOrchestrator {
  constructor(dbPool, config = {}) {
    this.dbPool = dbPool;
    this.config = config;
    this.auditLogger = new AuditLogger(dbPool);

    // Initialize components
    this.extractors = {
      cms: new CMSAPIExtractor({ auditLogger: this.auditLogger }),
      emedny: new EMedNYScraper({ auditLogger: this.auditLogger })
    };

    this.transformers = {
      cms: new DataTransformer({ sourceFormat: 'CMS_API', auditLogger: this.auditLogger }),
      emedny: new DataTransformer({ sourceFormat: 'EMEDNY', auditLogger: this.auditLogger })
    };

    this.validator = new ProgramValidator({ auditLogger: this.auditLogger });
    this.loader = new PostgreSQLLoader(dbPool, { auditLogger: this.auditLogger });
  }

  /**
   * Run the complete pipeline
   */
  async runPipeline() {
    const pipelineStart = new Date();
    console.log(`\n${'='.repeat(80)}`);
    console.log(`[Pipeline] Starting ETL pipeline at ${pipelineStart.toISOString()}`);
    console.log(`${'='.repeat(80)}\n`);

    const results = {
      startTime: pipelineStart,
      stages: [],
      summary: {},
      totalSuccess: false,
      errors: []
    };

    try {
      // Pre-flight checks
      console.log('[Pipeline] Running pre-flight checks...');
      const dbHealth = await this.loader.healthCheck();
      if (!dbHealth.healthy) {
        throw new Error('Database health check failed: ' + dbHealth.error);
      }
      console.log('[Pipeline] Database health check passed\n');

      // STAGE 1: Extract
      console.log('[Pipeline] STAGE 1: EXTRACT');
      console.log('-'.repeat(80));
      results.stages.push(await this.extractStage());

      // STAGE 2: Transform
      console.log('\n[Pipeline] STAGE 2: TRANSFORM');
      console.log('-'.repeat(80));
      results.stages.push(await this.transformStage(results.stages[0].data));

      // STAGE 3: Validate
      console.log('\n[Pipeline] STAGE 3: VALIDATE');
      console.log('-'.repeat(80));
      results.stages.push(await this.validateStage(results.stages[1].data));

      // STAGE 4: Deduplicate
      console.log('\n[Pipeline] STAGE 4: DEDUPLICATE');
      console.log('-'.repeat(80));
      results.stages.push(await this.deduplicateStage(results.stages[2].validPrograms));

      // STAGE 5: Load
      console.log('\n[Pipeline] STAGE 5: LOAD');
      console.log('-'.repeat(80));
      results.stages.push(await this.loadStage(results.stages[3].data));

      // STAGE 6: Verify
      console.log('\n[Pipeline] STAGE 6: VERIFY');
      console.log('-'.repeat(80));
      results.stages.push(await this.verifyStage());

      // Calculate summary
      const loadStage = results.stages[4];
      results.summary = {
        inserted: loadStage.data.inserted,
        updated: loadStage.data.updated,
        totalLoaded: loadStage.data.inserted + loadStage.data.updated,
        errors: loadStage.data.errors.length
      };

      results.totalSuccess = true;
      results.endTime = new Date();
      results.duration = results.endTime - pipelineStart;

      console.log('\n[Pipeline] STAGE 7: REPORT');
      console.log('-'.repeat(80));
      await this.reportStage(results);

    } catch (error) {
      console.error(`\n[Pipeline] FATAL ERROR:`, error.message);
      results.totalSuccess = false;
      results.errors.push({
        stage: 'PIPELINE',
        message: error.message,
        timestamp: new Date().toISOString()
      });
      results.endTime = new Date();
      results.duration = results.endTime - pipelineStart;

      await this.handleFailure(results, error);
    }

    return results;
  }

  /**
   * STAGE 1: Extract data from all sources
   */
  async extractStage() {
    const data = [];
    const errors = [];
    const stageStart = new Date();

    // CMS API
    try {
      console.log('[Extract] Pulling from CMS API...');
      const cmsData = await this.extractors.cms.extractMedicaidPlans();
      data.push(cmsData);
      console.log(`[Extract] CMS API: ${cmsData.recordCount} programs`);
    } catch (error) {
      console.error('[Extract] CMS API failed:', error.message);
      errors.push({ source: 'CMS_API', error: error.message });
    }

    // eMedNY
    try {
      console.log('[Extract] Scraping eMedNY portal...');
      const emednyData = await this.extractors.emedny.scrapeAllPlans();
      data.push(emednyData);
      console.log(`[Extract] eMedNY: ${emednyData.recordCount} programs`);
    } catch (error) {
      console.error('[Extract] eMedNY scrape failed:', error.message);
      errors.push({ source: 'EMEDNY', error: error.message });
    }

    const stageDuration = new Date() - stageStart;
    console.log(`[Extract] Complete (${stageDuration}ms, ${errors.length} errors)`);

    return {
      stage: 'EXTRACT',
      success: errors.length === 0,
      data,
      errors,
      duration: stageDuration
    };
  }

  /**
   * STAGE 2: Transform all data to unified format
   */
  async transformStage(extractedData) {
    const data = [];
    const errors = [];
    const stageStart = new Date();

    for (const extracted of extractedData) {
      try {
        console.log(`[Transform] Processing ${extracted.source}...`);
        const transformer = this.transformers[extracted.source.toLowerCase().replace('_', '')];

        if (!transformer) {
          throw new Error(`No transformer found for ${extracted.source}`);
        }

        const transformed = await transformer.transform(extracted.data);
        data.push({
          source: extracted.source,
          records: transformed,
          count: transformed.length
        });
        console.log(`[Transform] ${extracted.source}: Transformed ${transformed.length} programs`);
      } catch (error) {
        console.error(`[Transform] ${extracted.source} failed:`, error.message);
        errors.push({ source: extracted.source, error: error.message });
      }
    }

    const stageDuration = new Date() - stageStart;
    console.log(`[Transform] Complete (${stageDuration}ms, ${errors.length} errors)`);

    return {
      stage: 'TRANSFORM',
      success: errors.length === 0,
      data,
      errors,
      duration: stageDuration
    };
  }

  /**
   * STAGE 3: Validate all data
   */
  async validateStage(transformedData) {
    const stageStart = new Date();
    const allRecords = [];

    // Flatten all records
    for (const transformed of transformedData) {
      allRecords.push(...transformed.records);
    }

    console.log(`[Validate] Validating ${allRecords.length} programs...`);

    const validationResults = await this.validator.validateBatch(allRecords);
    const validPercent = parseFloat(validationResults.summary.validPercent);

    if (validationResults.summary.passed) {
      console.log(`[Validate] PASSED (${validPercent}% valid records)`);
    } else {
      console.warn(`[Validate] WARNING: Only ${validPercent}% valid (target: 99.5%)`);
      console.warn(`[Validate] Invalid: ${validationResults.invalid} records`);
    }

    const stageDuration = new Date() - stageStart;
    console.log(`[Validate] Complete (${stageDuration}ms)`);

    return {
      stage: 'VALIDATE',
      success: validationResults.summary.passed,
      validPrograms: validationResults.validPrograms,
      invalidPrograms: validationResults.invalidPrograms,
      summary: validationResults.summary,
      duration: stageDuration
    };
  }

  /**
   * STAGE 4: Deduplicate programs
   */
  async deduplicateStage(validPrograms) {
    const stageStart = new Date();

    console.log(`[Deduplicate] Deduplicating ${validPrograms.length} programs...`);

    // Group by name + state, keep most recent
    const deduped = [];
    const seen = new Map();

    for (const program of validPrograms) {
      const key = `${program.name}|${program.state}`;

      if (!seen.has(key)) {
        deduped.push(program);
        seen.set(key, program);
      } else {
        const existing = seen.get(key);
        // Compare timestamps (if available) or keep first
        if (program.transformed_at && existing.transformed_at &&
            program.transformed_at > existing.transformed_at) {
          const index = deduped.indexOf(existing);
          deduped[index] = program;
          seen.set(key, program);
        }
      }
    }

    const removed = validPrograms.length - deduped.length;
    console.log(`[Deduplicate] Removed ${removed} duplicates, ${deduped.length} unique programs`);

    const stageDuration = new Date() - stageStart;
    console.log(`[Deduplicate] Complete (${stageDuration}ms)`);

    return {
      stage: 'DEDUPLICATE',
      success: true,
      data: deduped,
      summary: { original: validPrograms.length, unique: deduped.length, removed },
      duration: stageDuration
    };
  }

  /**
   * STAGE 5: Load into database
   */
  async loadStage(deduplicatedPrograms) {
    const stageStart = new Date();

    console.log(`[Load] Loading ${deduplicatedPrograms.length} programs into database...`);

    const loadResults = await this.loader.loadPrograms(deduplicatedPrograms, {
      source: 'PIPELINE',
      timestamp: new Date().toISOString()
    });

    console.log(`[Load] Inserted: ${loadResults.inserted}, Updated: ${loadResults.updated}, Errors: ${loadResults.errors.length}`);

    const stageDuration = new Date() - stageStart;
    console.log(`[Load] Complete (${stageDuration}ms)`);

    return {
      stage: 'LOAD',
      success: loadResults.errors.length === 0,
      data: loadResults,
      duration: stageDuration
    };
  }

  /**
   * STAGE 6: Verify load
   */
  async verifyStage() {
    const stageStart = new Date();

    console.log('[Verify] Verifying load...');

    const verification = await this.loader.verifyLoad();
    const stats = await this.loader.getStats();

    console.log(`[Verify] Database contains: ${stats.totalPrograms} total, ${stats.activePrograms} active`);

    const stageDuration = new Date() - stageStart;
    console.log(`[Verify] Complete (${stageDuration}ms)`);

    return {
      stage: 'VERIFY',
      success: verification.healthy,
      verification,
      stats,
      duration: stageDuration
    };
  }

  /**
   * STAGE 7: Report results
   */
  async reportStage(results) {
    const duration = results.duration;
    const durationSeconds = (duration / 1000).toFixed(2);

    console.log(`\nPipeline Execution Summary:`);
    console.log(`  Status: ${results.totalSuccess ? '✓ SUCCESS' : '✗ FAILED'}`);
    console.log(`  Duration: ${durationSeconds}s`);
    console.log(`  Stages Completed: ${results.stages.filter(s => s.success).length}/${results.stages.length}`);
    console.log(`  Programs Loaded: ${results.summary.totalLoaded} (Inserted: ${results.summary.inserted}, Updated: ${results.summary.updated})`);
    console.log(`  Errors: ${results.summary.errors}`);

    // Log to audit trail
    await this.auditLogger.log({
      timestamp: new Date().toISOString(),
      action: 'PIPELINE_COMPLETED',
      success: results.totalSuccess,
      duration_ms: duration,
      durationSeconds: parseFloat(durationSeconds),
      stages_completed: results.stages.filter(s => s.success).length,
      total_stages: results.stages.length,
      summary: results.summary,
      error_count: results.errors.length
    });

    return {
      stage: 'REPORT',
      success: true,
      summary: {
        overallStatus: results.totalSuccess ? 'SUCCESS' : 'FAILED',
        totalDuration: durationSeconds + 's',
        programsLoaded: results.summary.totalLoaded,
        errors: results.errors.length
      }
    };
  }

  /**
   * Handle pipeline failure
   */
  async handleFailure(results, error) {
    console.error(`\n${'='.repeat(80)}`);
    console.error(`Pipeline FAILED at ${new Date().toISOString()}`);
    console.error(`Duration: ${((results.duration) / 1000).toFixed(2)}s`);
    console.error(`Error: ${error.message}`);
    console.error(`${'='.repeat(80)}\n`);

    // Log failure
    await this.auditLogger.log({
      timestamp: new Date().toISOString(),
      action: 'PIPELINE_FAILED',
      error: error.message,
      duration_ms: results.duration,
      completedStages: results.stages.length
    });

    // Send alert (would call notification service)
    console.warn('[Pipeline] ALERT: Pipeline execution failed. Manual review required.');
  }

  /**
   * Schedule pipeline to run daily
   */
  scheduleDaily(time = '0 2 * * *') { // Default: 2 AM ET daily
    console.log(`[Pipeline] Scheduling daily execution at ${time}...`);

    cron.schedule(time, async () => {
      console.log(`[Pipeline] Scheduled run started at ${new Date().toISOString()}`);
      try {
        await this.runPipeline();
      } catch (error) {
        console.error('[Pipeline] Scheduled run failed:', error.message);
      }
    });

    console.log('[Pipeline] Daily schedule active');
  }

  /**
   * Run pipeline once (for testing)
   */
  async runOnce() {
    return this.runPipeline();
  }
}

module.exports = PipelineOrchestrator;
