/**
 * RED/YELLOW/GREEN COMPONENT (Phase 1.2)
 * Reusable UI component for displaying data confidence/veracity indicators
 *
 * Used by Cards 4 (USHI) and Card 5 (UBADA) to show:
 * - Data reliability (HIGH, MEDIUM, LOW)
 * - Source quality
 * - Freshness & completeness
 * - Audit trail access
 */

class RYGComponent {
  /**
   * Constructor
   * @param {Object} confidenceData - Confidence object from API
   * @param {Object} options - Component options
   */
  constructor(confidenceData, options = {}) {
    this.data = confidenceData;
    this.options = {
      mode: 'inline-badge', // inline-badge, inline-indicator, expandable-card, tooltip
      containerClass: 'ryg-container',
      ...options
    };

    this.element = null;
    this.isExpanded = false;
  }

  /**
   * Render the component
   * @returns {HTMLElement}
   */
  render() {
    switch (this.options.mode) {
      case 'inline-badge':
        return this.renderBadge();
      case 'inline-indicator':
        return this.renderInlineIndicator();
      case 'expandable-card':
        return this.renderExpandableCard();
      case 'tooltip':
        return this.renderTooltip();
      default:
        return this.renderBadge();
    }
  }

  /**
   * Minimal badge mode: color + label
   * Usage: "🟢 HIGH" inline with text
   */
  renderBadge() {
    const container = document.createElement('span');
    container.className = `${this.options.containerClass} ryg-badge`;

    const { color, label, icon } = this.getColorAndLabel();

    container.innerHTML = `
      <span class="ryg-badge-icon" aria-hidden="true">${icon}</span>
      <span class="ryg-badge-label">${label}</span>
    `;

    container.setAttribute('data-color', color);
    container.setAttribute('aria-label', `Data confidence level: ${label}`);

    // Add inline styles
    container.style.display = 'inline-flex';
    container.style.alignItems = 'center';
    container.style.gap = '0.5rem';
    container.style.padding = '0.25rem 0.5rem';
    container.style.borderRadius = '4px';
    container.style.fontSize = '0.875rem';
    container.style.fontWeight = '600';

    this.element = container;
    return container;
  }

  /**
   * Inline indicator mode: badge + source + freshness
   * Usage: "🟢 HIGH | eMedNY | 2 hours old"
   */
  renderInlineIndicator() {
    const badge = this.renderBadge();
    const { color } = this.getColorAndLabel();

    const wrapper = document.createElement('span');
    wrapper.className = `${this.options.containerClass} ryg-inline-indicator`;

    const source = this.data.sources ? this.data.sources[0] : 'Unknown';
    const freshness = this.getFreshnessLabel();

    wrapper.innerHTML = `
      ${badge.outerHTML}
      <span class="ryg-source" style="margin-left: 1rem; font-size: 0.875rem; color: #666;">
        | ${source} | ${freshness}
      </span>
    `;

    wrapper.setAttribute('data-color', color);

    this.element = wrapper;
    return wrapper;
  }

  /**
   * Expandable card mode: badge + collapsible detail section
   * Click to expand full information
   */
  renderExpandableCard() {
    const container = document.createElement('div');
    container.className = `${this.options.containerClass} ryg-expandable-card`;

    const { color, label, icon } = this.getColorAndLabel();
    const cardId = `ryg-card-${Date.now()}`;

    container.innerHTML = `
      <div class="ryg-header" style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background-color: ${this.getBackgroundColor(color)};
        border: 1px solid ${this.getBorderColor(color)};
        border-radius: 6px;
        cursor: pointer;
        user-select: none;
      ">
        <span class="ryg-summary" style="display: flex; align-items: center; gap: 0.75rem;">
          <span class="ryg-icon" style="font-size: 1.5rem;">${icon}</span>
          <span>
            <strong>${label} Confidence</strong>
            <div style="font-size: 0.875rem; color: #666; margin-top: 0.25rem;">
              ${this.data.confidence ? this.data.confidence.toFixed(2) : 'N/A'} |
              ${this.data.sources ? this.data.sources[0] : 'Unknown'}
            </div>
          </span>
        </span>
        <span class="ryg-toggle" style="font-size: 1.25rem; transition: transform 0.2s;">
          ▼
        </span>
      </div>

      <div class="ryg-detail" style="
        display: none;
        padding: 1rem;
        background-color: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-top: none;
        border-radius: 0 0 6px 6px;
        font-size: 0.875rem;
      ">
        <div style="margin-bottom: 1rem;">
          <strong>Confidence Level:</strong> ${label}
          <div style="margin-top: 0.5rem; color: #666;">
            Score: ${this.data.confidence ? this.data.confidence.toFixed(3) : 'N/A'} / 1.0
          </div>
        </div>

        ${this.data.sources ? `
          <div style="margin-bottom: 1rem;">
            <strong>Sources Used:</strong>
            <ul style="margin: 0.5rem 0 0 1.5rem; color: #666;">
              ${this.data.sources.map(s => `<li>${s}</li>`).join('')}
            </ul>
          </div>
        ` : ''}

        <div style="margin-bottom: 1rem;">
          <strong>Freshness:</strong>
          <div style="margin-top: 0.5rem; color: #666;">
            ${this.getFreshnessLabel()}
          </div>
        </div>

        ${this.data.caveat ? `
          <div style="
            margin-top: 1rem;
            padding: 0.75rem;
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            color: #856404;
          ">
            <strong>⚠️ Note:</strong> ${this.data.caveat}
          </div>
        ` : ''}

        <div style="margin-top: 1rem;">
          <button class="ryg-view-audit" style="
            background-color: #007bff;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.875rem;
          ">
            View Audit Trail →
          </button>
        </div>
      </div>
    `;

    // Toggle expand/collapse
    const header = container.querySelector('.ryg-header');
    const detail = container.querySelector('.ryg-detail');
    const toggle = container.querySelector('.ryg-toggle');

    header.addEventListener('click', () => {
      this.isExpanded = !this.isExpanded;
      detail.style.display = this.isExpanded ? 'block' : 'none';
      toggle.style.transform = this.isExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
    });

    // Audit trail button
    const auditButton = container.querySelector('.ryg-view-audit');
    if (auditButton && this.options.onAuditClick) {
      auditButton.addEventListener('click', () => {
        this.options.onAuditClick();
      });
    }

    container.setAttribute('data-color', color);
    this.element = container;
    return container;
  }

  /**
   * Tooltip mode: hover to see details
   */
  renderTooltip() {
    const badge = this.renderBadge();
    const { color } = this.getColorAndLabel();

    badge.style.position = 'relative';
    badge.style.cursor = 'help';

    const tooltip = document.createElement('div');
    tooltip.className = 'ryg-tooltip';
    tooltip.style.cssText = `
      position: absolute;
      bottom: 100%;
      left: 50%;
      transform: translateX(-50%);
      background-color: #333;
      color: white;
      padding: 0.75rem 1rem;
      border-radius: 4px;
      font-size: 0.875rem;
      white-space: nowrap;
      z-index: 1000;
      display: none;
      margin-bottom: 0.5rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    `;

    tooltip.innerHTML = `
      ${this.data.confidence ? `Score: ${this.data.confidence.toFixed(3)}` : 'Confidence: Unknown'}
      ${this.data.sources ? ` | ${this.data.sources[0]}` : ''}
    `;

    badge.appendChild(tooltip);

    // Show/hide on hover
    badge.addEventListener('mouseenter', () => {
      tooltip.style.display = 'block';
    });

    badge.addEventListener('mouseleave', () => {
      tooltip.style.display = 'none';
    });

    this.element = badge;
    return badge;
  }

  /**
   * Get color and label based on confidence score
   */
  getColorAndLabel() {
    const score = this.data.confidence || 0;

    if (score >= 0.85) {
      return {
        color: 'green',
        label: 'HIGH',
        icon: '🟢'
      };
    } else if (score >= 0.60) {
      return {
        color: 'yellow',
        label: 'MEDIUM',
        icon: '🟡'
      };
    } else {
      return {
        color: 'red',
        label: 'LOW',
        icon: '🔴'
      };
    }
  }

  /**
   * Get background color for card mode
   */
  getBackgroundColor(color) {
    switch (color) {
      case 'green':
        return '#d4edda';
      case 'yellow':
        return '#fff3cd';
      case 'red':
        return '#f8d7da';
      default:
        return '#f5f5f5';
    }
  }

  /**
   * Get border color for card mode
   */
  getBorderColor(color) {
    switch (color) {
      case 'green':
        return '#c3e6cb';
      case 'yellow':
        return '#ffeeba';
      case 'red':
        return '#f5c6cb';
      default:
        return '#ddd';
    }
  }

  /**
   * Get freshness label
   */
  getFreshnessLabel() {
    const ageMinutes = this.data.age_minutes || 0;

    if (ageMinutes === 0) {
      return 'Real-time';
    } else if (ageMinutes < 60) {
      return `${ageMinutes} min old`;
    } else if (ageMinutes < 1440) {
      const hours = Math.floor(ageMinutes / 60);
      return `${hours} hour${hours > 1 ? 's' : ''} old`;
    } else {
      const days = Math.floor(ageMinutes / 1440);
      return `${days} day${days > 1 ? 's' : ''} old`;
    }
  }

  /**
   * Attach to DOM element
   */
  attachTo(selector) {
    const container = document.querySelector(selector);
    if (container) {
      container.appendChild(this.render());
    }
  }

  /**
   * Update data and re-render
   */
  update(newData) {
    this.data = newData;
    if (this.element && this.element.parentNode) {
      const parent = this.element.parentNode;
      this.element.remove();
      parent.appendChild(this.render());
    }
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = RYGComponent;
}
