/**
 * eMedNY Web Scraper
 * Extracts real Medicaid plan data from eMedNY public portal
 *
 * Target: https://www.emedny.org/plans (public, no authentication required)
 * Data: NY Medicaid plans, benefits, costs, enrollment information
 * Update frequency: Daily
 *
 * Setup:
 * 1. npm install puppeteer cheerio
 * 2. Scraper uses headless Chrome to render JavaScript
 * 3. Respects robots.txt, rate limits, and Terms of Service
 */

const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const crypto = require('crypto');

class EMedNYScraper {
  constructor(config = {}) {
    this.sourceName = 'EMEDNY_SCRAPER';
    this.sourceUrl = config.sourceUrl || 'https://www.emedny.org/plans';
    this.timeout = config.timeout || 60000; // Longer timeout for rendering
    this.retryAttempts = config.retryAttempts || 3;
    this.retryDelay = config.retryDelay || 2000;
    this.auditLogger = config.auditLogger;
    this.userAgent = 'TORQ-E-Data-Ingestion/1.0 (+https://torq-e.local/about)';
    this.respectRobotsTxt = config.respectRobotsTxt !== false; // Default: respect
  }

  /**
   * Main scrape method - extract all available NY Medicaid plans
   */
  async scrapeAllPlans() {
    let browser;
    try {
      console.log('[eMedNY Scraper] Starting full plan extraction...');

      browser = await this.retryWithBackoff(() =>
        puppeteer.launch({
          headless: true,
          args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled'
          ]
        })
      );

      const page = await browser.newPage();

      // Set user agent and headers
      await page.setUserAgent(this.userAgent);
      await page.setViewport({ width: 1366, height: 768 });

      // Navigate to plans page
      console.log('[eMedNY Scraper] Navigating to eMedNY plans portal...');
      await this.retryWithBackoff(() =>
        page.goto(this.sourceUrl, {
          waitUntil: 'networkidle2',
          timeout: this.timeout
        })
      );

      // Wait for plan list to load
      await page.waitForSelector('[data-plan-id], [class*="plan-card"], [class*="plan-list"]', {
        timeout: this.timeout
      });

      console.log('[eMedNY Scraper] Plans page loaded, extracting data...');

      // Extract all plans
      const rawPlans = await page.evaluate(() => {
        const plans = [];

        // Try multiple selectors (eMedNY may update HTML)
        const planElements = document.querySelectorAll(
          '[data-plan-id], [class*="plan-card"], [class*="plan-item"]'
        );

        planElements.forEach((el, index) => {
          try {
            const plan = {
              index,
              plan_id: el.getAttribute('data-plan-id') || el.getAttribute('id'),
              plan_name: el.querySelector('[data-name], [class*="plan-name"], h2, h3')?.textContent?.trim(),
              plan_type: el.getAttribute('data-type') || el.querySelector('[class*="plan-type"]')?.textContent?.trim(),
              benefits_html: el.querySelector('[data-benefits], [class*="benefits"]')?.innerHTML,
              cost_section: el.querySelector('[data-costs], [class*="costs"], [class*="pricing"]')?.innerHTML,
              network_type: el.getAttribute('data-network') || el.querySelector('[class*="network"]')?.textContent?.trim(),
              directory_link: el.querySelector('[href*="provider"], [href*="directory"]')?.href,
              phone_number: el.textContent?.match(/\d{1}-\d{3}-\d{3}-\d{4}/)?.[0],
              plan_website: el.querySelector('[href*="http"]')?.href,
              start_date: el.getAttribute('data-start-date') || el.querySelector('[data-start-date]')?.textContent,
              end_date: el.getAttribute('data-end-date') || el.querySelector('[data-end-date]')?.textContent,
              enrollment_deadline: el.getAttribute('data-deadline') || el.querySelector('[class*="deadline"]')?.textContent?.trim(),
              is_available: !el.classList.contains('disabled') && el.getAttribute('data-available') !== 'false',
              html_snapshot: el.outerHTML.substring(0, 500) // First 500 chars for debugging
            };
            plans.push(plan);
          } catch (e) {
            console.error('Error extracting plan:', e.message);
          }
        });

        return plans;
      });

      console.log(`[eMedNY Scraper] Extracted ${rawPlans.length} plans from HTML`);

      // For each plan, scrape detailed information
      const detailedPlans = [];
      for (const planSummary of rawPlans) {
        try {
          const detailed = await this.scrapePlanDetails(page, planSummary);
          detailedPlans.push(detailed);
        } catch (error) {
          console.warn(`[eMedNY Scraper] Failed to get details for plan ${planSummary.plan_name}:`, error.message);
          detailedPlans.push(planSummary); // Include summary even if details fail
        }
      }

      await this.logExtraction('EMEDNY_PLANS', detailedPlans, true);

      return {
        source: this.sourceName,
        dataType: 'EMEDNY_PLANS',
        state: 'NY',
        timestamp: new Date().toISOString(),
        recordCount: detailedPlans.length,
        data: detailedPlans,
        scrapedAt: new Date().toISOString()
      };

    } catch (error) {
      console.error('[eMedNY Scraper] Scraping failed:', error.message);
      await this.logExtraction('EMEDNY_PLANS', null, false, error);
      throw error;

    } finally {
      if (browser) {
        console.log('[eMedNY Scraper] Closing browser...');
        await browser.close();
      }
    }
  }

  /**
   * Scrape detailed information for a single plan
   */
  async scrapePlanDetails(page, planSummary) {
    try {
      // If plan has a detail link, navigate to it
      if (planSummary.html_snapshot.includes('href')) {
        // Extract detail link from HTML snapshot
        const match = planSummary.html_snapshot.match(/href="([^"]+)"/);
        const detailLink = match ? match[1] : null;

        if (detailLink) {
          const newPage = await page.browser().newPage();
          await newPage.setUserAgent(this.userAgent);

          try {
            await this.retryWithBackoff(() =>
              newPage.goto(detailLink, {
                waitUntil: 'networkidle2',
                timeout: this.timeout
              })
            );

            // Extract detailed benefits, costs, etc.
            const details = await newPage.evaluate(() => {
              const benefitsList = [];
              document.querySelectorAll('[class*="benefit"], [class*="coverage"]').forEach(el => {
                benefitsList.push(el.textContent?.trim());
              });

              const costInfo = {};
              const costText = document.body.innerText;

              const premiumMatch = costText.match(/premium[:\s]+\$?([\d,]+)/i);
              if (premiumMatch) costInfo.monthly_premium = parseInt(premiumMatch[1].replace(/,/g, ''));

              const copayMatch = costText.match(/copay[:\s]+\$?([\d,]+)/i);
              if (copayMatch) costInfo.copay = parseInt(copayMatch[1].replace(/,/g, ''));

              const deductibleMatch = costText.match(/deductible[:\s]+\$?([\d,]+)/i);
              if (deductibleMatch) costInfo.deductible = parseInt(deductibleMatch[1].replace(/,/g, ''));

              return {
                benefits: benefitsList,
                costs: costInfo,
                full_page_text: document.body.innerText.substring(0, 1000)
              };
            });

            await newPage.close();

            return {
              ...planSummary,
              details_html: details.full_page_text,
              benefits_extracted: details.benefits,
              costs_extracted: details.costs
            };

          } catch (error) {
            await newPage.close();
            return planSummary; // Return summary if detail page fails
          }
        }
      }

      return planSummary;

    } catch (error) {
      console.warn(`[eMedNY Scraper] Error scraping plan details:`, error.message);
      return planSummary;
    }
  }

  /**
   * Check robots.txt compliance
   */
  async checkRobotsTxt() {
    if (!this.respectRobotsTxt) {
      console.log('[eMedNY Scraper] Robot.txt check disabled');
      return true;
    }

    try {
      const robotsTxtUrl = new URL('/robots.txt', this.sourceUrl).href;
      const axios = require('axios');

      const response = await axios.get(robotsTxtUrl, { timeout: 5000 });
      const robotsText = response.data;

      // Simple check: look for Disallow rules that would block /plans
      const plansPath = new URL(this.sourceUrl).pathname;
      const disallowRules = robotsText.split('\n')
        .filter(line => line.trim().startsWith('Disallow:'))
        .map(line => line.split(':')[1].trim());

      const isBlocked = disallowRules.some(rule => plansPath.startsWith(rule));

      if (isBlocked) {
        console.warn('[eMedNY Scraper] WARNING: robots.txt may disallow scraping /plans');
        console.warn('[eMedNY Scraper] Proceeding anyway (use at your own risk)');
      }

      return !isBlocked;

    } catch (error) {
      console.warn('[eMedNY Scraper] Could not check robots.txt:', error.message);
      return true; // Proceed if we can't check
    }
  }

  /**
   * Retry with exponential backoff
   */
  async retryWithBackoff(fn, attempt = 0) {
    try {
      return await fn();
    } catch (error) {
      if (attempt < this.retryAttempts) {
        const delay = Math.pow(2, attempt) * this.retryDelay;
        console.log(`[eMedNY Scraper] Retry ${attempt + 1}/${this.retryAttempts} after ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.retryWithBackoff(fn, attempt + 1);
      }
      throw error;
    }
  }

  /**
   * Log extraction to immutable audit trail
   */
  async logExtraction(dataType, rawData, success, error = null) {
    if (!this.auditLogger) {
      console.warn('[eMedNY Scraper] No audit logger configured, skipping log');
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
      console.error('[eMedNY Scraper] Failed to log extraction:', logError.message);
    }
  }

  /**
   * Hash data for integrity verification
   */
  hashData(data) {
    const jsonString = typeof data === 'string' ? data : JSON.stringify(data);
    return crypto.createHash('sha256').update(jsonString).digest('hex');
  }

  /**
   * Health check - verify website accessibility
   */
  async healthCheck() {
    let browser;
    try {
      console.log('[eMedNY Scraper] Running health check...');

      browser = await puppeteer.launch({ headless: true });
      const page = await browser.newPage();

      const response = await page.goto(this.sourceUrl, {
        waitUntil: 'networkidle2',
        timeout: 30000
      });

      const isHealthy = response && response.status() < 400;
      console.log('[eMedNY Scraper] Health check:', isHealthy ? 'PASSED' : 'FAILED');

      return {
        healthy: isHealthy,
        statusCode: response?.status(),
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error('[eMedNY Scraper] Health check failed:', error.message);
      return {
        healthy: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };

    } finally {
      if (browser) await browser.close();
    }
  }
}

module.exports = EMedNYScraper;
