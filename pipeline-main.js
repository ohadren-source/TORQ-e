/**
 * TORQ-E Data Ingestion Pipeline - Main Entry Point
 *
 * Usage:
 *   node pipeline-main.js --run-once          (Run pipeline one time)
 *   node pipeline-main.js --schedule          (Schedule daily at 2 AM)
 *   node pipeline-main.js --health-check      (Verify system health)
 *   node pipeline-main.js --audit-report      (Generate compliance report)
 *
 * Environment Variables:
 *   DATABASE_URL      - PostgreSQL connection string
 *   CMS_API_KEY       - CMS API key (get at https://api.cms.gov/)
 *   NODE_ENV          - production/development
 */

require('dotenv').config();

const { Pool } = require('pg');
const PipelineOrchestrator = require('./pipeline-orchestrator');
const AuditLogger = require('./audit-logger');

// Configuration
const config = {
  database: {
    connectionString: process.env.DATABASE_URL || 'postgresql://localhost/torq_e_card3'
  },
  cms: {
    apiKey: process.env.CMS_API_KEY
  },
  pipeline: {
    scheduleTime: process.env.SCHEDULE_TIME || '0 2 * * *' // 2 AM daily
  }
};

// Validate configuration
function validateConfig() {
  if (!config.cms.apiKey) {
    console.warn('[Config] WARNING: CMS_API_KEY not set. CMS extraction will fail.');
  }
  console.log('[Config] Configuration loaded');
}

/**
 * Initialize database connection
 */
async function initializeDatabase() {
  console.log('[Database] Connecting to PostgreSQL...');

  const pool = new Pool({
    connectionString: config.database.connectionString,
    max: 10,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000
  });

  try {
    const client = await pool.connect();
    console.log('[Database] Connected successfully');
    client.release();
    return pool;
  } catch (error) {
    console.error('[Database] Connection failed:', error.message);
    process.exit(1);
  }
}

/**
 * Run pipeline once (command-line execution)
 */
async function runOnce(pool) {
  console.log('[Main] Running pipeline once...\n');

  try {
    const orchestrator = new PipelineOrchestrator(pool, config);
    const results = await orchestrator.runPipeline();

    console.log('\n[Main] Pipeline execution complete');
    console.log(`[Main] Status: ${results.totalSuccess ? 'SUCCESS' : 'FAILED'}`);
    console.log(`[Main] Duration: ${(results.duration / 1000).toFixed(2)}s`);

    if (results.totalSuccess) {
      console.log(`[Main] Loaded: ${results.summary.totalLoaded} programs`);
      process.exit(0);
    } else {
      console.log('[Main] Errors encountered:', results.errors);
      process.exit(1);
    }

  } catch (error) {
    console.error('[Main] Pipeline execution failed:', error.message);
    process.exit(1);
  }
}

/**
 * Schedule daily pipeline execution
 */
async function scheduleDaily(pool) {
  console.log('[Main] Starting pipeline scheduler...');

  const orchestrator = new PipelineOrchestrator(pool, config);
  orchestrator.scheduleDaily(config.pipeline.scheduleTime);

  console.log('[Main] Pipeline will run daily at:', config.pipeline.scheduleTime);
  console.log('[Main] (Schedule format: minute hour day month dayofweek)');
  console.log('[Main] Scheduler is now running. Press Ctrl+C to stop.\n');

  // Keep process alive
  process.on('SIGINT', () => {
    console.log('[Main] Scheduler stopped');
    process.exit(0);
  });
}

/**
 * Run health checks
 */
async function healthCheck(pool) {
  console.log('[Health] Running system health checks...\n');

  try {
    // Database health
    console.log('[Health] Checking database...');
    const dbClient = await pool.connect();
    const dbHealth = await dbClient.query('SELECT 1');
    dbClient.release();
    console.log('[Health] Database: ✓ OK\n');

    // Audit log health
    console.log('[Health] Checking audit log...');
    const auditLogger = new AuditLogger(pool);
    const integrity = await auditLogger.verifyIntegrity();
    console.log(`[Health] Audit log: ${integrity.integrityOK ? '✓ OK' : '✗ ISSUES'}`);
    console.log(`[Health]   Total entries: ${integrity.totalEntries}`);
    console.log(`[Health]   Valid entries: ${integrity.validEntries}`);
    console.log(`[Health]   Invalid entries: ${integrity.invalidEntries}\n`);

    // CMS API health
    console.log('[Health] Checking CMS API access...');
    if (!config.cms.apiKey) {
      console.log('[Health] CMS API: ⚠ No API key configured');
    } else {
      console.log('[Health] CMS API: ✓ Key configured');
    }

    console.log('\n[Health] Health check complete');
    process.exit(0);

  } catch (error) {
    console.error('[Health] Health check failed:', error.message);
    process.exit(1);
  }
}

/**
 * Generate compliance report
 */
async function generateComplianceReport(pool) {
  console.log('[Report] Generating compliance report...\n');

  try {
    const auditLogger = new AuditLogger(pool);

    // Last 30 days
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 30 * 24 * 60 * 60 * 1000);

    console.log(`[Report] Period: ${startDate.toISOString().split('T')[0]} to ${endDate.toISOString().split('T')[0]}`);

    const report = await auditLogger.generateComplianceReport(
      startDate.toISOString(),
      endDate.toISOString()
    );

    console.log('\n[Report] Activity Summary:');
    for (const row of report.summary) {
      console.log(`  ${row.action}: ${row.count} events (${row.days} days)`);
    }

    console.log('\n[Report] Audit Trail Integrity:');
    console.log(`  Total entries: ${report.integrity.totalEntries}`);
    console.log(`  Valid entries: ${report.integrity.validEntries}`);
    console.log(`  Invalid entries: ${report.integrity.invalidEntries}`);
    console.log(`  Integrity status: ${report.integrity.integrityOK ? '✓ OK' : '✗ COMPROMISED'}`);

    console.log('\n[Report] Report complete');
    process.exit(0);

  } catch (error) {
    console.error('[Report] Report generation failed:', error.message);
    process.exit(1);
  }
}

/**
 * Main entry point
 */
async function main() {
  console.log(`\n${'='.repeat(80)}`);
  console.log('TORQ-E Data Ingestion Pipeline');
  console.log(`Started: ${new Date().toISOString()}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`${'='.repeat(80)}\n`);

  // Validate config
  validateConfig();

  // Parse command-line arguments
  const args = process.argv.slice(2);
  const command = args[0] || '--run-once';

  // Initialize database
  const pool = await initializeDatabase();

  try {
    switch (command) {
      case '--run-once':
        await runOnce(pool);
        break;

      case '--schedule':
        await scheduleDaily(pool);
        break;

      case '--health-check':
        await healthCheck(pool);
        break;

      case '--audit-report':
        await generateComplianceReport(pool);
        break;

      case '--help':
        console.log(`Usage: node pipeline-main.js [command]

Commands:
  --run-once        Run pipeline one time (default)
  --schedule        Schedule daily execution at 2 AM
  --health-check    Run system health checks
  --audit-report    Generate compliance report
  --help            Show this help message

Environment Variables:
  DATABASE_URL      PostgreSQL connection string
  CMS_API_KEY       CMS API key
  SCHEDULE_TIME     Cron format (default: '0 2 * * *' = 2 AM daily)
  NODE_ENV          production or development

Example:
  CMS_API_KEY=xxxxx DATABASE_URL=postgresql://... node pipeline-main.js --schedule
`);
        process.exit(0);
        break;

      default:
        console.error(`Unknown command: ${command}`);
        console.error(`Run with --help for usage information`);
        process.exit(1);
    }

  } catch (error) {
    console.error('[Main] Fatal error:', error.message);
    process.exit(1);

  } finally {
    // Close database connection if not scheduled
    if (command !== '--schedule') {
      await pool.end();
    }
  }
}

// Run
main().catch(error => {
  console.error('[Main] Uncaught error:', error);
  process.exit(1);
});
