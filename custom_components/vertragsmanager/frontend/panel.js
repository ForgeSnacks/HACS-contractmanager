class VertragsmanagerPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) {
      this._initialized = true;
      this._page = this._initialPage();
      this.renderShell();
    }
    this.render();
  }

  _initialPage() {
    const url = new URL(window.location.href);
    return url.searchParams.get("page") || "overview";
  }

  renderShell() {
    this.innerHTML = `
      <style>
        :host {
          display: block;
          background: transparent;
          color: var(--primary-text-color);
          font-family: var(--primary-font-family);
        }
        .wrap {
          max-width: 1440px;
          margin: 0 auto;
          padding: 24px;
          background: var(--card-background-color);
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .nav {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 20px;
        }
        .nav button {
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          color: var(--primary-text-color);
          padding: 10px 14px;
          border-radius: 10px;
          cursor: pointer;
        }
        .nav button.active {
          background: var(--primary-color);
          color: white;
          border-color: var(--primary-color);
        }
        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 16px;
          margin-bottom: 20px;
        }
        .split {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 16px;
        }
        .card {
          background: var(--card-background-color, #ffffff);
          border: 1px solid var(--divider-color);
          border-radius: 12px;
          padding: 16px;
        }
        .value { font-size: 1.8rem; font-weight: 700; }
        .hint { color: var(--secondary-text-color); }
        .bar-row {
          display: grid;
          grid-template-columns: 220px 1fr 120px;
          gap: 12px;
          align-items: center;
          margin-bottom: 10px;
        }
        .bar {
          height: 12px;
          border-radius: 999px;
          overflow: hidden;
          background: rgba(120,120,120,0.18);
        }
        .bar > div { height: 100%; background: var(--primary-color); }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 10px 8px; border-bottom: 1px solid var(--divider-color); }
        @media (max-width: 900px) {
          .split { grid-template-columns: 1fr; }
          .bar-row { grid-template-columns: 1fr; }
        }
      </style>
      <div class="wrap">
        <div class="nav" id="nav"></div>
        <div id="content"></div>
      </div>
    `;

    this.querySelector("#nav").addEventListener("click", (ev) => {
      const btn = ev.target.closest("button[data-page]");
      if (!btn) return;
      this._page = btn.dataset.page;
      const url = new URL(window.location.href);
      url.searchParams.set("page", this._page);
      window.history.replaceState({}, "", url);
      this.render();
    });
  }

  _escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  _displayName(name) {
    return String(name || "").replace(/\s*Kündigungsfrist\s*$/i, "").replace(/\s*Frist\s*$/i, "").trim();
  }

  _contractKeyFromInput(raw) {
    return String(raw || "").trim().toLowerCase().replace(/[^a-z0-9äöüß]+/gi, "_").replace(/^_+|_+$/g, "");
  }

  _isPrimaryContractSensor(state) {
    return state.entity_id.startsWith("sensor.vertragsmanager_") && state.entity_id.endsWith("_frist") && state.attributes.deadline_date;
  }

  _contractKeyFromState(state) {
    return state.entity_id.replace(/^sensor\.vertragsmanager_/, "").replace(/_frist$/, "");
  }

  _deviceNameFromState(state) {
    return state?.attributes?.device_name || state?.attributes?.friendly_name || this._contractKeyFromState(state).replace(/_/g, " ");
  }

  _findMonthlyState(contractKey) {
    return this._hass.states[`sensor.vertragsmanager_${contractKey}_monatskosten`] || null;
  }

  contracts() {
    return Object.values(this._hass.states)
      .filter((state) => this._isPrimaryContractSensor(state))
      .map((state) => {
        const contractKey = this._contractKeyFromState(state);
        const monthly = this._findMonthlyState(contractKey);
        return {
          entity_id: state.entity_id,
          key: contractKey,
          name: this._displayName(this._deviceNameFromState(state)),
          provider: state.attributes.provider || "",
          category: state.attributes.category || "",
          monthlyCost: Number(monthly?.state || 0),
          deadlineDays: Number(state.state || 0),
          deadlineDate: state.attributes.deadline_date || "",
          renewalDate: state.attributes.next_renewal || "",
        };
      })
      .sort((a, b) => a.deadlineDays - b.deadlineDays);
  }

  summary(contracts) {
    const total = contracts.reduce((sum, item) => sum + item.monthlyCost, 0);
    const urgent = contracts.filter((item) => item.deadlineDays <= 30).length;
    const next = contracts.length ? contracts[0] : null;
    return { total, urgent, next };
  }

  groupByCategory(contracts) {
    const grouped = {};
    for (const item of contracts) grouped[item.category] = (grouped[item.category] || 0) + item.monthlyCost;
    return Object.entries(grouped).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
  }

  bars(items, suffix = "€") {
    if (!items.length) return `<p class="hint">Noch keine Daten vorhanden.</p>`;
    const max = Math.max(...items.map((item) => item.value), 1);
    return items.map((item) => `
      <div class="bar-row">
        <div>${item.name}</div>
        <div class="bar"><div style="width:${(item.value / max) * 100}%"></div></div>
        <div>${item.value.toFixed(2)} ${suffix}</div>
      </div>
    `).join("");
  }

  pieChart(items) {
    if (!items.length) return `<p class="hint">Noch keine Daten vorhanden.</p>`;
    const total = items.reduce((sum, item) => sum + item.value, 0);
    const colors = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16", "#f97316", "#64748b"];
    let cumulative = 0;
    const segments = items.map((item, idx) => {
      const value = Number(item.value || 0);
      const percentage = (value / total) * 100;
      const startAngle = (cumulative / total) * 360;
      cumulative += value;
      const endAngle = (cumulative / total) * 360;
      const largeArc = percentage > 50 ? 1 : 0;
      const x1 = Math.cos(Math.PI * startAngle / 180) * 100;
      const y1 = Math.sin(Math.PI * startAngle / 180) * 100;
      const x2 = Math.cos(Math.PI * endAngle / 180) * 100;
      const y2 = Math.sin(Math.PI * endAngle / 180) * 100;
      const d = `M 0 0 L ${x1} ${y1} A 100 100 0 ${largeArc} 1 ${x2} ${y2} Z`;
      return `<path d="${d}" fill="${colors[idx % colors.length]}" stroke="white" stroke-width="2"><title>${item.name}: ${value.toFixed(2)} € (${percentage.toFixed(1)}%)</title></path>`;
    }).join("");
    return `
      <div style="display:flex; justify-content:center; gap:20px; flex-wrap:wrap;">
        <svg viewBox="-100 -100 200 200" width="220" height="220">${segments}</svg>
        <div>
          ${items.map((item, idx) => `
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
              <div style="width:12px; height:12px; background:${colors[idx % colors.length]}; border-radius:2px;"></div>
              <span>${item.name}: ${Number(item.value).toFixed(2)} €</span>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  }

  renderOverview(contracts) {
    const summary = this.summary(contracts);
    const costByContract = contracts.map((item) => ({ name: item.name, value: item.monthlyCost }));
    const costByCategory = this.groupByCategory(contracts);
    return `
      <div class="grid">
        <div class="card"><h3>Verträge</h3><div class="value">${contracts.length}</div></div>
        <div class="card"><h3>Gesamtkosten / Monat</h3><div class="value">${summary.total.toFixed(2)} €</div></div>
        <div class="card"><h3>Fristen ≤ 30 Tage</h3><div class="value">${summary.urgent}</div></div>
        <div class="card"><h3>Nächste Frist</h3><div class="value">${summary.next ? `${Math.round(summary.next.deadlineDays)} Tage` : "-"}</div></div>
      </div>
      <div class="split">
        <div class="card"><h3>Kosten pro Vertrag</h3>${this.bars(costByContract)}</div>
        <div class="card"><h3>Kosten nach Kategorie</h3>${this.bars(costByCategory)}</div>
      </div>
      <div class="split">
        <div class="card"><h3>Kosten-Diagramm</h3>${this.pieChart(costByContract)}</div>
        <div class="card"><h3>Kategorien-Diagramm</h3>${this.pieChart(costByCategory)}</div>
      </div>
    `;
  }

  renderContracts(contracts) {
    return `
      <div class="card">
        <h3>Alle Verträge</h3>
        <table>
          <thead>
            <tr>
              <th>Name</th><th>Anbieter</th><th>Kategorie</th><th>Monatlich</th><th>Kündigung in</th><th>Fristdatum</th>
            </tr>
          </thead>
          <tbody>
            ${contracts.map((item) => `
              <tr>
                <td>${item.name}</td>
                <td>${item.provider}</td>
                <td>${item.category}</td>
                <td>${item.monthlyCost.toFixed(2)} €</td>
                <td>${Math.round(item.deadlineDays)} Tage</td>
                <td>${item.deadlineDate}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  renderCosts(contracts) {
    const costByContract = contracts.map((item) => ({ name: item.name, value: item.monthlyCost }));
    const costByCategory = this.groupByCategory(contracts);
    return `
      <div class="split">
        <div class="card"><h3>Monatliche Kosten je Vertrag</h3>${this.bars(costByContract)}</div>
        <div class="card"><h3>Kosten je Kategorie</h3>${this.bars(costByCategory)}</div>
      </div>
    `;
  }

  renderDeadlines(contracts) {
    return `
      <div class="card">
        <h3>Fristen</h3>
        ${contracts.length ? contracts.map((item) => `
          <div class="bar-row">
            <div>${item.name}</div>
            <div class="bar"><div style="width:${Math.max(3, Math.min(100, ((365 - item.deadlineDays) / 365) * 100))}%"></div></div>
            <div>${Math.round(item.deadlineDays)} T</div>
          </div>
        `).join("") : `<p class="hint">Noch keine Fristen vorhanden.</p>`}
      </div>
    `;
  }

  render() {
    if (!this._hass) return;
    const contracts = this.contracts();
    const pages = [["overview", "Übersicht"],["contracts", "Alle Verträge"],["costs", "Kosten"],["deadlines", "Fristen"],["add", "Hinzufügen"]];
    this.querySelector("#nav").innerHTML = pages.map(([key, label]) => `<button class="${this._page === key ? "active" : ""}" data-page="${key}">${label}</button>`).join("");
    let content = "";
    if (this._page === "overview") content = this.renderOverview(contracts);
    if (this._page === "contracts") content = this.renderContracts(contracts);
    if (this._page === "costs") content = this.renderCosts(contracts);
    if (this._page === "deadlines") content = this.renderDeadlines(contracts);
    if (this._page === "add") content = `
      <div class="card">
        <h3>Vertrag / HUB hinzufügen</h3>
        <p class="hint">Öffnet den Home-Assistant-Setup-Assistenten für Vertragsmanager.</p>
        <a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=vertragsmanager" target="_blank" rel="noopener noreferrer" style="display:inline-block;padding:10px 14px;border-radius:10px;background:var(--primary-color);color:white;text-decoration:none;">Hinzufügen</a>
      </div>
    `;
    this.querySelector("#content").innerHTML = content;
  }
}

if (!customElements.get("vertragsmanager-panel")) {
  customElements.define("vertragsmanager-panel", VertragsmanagerPanel);
}
