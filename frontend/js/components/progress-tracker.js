// js/components/progress-tracker.js

class ProgressTracker {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.steps = [
      { id: 'document_agent', name: 'Document Agent', label: 'RAG Retrieval' },
      { id: 'image_agent', name: 'Image Agent', label: 'Vision Inspection' },
      { id: 'rule_agent', name: 'Rule Agent', label: 'Rule Verification' },
      { id: 'evidence_agent', name: 'Evidence Agent', label: 'Evidence Bundle' },
      { id: 'verdict_agent', name: 'Verdict Agent', label: 'Final Verdict' }
    ];
    this.currentStepIndex = -1;
    this.render();
  }

  render() {
    if (!this.container) return;

    // Inject component styles if not already present
    if (!document.getElementById('progress-tracker-styles')) {
      const style = document.createElement('style');
      style.id = 'progress-tracker-styles';
      style.textContent = `
        .pipeline-tracker {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
          padding: 24px;
          background-color: var(--slate-900);
          border: 1px solid var(--border-color);
          border-radius: var(--border-radius-md);
          margin-bottom: 24px;
          overflow-x: auto;
          gap: 16px;
        }
        
        .pipeline-step {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          position: relative;
          flex: 1;
        }

        .pipeline-step:not(:last-child)::after {
          content: '';
          position: absolute;
          top: 20px;
          left: calc(50% + 20px);
          right: calc(-50% + 20px);
          height: 2px;
          background-color: var(--slate-800);
          z-index: 1;
          transition: background-color 0.4s ease;
        }

        .pipeline-step.completed:not(:last-child)::after {
          background-color: var(--emerald-success);
        }

        .pipeline-step.error:not(:last-child)::after {
          background-color: var(--rose-error);
        }

        .step-node {
          width: 40px;
          height: 40px;
          border-radius: var(--border-radius-full);
          background-color: var(--charcoal-bg);
          border: 2px solid var(--slate-700);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          color: var(--on-surface-variant);
          z-index: 2;
          margin-bottom: 8px;
          transition: all 0.3s ease;
          position: relative;
        }

        .pipeline-step.pending .step-node {
          border-color: var(--slate-700);
          color: var(--on-surface-variant);
        }

        .pipeline-step.active .step-node {
          border-color: var(--cobalt-primary);
          color: #ffffff;
          box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.2);
          animation: node-pulse 1.5s infinite alternate;
        }

        .pipeline-step.completed .step-node {
          background-color: var(--emerald-success);
          border-color: var(--emerald-success);
          color: #ffffff;
        }

        .pipeline-step.error .step-node {
          background-color: var(--rose-error);
          border-color: var(--rose-error);
          color: #ffffff;
        }

        .step-name {
          font-size: 13px;
          font-weight: 600;
          color: var(--on-surface-variant);
          margin-bottom: 2px;
          transition: color 0.3s ease;
        }

        .pipeline-step.active .step-name {
          color: var(--on-surface);
        }

        .pipeline-step.completed .step-name {
          color: var(--emerald-success);
        }

        .step-label {
          font-size: 10px;
          color: var(--slate-500);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        @keyframes node-pulse {
          0% {
            box-shadow: 0 0 0 0px rgba(37, 99, 235, 0.4);
            background-color: var(--charcoal-bg);
          }
          100% {
            box-shadow: 0 0 0 8px rgba(37, 99, 235, 0.1);
            background-color: rgba(37, 99, 235, 0.1);
          }
        }

        @media (max-width: 768px) {
          .pipeline-tracker {
            flex-direction: column;
            align-items: flex-start;
            gap: 24px;
          }
          .pipeline-step {
            flex-direction: row;
            align-items: center;
            text-align: left;
            width: 100%;
            gap: 16px;
          }
          .pipeline-step:not(:last-child)::after {
            top: 40px;
            left: 20px;
            right: auto;
            bottom: -24px;
            width: 2px;
            height: calc(100% - 16px);
          }
          .step-node {
            margin-bottom: 0;
          }
          .step-details {
            display: flex;
            flex-direction: column;
          }
        }
      `;
      document.head.appendChild(style);
    }

    this.container.innerHTML = `
      <div class="pipeline-tracker">
        ${this.steps.map((step, idx) => `
          <div class="pipeline-step pending" id="step-${step.id}">
            <div class="step-node" id="node-${step.id}">${idx + 1}</div>
            <div class="step-details">
              <div class="step-name">${step.name}</div>
              <div class="step-label">${step.label}</div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  updateNode(nodeId, status) {
    // status: 'active' | 'completed' | 'error' | 'pending'
    const stepEl = document.getElementById(`step-${nodeId}`);
    const nodeEl = document.getElementById(`node-${nodeId}`);
    if (!stepEl || !nodeEl) return;

    // Reset classes
    stepEl.className = `pipeline-step ${status}`;
    
    // Set icon or step number
    const stepIndex = this.steps.findIndex(s => s.id === nodeId);
    if (status === 'completed') {
      nodeEl.innerHTML = `
        <svg style="width: 18px; height: 18px;" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"></path>
        </svg>
      `;
    } else if (status === 'error') {
      nodeEl.innerHTML = `
        <svg style="width: 18px; height: 18px;" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      `;
    } else {
      nodeEl.textContent = stepIndex + 1;
    }
  }

  setCurrentStep(nodeId) {
    // Mark previous steps as completed if they are still pending/active
    const index = this.steps.findIndex(s => s.id === nodeId);
    if (index === -1) return;

    this.currentStepIndex = index;

    this.steps.forEach((step, idx) => {
      if (idx < index) {
        // Only mark complete if it wasn't already marked error
        const stepEl = document.getElementById(`step-${step.id}`);
        if (!stepEl.classList.contains('error')) {
          this.updateNode(step.id, 'completed');
        }
      } else if (idx === index) {
        this.updateNode(step.id, 'active');
      } else {
        this.updateNode(step.id, 'pending');
      }
    });
  }

  markComplete(nodeId) {
    this.updateNode(nodeId, 'completed');
  }

  markError(nodeId) {
    this.updateNode(nodeId, 'error');
  }

  reset() {
    this.currentStepIndex = -1;
    this.steps.forEach(step => {
      this.updateNode(step.id, 'pending');
    });
  }
}

window.ProgressTracker = ProgressTracker;
export default ProgressTracker;
