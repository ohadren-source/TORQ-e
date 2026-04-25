/**
 * Immutable Audit Logger
 * Write-once, append-only logging for data ingestion pipeline
 *
 * Properties:
 * - IMMUTABLE: Once written, cannot be modified or deleted
 * - APPEND-ONLY: New entries only, no updates to existing entries
 * - HASHABLE: Each entry is hashed for integrity verification
 * - QUERYABLE: Can be queried for compliance audits
 *
 * Table: data_ingestion_audit_log
 */

const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');

class AuditLogger {
  constructor(dbPool) {
    this.db = dbPool;
  }

  /**
   * Log an entry (append-only)
   * Returns: entry ID
   */
  async log(entry) {
    try {
      const entryId = uuidv4();
      const timestamp = new Date().toISOString();
      const entryJson = JSON.stringify({
        ...entry,
        entryId,
        timestamp
      });
      const hash = this.hashEntry(entryJson);

      // Insert into immutable append-only log
      const result = await this.db.query(
        `INSERT INTO data_ingestion_audit_log
        (id, timestamp, action, entry_json, hash, created_at)
        VALUES ($1, $2, $3, $4, $5, NOW())
        RETURNING id`,
        [entryId, timestamp, entry.action || 'LOG', entryJson, hash]
      );

      return result.rows[0].id;

    } catch (error) {
      console.error('[AuditLogger] Failed to log entry:', error.message);
      // Don't throw - logging should never break the pipeline
      console.error('[AuditLogger] WARNING: Audit trail may be incomplete');
      return null;
    }
  }

  /**
   * Query audit log (read-only, no modifications allowed)
   */
  async query(filters = {}) {
    try {
      let sql = 'SELECT * FROM data_ingestion_audit_log WHERE 1=1';
      const params = [];

      if (filters.action) {
        sql += ` AND action = $${params.length + 1}`;
        params.push(filters.action);
      }

      if (filters.startDate) {
        sql += ` AND timestamp >= $${params.length + 1}`;
        params.push(filters.startDate);
      }

      if (filters.endDate) {
        sql += ` AND timestamp <= $${params.length + 1}`;
        params.push(filters.endDate);
      }

      if (filters.source) {
        sql += ` AND entry_json @> $${params.length + 1}`;
        params.push(JSON.stringify({ source: filters.source }));
      }

      // Always order by timestamp descending (most recent first)
      sql += ' ORDER BY timestamp DESC';

      // Optional limit
      if (filters.limit) {
        sql += ` LIMIT $${params.length + 1}`;
        params.push(filters.limit);
      }

      const result = await this.db.query(sql, params);

      // Parse entry_json back to objects
      return result.rows.map(row => ({
        ...row,
        entry: JSON.parse(row.entry_json)
      }));

    } catch (error) {
      console.error('[AuditLogger] Query failed:', error.message);
      return [];
    }
  }

  /**
   * Get audit trail summary for date range
   */
  async getSummary(startDate, endDate) {
    try {
      const result = await this.db.query(
        `SELECT
          action,
          COUNT(*) as count,
          COUNT(DISTINCT DATE(timestamp)) as days
         FROM data_ingestion_audit_log
         WHERE timestamp >= $1 AND timestamp <= $2
         GROUP BY action
         ORDER BY count DESC`,
        [startDate, endDate]
      );

      return result.rows;

    } catch (error) {
      console.error('[AuditLogger] Summary query failed:', error.message);
      return [];
    }
  }

  /**
   * Verify audit trail integrity
   * Check: are hashes still valid? (indicates no tampering)
   */
  async verifyIntegrity() {
    try {
      const result = await this.db.query(
        `SELECT
          id,
          timestamp,
          hash,
          entry_json,
          (SHA256(entry_json)::text = hash) as valid
         FROM data_ingestion_audit_log
         ORDER BY timestamp ASC`
      );

      const entries = result.rows;
      const valid = entries.filter(e => e.valid).length;
      const invalid = entries.length - valid;

      return {
        totalEntries: entries.length,
        validEntries: valid,
        invalidEntries: invalid,
        integrityOK: invalid === 0,
        entries: invalid > 0 ? entries.filter(e => !e.valid) : []
      };

    } catch (error) {
      console.error('[AuditLogger] Integrity check failed:', error.message);
      return {
        error: error.message
      };
    }
  }

  /**
   * Generate compliance report
   */
  async generateComplianceReport(startDate, endDate) {
    try {
      const summary = await this.getSummary(startDate, endDate);
      const integrity = await this.verifyIntegrity();

      return {
        period: {
          start: startDate,
          end: endDate
        },
        summary,
        integrity: {
          totalEntries: integrity.totalEntries,
          validEntries: integrity.validEntries,
          invalidEntries: integrity.invalidEntries,
          integrityOK: integrity.integrityOK
        },
        generatedAt: new Date().toISOString()
      };

    } catch (error) {
      console.error('[AuditLogger] Report generation failed:', error.message);
      return { error: error.message };
    }
  }

  /**
   * Hash entry for integrity (uses SHA256)
   */
  hashEntry(entryJson) {
    return crypto
      .createHash('sha256')
      .update(entryJson)
      .digest('hex');
  }

  /**
   * Log extraction event
   */
  async logExtraction(source, recordCount, success, error = null) {
    return this.log({
      action: 'DATA_EXTRACTED',
      source,
      recordCount,
      success,
      error: error ? error.message : null
    });
  }

  /**
   * Log transformation event
   */
  async logTransformation(sourceFormat, recordCount, success, error = null) {
    return this.log({
      action: 'DATA_TRANSFORMED',
      sourceFormat,
      recordCount,
      success,
      error: error ? error.message : null
    });
  }

  /**
   * Log validation event
   */
  async logValidation(recordCount, validCount, invalidCount, passed) {
    return this.log({
      action: 'DATA_VALIDATED',
      totalRecords: recordCount,
      validRecords: validCount,
      invalidRecords: invalidCount,
      passed
    });
  }

  /**
   * Log load event
   */
  async logLoad(inserted, updated, errors) {
    return this.log({
      action: 'PROGRAMS_LOADED',
      inserted,
      updated,
      errors
    });
  }

  /**
   * Log pipeline event
   */
  async logPipelineEvent(action, success, details = {}) {
    return this.log({
      action,
      success,
      ...details
    });
  }
}

module.exports = AuditLogger;
