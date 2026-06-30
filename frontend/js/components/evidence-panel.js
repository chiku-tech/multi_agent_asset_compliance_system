// js/components/evidence-panel.js

class EvidencePanel {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
  }

  render(evidenceList = []) {
    if (!this.container) return;

    if (evidenceList.length === 0) {
      this.container.innerHTML = `
        <div class="card">
          <h3 class="headline-sm card-title">Compliance Evidence Bundle</h3>
          <p class="body-md" style="color: var(--slate-500); font-style: italic;">No evidence compiled for this audit run.</p>
        </div>
      `;
      return;
    }

    // Inject styles
    if (!document.getElementById('evidence-panel-styles')) {
      const style = document.createElement('style');
      style.id = 'evidence-panel-styles';
      style.textContent = `
        .evidence-accordion {
          display: flex;
          flex-direction: column;
          gap: 12px;
          width: 100%;
        }

        .evidence-item {
          background-color: var(--slate-900);
          border: 1px solid var(--border-color);
          border-radius: var(--border-radius-md);
          overflow: hidden;
          transition: all 0.3s ease;
        }

        .evidence-item.highlighted {
          border-color: var(--cobalt-primary);
          box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.3);
          transform: translateY(-2px);
        }

        .evidence-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          cursor: pointer;
          user-select: none;
          background-color: rgba(30, 41, 59, 0.2);
          transition: background-color 0.2s ease;
        }

        .evidence-header:hover {
          background-color: rgba(30, 41, 59, 0.4);
        }

        .evidence-header-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .evidence-index {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-width: 24px;
          height: 24px;
          border-radius: 4px;
          background-color: var(--slate-800);
          border: 1px solid var(--slate-700);
          color: var(--on-surface);
          font-family: var(--font-code);
          font-size: 11px;
          font-weight: 700;
        }

        .evidence-title {
          font-weight: 600;
          font-size: 14px;
          color: var(--on-surface);
        }

        .evidence-type-badge {
          display: inline-flex;
          padding: 2px 8px;
          border-radius: var(--border-radius-full);
          font-size: 10px;
          font-weight: 700;
          letter-spacing: 0.05em;
          text-transform: uppercase;
        }

        .type-document {
          background-color: rgba(37, 99, 235, 0.1);
          color: #60a5fa;
          border: 1px solid rgba(37, 99, 235, 0.2);
        }

        .type-image {
          background-color: rgba(16, 185, 129, 0.1);
          color: var(--emerald-success);
          border: 1px solid rgba(16, 185, 129, 0.2);
        }

        .type-remark {
          background-color: rgba(245, 158, 11, 0.1);
          color: var(--amber-warning);
          border: 1px solid rgba(245, 158, 11, 0.2);
        }

        .evidence-toggle-icon {
          font-size: 12px;
          color: var(--on-surface-variant);
          transition: transform 0.3s ease;
        }

        .evidence-item.expanded .evidence-toggle-icon {
          transform: rotate(180deg);
        }

        .evidence-body {
          max-height: 0;
          overflow: hidden;
          transition: max-height 0.3s cubic-bezier(0, 1, 0, 1);
        }

        .evidence-item.expanded .evidence-body {
          max-height: 1000px;
          transition: max-height 0.3s cubic-bezier(0.85, 0, 0.15, 1);
        }

        .evidence-content {
          padding: 20px;
          border-top: 1px solid var(--border-color);
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .relevance-bar-container {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .relevance-bar {
          flex: 1;
          height: 6px;
          background-color: var(--slate-800);
          border-radius: var(--border-radius-full);
          overflow: hidden;
        }

        .relevance-fill {
          height: 100%;
          background-color: var(--cobalt-primary);
          border-radius: var(--border-radius-full);
        }

        .relevance-score {
          font-family: var(--font-code);
          font-size: 12px;
          color: var(--on-surface-variant);
          min-width: 32px;
          text-align: right;
        }

        .citation-box {
          background-color: #000000;
          border: 1px solid var(--slate-800);
          border-radius: var(--border-radius-sm);
          padding: 14px 16px;
          font-family: var(--font-code);
          font-size: 12px;
          color: var(--on-surface-variant);
          line-height: 1.6;
          white-space: pre-wrap;
          position: relative;
          margin-top: 4px;
        }

        .citation-box::before {
          content: 'EXCERPT';
          position: absolute;
          top: -8px;
          left: 12px;
          background-color: var(--slate-900);
          padding: 0 6px;
          font-family: var(--font-body);
          font-size: 9px;
          font-weight: 700;
          color: var(--slate-500);
          letter-spacing: 0.05em;
        }

        .evidence-meta-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          background-color: rgba(30, 41, 59, 0.15);
          padding: 12px 16px;
          border-radius: var(--border-radius-sm);
        }

        .evidence-meta-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .evidence-meta-label {
          font-size: 10px;
          font-weight: 700;
          color: var(--slate-500);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .evidence-meta-value {
          font-size: 13px;
          color: var(--on-surface);
        }
      `;
      document.head.appendChild(style);
    }

    this.container.innerHTML = `
      <div class="card" style="margin-bottom: 24px;">
        <h3 class="headline-sm card-title" style="margin-bottom: 20px;">Compliance Evidence Bundle</h3>
        
        <div class="evidence-accordion">
          ${evidenceList.map((item, idx) => {
            let title = '';
            let typeBadge = '';
            let detailsHtml = '';

            if (item.source_type === 'document') {
              title = `${item.filename || 'Document'} ${item.page ? `(Page ${item.page})` : ''}`;
              typeBadge = `<span class="evidence-type-badge type-document">Document</span>`;
              
              const scorePct = item.relevance_score ? Math.round(item.relevance_score * 100) : 0;
              detailsHtml = `
                ${item.relevance_score !== null && item.relevance_score !== undefined ? `
                  <div class="evidence-meta-item" style="margin-bottom: 8px;">
                    <span class="evidence-meta-label">Relevance Alignment</span>
                    <div class="relevance-bar-container">
                      <div class="relevance-bar">
                        <div class="relevance-fill" style="width: ${scorePct}%;"></div>
                      </div>
                      <span class="relevance-score">${item.relevance_score.toFixed(2)}</span>
                    </div>
                  </div>
                ` : ''}
                
                ${item.excerpt ? `
                  <div class="citation-box">${item.excerpt}</div>
                ` : ''}

                <div class="evidence-meta-row">
                  <div class="evidence-meta-item">
                    <span class="evidence-meta-label">Document ID</span>
                    <span class="evidence-meta-value code-sm">${item.doc_id || 'N/A'}</span>
                  </div>
                  <div class="evidence-meta-item">
                    <span class="evidence-meta-label">Document Type</span>
                    <span class="evidence-meta-value code-sm">${item.doc_type || 'N/A'}</span>
                  </div>
                  <div class="evidence-meta-item">
                    <span class="evidence-meta-label">Finding Description</span>
                    <span class="evidence-meta-value">${item.finding || 'N/A'}</span>
                  </div>
                </div>
              `;
            } else if (item.source_type === 'image') {
              title = `Audit Photograph: ${item.s3_key ? item.s3_key.split('/').pop() : 'Unspecified Key'}`;
              typeBadge = `<span class="evidence-type-badge type-image">Image Agent</span>`;

              let condBadgeClass = 'badge-info';
              if (item.condition === 'critical' || item.condition === 'poor') condBadgeClass = 'badge-danger';
              else if (item.condition === 'fair') condBadgeClass = 'badge-warning';
              else if (item.condition === 'good') condBadgeClass = 'badge-success';

              detailsHtml = `
                <div class="evidence-meta-row" style="margin-bottom: 12px;">
                  <div class="evidence-meta-item">
                    <span class="evidence-meta-label">S3 Bucket Path</span>
                    <span class="evidence-meta-value code-sm">${item.s3_key || 'N/A'}</span>
                  </div>
                  <div class="evidence-meta-item">
                    <span class="evidence-meta-label">Visual Condition</span>
                    <div>
                      <span class="badge ${condBadgeClass}">${item.condition || 'Unknown'}</span>
                    </div>
                  </div>
                </div>

                <div class="citation-box" style="font-family: var(--font-body); font-size: 13px;">${item.image_finding || item.finding}</div>
              `;
            } else if (item.source_type === 'auditor_remark') {
              title = 'Auditor Site Remark';
              typeBadge = `<span class="evidence-type-badge type-remark">Remark</span>`;
              detailsHtml = `
                <div class="citation-box" style="font-family: var(--font-body); font-size: 13px;">${item.remark_text || item.finding}</div>
              `;
            }

            return `
              <div class="evidence-item" id="evidence-item-${idx}">
                <div class="evidence-header" data-index="${idx}">
                  <div class="evidence-header-left">
                    <span class="evidence-index">#${idx + 1}</span>
                    ${typeBadge}
                    <span class="evidence-title">${title}</span>
                  </div>
                  <span class="evidence-toggle-icon">▼</span>
                </div>
                <div class="evidence-body">
                  <div class="evidence-content">
                    ${detailsHtml}
                  </div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;

    // Add toggle event listeners
    this.container.querySelectorAll('.evidence-header').forEach(header => {
      header.addEventListener('click', (e) => {
        const item = e.currentTarget.closest('.evidence-item');
        item.classList.toggle('expanded');
      });
    });
  }

  highlightIndex(index) {
    const item = document.getElementById(`evidence-item-${index}`);
    if (!item) return;

    // Expand if collapsed
    item.classList.add('expanded');

    // Scroll into view
    item.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Flash highlight style
    item.classList.add('highlighted');
    setTimeout(() => {
      item.classList.remove('highlighted');
    }, 2000);
  }
}

window.EvidencePanel = EvidencePanel;
export default EvidencePanel;
