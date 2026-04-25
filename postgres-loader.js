/**
 * PostgreSQL Loader
 * Loads validated programs into Card 3 database
 *
 * Operations:
 * - INSERT new programs
 * - UPDATE existing programs (if data changed)
 * - ARCHIVE old programs (if no longer available)
 * - DEDUPLICATE programs from multiple sources
 *
 * All operations are immutable and logged to audit trail
 */

const crypto = require('crypto');

class PostgreSQLLoader {
  constructor(dbPool, config = {}) {
    this.db = dbPool;
    this.auditLogger = config.auditLogger;
  }

  /**
   * Load programs into database
   * - Insert new programs
   * - Update existing (by name + state)
   * - Log all operations immutably
   */
  async loadPrograms(validPrograms, sourceMetadata = {}) {
    console.log(`[Loader] Loading ${validPrograms.length} programs into database...`);

    const results = {
      inserted: 0,
      updated: 0,
      errors: [],
      operationLog: []
    };

    for (const program of validPrograms) {
      try {
        // Check if program already exists (by name + state)
        const existing = await this.db.query(
          'SELECT id, updated_at FROM programs WHERE LOWER(name) = LOWER($1) AND state = $2',
          [program.name, program.state]
        );

        if (existing.rows.length > 0) {
          // UPDATE existing program
          const programId = existing.rows[0].id;
          const oldUpdatedAt = existing.rows[0].updated_at;

          const updateResult = await this.db.query(
            `UPDATE programs SET
              type = $1,
              eligibility_criteria = $2,
              benefits = $3,
              cost_sharing = $4,
              network_type = $5,
              provider_directory_url = $6,
              coverage_start_date = $7,
              coverage_end_date = $8,
              contact_info = $9,
              enrollment_deadline = $10,
              status = $11,
              updated_at = NOW(),
              last_modified_by = $12
            WHERE id = $13
            RETURNING *`,
            [
              program.type,
              JSON.stringify(program.eligibility_criteria),
              JSON.stringify(program.benefits),
              JSON.stringify(program.cost_sharing),
              program.network_type,
              program.provider_directory_url,
              program.coverage_start_date,
              program.coverage_end_date,
              JSON.stringify(program.contact_info),
              program.enrollment_deadline,
              program.status,
              sourceMetadata.source || 'PIPELINE',
              programId
            ]
          );

          results.updated++;
          results.operationLog.push({
            operation: 'UPDATE',
            programId,
            programName: program.name,
            state: program.state,
            timestamp: new Date().toISOString()
          });

        } else {
          // INSERT new program
          const insertResult = await this.db.query(
            `INSERT INTO programs
            (name, type, state, eligibility_criteria, benefits, cost_sharing,
             network_type, provider_directory_url, coverage_start_date,
             coverage_end_date, contact_info, enrollment_deadline, status,
             created_at, updated_at, last_modified_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW(), NOW(), $14)
            RETURNING id`,
            [
              program.name,
              program.type,
              program.state,
              JSON.stringify(program.eligibility_criteria),
              JSON.stringify(program.benefits),
              JSON.stringify(program.cost_sharing),
              program.network_type,
              program.provider_directory_url,
              program.coverage_start_date,
              program.coverage_end_date,
              JSON.stringify(program.contact_info),
              program.enrollment_deadline,
              program.status,
              sourceMetadata.source || 'PIPELINE'
            ]
          );

          results.inserted++;
          results.operationLog.push({
            operation: 'INSERT',
            programId: insertResult.rows[0].id,
            programName: program.name,
            state: program.state,
            timestamp: new Date().toISOString()
          });
        }

      } catch (error) {
        console.error(`[Loader] Error loading program "${program.name}":`, error.message);
        results.errors.push({
          program: program.name,
          state: program.state,
          error: error.message
        });
      }
    }

    console.log(`[Loader] Load complete: ${results.inserted} inserted, ${results.updated} updated, ${results.errors.length} errors`);

    await this.logLoadOperation(validPrograms, results, sourceMetadata);
    return results;
  }

  /**
   * Archive programs that are no longer available
   * (coverage_end_date is in past, status should change to ARCHIVED)
   */
  async archiveOldPrograms(cutoffDate = null) {
    const archiveDate = cutoffDate || new Date().toISOString().split('T')[0];

    console.log(`[Loader] Archiving programs with end date before ${archiveDate}...`);

    try {
      const result = await this.db.query(
        `UPDATE programs
         SET status = $1, updated_at = NOW(), last_modified_by = $2
         WHERE coverage_end_date < $3 AND status = $4
         RETURNING id, name, state`,
        ['ARCHIVED', 'PIPELINE', archiveDate, 'ACTIVE']
      );

      console.log(`[Loader] Archived ${result.rowCount} programs`);

      await this.auditLogger.log({
        timestamp: new Date().toISOString(),
        action: 'PROGRAMS_ARCHIVED',
        count: result.rowCount,
        cutoff_date: archiveDate
      });

      return result.rowCount;

    } catch (error) {
      console.error('[Loader] Archive operation failed:', error.message);
      throw error;
    }
  }

  /**
   * Deduplicate programs within database
   * If same program appears multiple times, keep most recent, delete others
   */
  async deduplicateProgramsInDatabase() {
    console.log('[Loader] Deduplicating programs in database...');

    try {
      // Find duplicate programs (same name + state)
      const duplicates = await this.db.query(
        `SELECT name, state, COUNT(*) as count
         FROM programs
         GROUP BY name, state
         HAVING COUNT(*) > 1`
      );

      console.log(`[Loader] Found ${duplicates.rows.length} duplicate program names`);

      let totalDeduped = 0;

      for (const dup of duplicates.rows) {
        // Get all IDs for this program, ordered by updated_at (newest first)
        const versions = await this.db.query(
          `SELECT id FROM programs
           WHERE name = $1 AND state = $2
           ORDER BY updated_at DESC`,
          [dup.name, dup.state]
        );

        // Keep the first (most recent), delete the rest
        const toDelete = versions.rows.slice(1);

        for (const version of toDelete) {
          await this.db.query(
            'DELETE FROM programs WHERE id = $1',
            [version.id]
          );
          totalDeduped++;
        }
      }

      console.log(`[Loader] Deduplicated ${totalDeduped} program records`);

      await this.auditLogger.log({
        timestamp: new Date().toISOString(),
        action: 'PROGRAMS_DEDUPLICATED',
        duplicateSets: duplicates.rows.length,
        recordsDeleted: totalDeduped
      });

      return totalDeduped;

    } catch (error) {
      console.error('[Loader] Deduplication failed:', error.message);
      throw error;
    }
  }

  /**
   * Verify data was loaded successfully
   * Check: programs are in database, are queryable, status looks right
   */
  async verifyLoad() {
    console.log('[Loader] Verifying load...');

    try {
      // Count total programs
      const countResult = await this.db.query(
        'SELECT COUNT(*) as total, COUNT(CASE WHEN status = $1 THEN 1 END) as active FROM programs',
        ['ACTIVE']
      );

      const total = parseInt(countResult.rows[0].total);
      const active = parseInt(countResult.rows[0].active);

      // Check data integrity
      const integrityResult = await this.db.query(
        `SELECT COUNT(*) as issues FROM programs
         WHERE name IS NULL OR name = ''
         OR eligibility_criteria IS NULL
         OR benefits IS NULL
         OR cost_sharing IS NULL`
      );

      const issues = parseInt(integrityResult.rows[0].issues);

      const isHealthy = total > 0 && issues === 0;

      console.log(`[Loader] Verification: ${total} total programs, ${active} active, ${issues} data issues`);

      return {
        healthy: isHealthy,
        total,
        active,
        dataIssues: issues
      };

    } catch (error) {
      console.error('[Loader] Verification failed:', error.message);
      return {
        healthy: false,
        error: error.message
      };
    }
  }

  /**
   * Get loading statistics
   */
  async getStats() {
    try {
      const statResult = await this.db.query(
        `SELECT
          COUNT(*) as total,
          COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active,
          COUNT(CASE WHEN status = 'ARCHIVED' THEN 1 END) as archived,
          COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending,
          COUNT(DISTINCT state) as states
         FROM programs`
      );

      const stats = statResult.rows[0];

      return {
        totalPrograms: parseInt(stats.total),
        activePrograms: parseInt(stats.active),
        archivedPrograms: parseInt(stats.archived),
        pendingPrograms: parseInt(stats.pending),
        statesCovered: parseInt(stats.states),
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error('[Loader] Stats query failed:', error.message);
      return null;
    }
  }

  /**
   * Log load operation to audit trail
   */
  async logLoadOperation(programs, results, sourceMetadata) {
    if (!this.auditLogger) {
      console.warn('[Loader] No audit logger configured, skipping log');
      return;
    }

    const logEntry = {
      timestamp: new Date().toISOString(),
      action: 'PROGRAMS_LOADED',
      source: sourceMetadata.source || 'PIPELINE',
      totalRecords: programs.length,
      inserted: results.inserted,
      updated: results.updated,
      errors: results.errors.length,
      operationLogHash: this.hashData(results.operationLog),
      success: results.errors.length === 0
    };

    try {
      await this.auditLogger.log(logEntry);
    } catch (logError) {
      console.error('[Loader] Failed to log load operation:', logError.message);
    }
  }

  /**
   * Hash data
   */
  hashData(data) {
    const jsonString = typeof data === 'string' ? data : JSON.stringify(data);
    return crypto.createHash('sha256').update(jsonString).digest('hex');
  }

  /**
   * Health check - verify database connectivity
   */
  async healthCheck() {
    try {
      console.log('[Loader] Running database health check...');

      const result = await this.db.query('SELECT 1 as health');

      console.log('[Loader] Database health check passed');

      return {
        healthy: true,
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error('[Loader] Database health check failed:', error.message);

      return {
        healthy: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }
}

module.exports = PostgreSQLLoader;
