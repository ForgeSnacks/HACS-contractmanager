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
          padding: 16px;
          background: var(--primary-background-color);
          color: var(--primary-text-color);
          font-family: var(--primary-font-family);
        }
        .wrap { max-width: 1440px; margin: 0 auto; }
        .nav { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
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
          background: var(--card-background-color);
          border: 1px solid var(--divider-color);
          border-radius: 12px;
          padding: 16px;
        }
        .value { font-size: 1.8rem; font-weight: 700; }
        .hint { color: var(--secondary-text-color); }
        .bar-row {
          display: grid;
          grid-template-columns: 180px 1fr 80px;
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
        th, td {
          text-align: left;
          padding: 10px 8px;
          border-bottom: 1px solid var(--divider-color);
        }
        form { display: grid; gap: 12px; }
        input, select, textarea {
          width: 100%;
          padding: 10px 12px;
          border-radius: 10px;
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          color: var(--primary-text-color);
          box-sizing: border-box;
        }
        textarea { min-height: 100px; resize: vertical; }
        .primary {
          background: var(--primary-color);
          color: white;
          border: none;
          padding: 12px 16px;
          border-radius: 10px;
          cursor: pointer;
        }
        .actions { display: flex; gap: 12px; align-items: center; }
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

  contracts() {
    return Object.values(this._hass.states)
      .filter((state) => state.entity_id.startsWith("sensor.") && state.attributes.kündigungsfrist_datum)
      .map((state) => ({
        entity_id: state.entity_id,
        name: state.attributes.friendly_name || state.entity_id,
        provider: state.attributes.anbieter || "",
        category: state.attributes.kategorie || "",
        cost: Number(state.attributes.monatliche_kosten || 0),
        deadlineDays: Number(state.state || 0),
        deadlineDate: state.attributes.kündigungsfrist_datum || "",
        renewalDate: state.attributes.nächste_verlängerung || "",
      }))
      .sort((a, b) => a.deadlineDays - b.deadlineDays);
  }

  summary(contracts) {
    const total = contracts.reduce((sum, item) => sum + item.cost, 0);
    const urgent = contracts.filter((item) => item.deadlineDays <= 30).length;
    const next = contracts.length ? contracts[0] : null;
    return { total, urgent, next };
  }

  groupByCategory(contracts) {
    const grouped = {};
    for (const item of contracts) {
      grouped[item.category] = (grouped[item.category] || 0) + item.cost;
    }
    return Object.entries(grouped)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
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

  renderOverview(contracts) {
    const summary = this.summary(contracts);
    const costByContract = contracts.map((item) => ({ name: item.name, value: item.cost }));
    const costByCategory = this.groupByCategory(contracts);

    return `
      <div class="grid">
        <div class="card"><h3>Verträge</h3><div class="value">${contracts.length}</div></div>
        <div class="card"><h3>Gesamtkosten / Monat</h3><div class="value">${summary.total.toFixed(2)} €</div></div>
        <div class="card"><h3>Fristen ≤ 30 Tage</h3><div class="value">${summary.urgent}</div></div>
        <div class="card"><h3>Nächste Frist</h3><div class="value">${summary.next ? `${summary.next.deadlineDays} Tage` : "-"}</div></div>
      </div>
      <div class="split">
        <div class="card">
          <h3>Kosten pro Vertrag</h3>
          ${this.bars(costByContract)}
        </div>
        <div class="card">
          <h3>Kosten nach Kategorie</h3>
          ${this.bars(costByCategory)}
        </div>
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
              <th>Name</th>
              <th>Anbieter</th>
              <th>Kategorie</th>
              <th>Monatlich</th>
              <th>Kündigung in</th>
              <th>Fristdatum</th>
            </tr>
          </thead>
          <tbody>
            ${contracts.map((item) => `
              <tr>
                <td>${item.name}</td>
                <td>${item.provider}</td>
                <td>${item.category}</td>
                <td>${item.cost.toFixed(2)} €</td>
                <td>${item.deadlineDays} Tage</td>
                <td>${item.deadlineDate}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  renderCosts(contracts) {
    const costByContract = contracts.map((item) => ({ name: item.name, value: item.cost }));
    const costByCategory = this.groupByCategory(contracts);

    return `
      <div class="split">
        <div class="card">
          <h3>Monatliche Kosten je Vertrag</h3>
          ${this.bars(costByContract)}
        </div>
        <div class="card">
          <h3>Kosten je Kategorie</h3>
          ${this.bars(costByCategory)}
        </div>
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
            <div>${item.deadlineDays} T</div>
          </div>
        `).join("") : `<p class="hint">Noch keine Fristen vorhanden.</p>`}
      </div>
    `;
  }

  renderAdd() {
    return `
      <div class="card">
        <h3>Vertrag hinzufügen</h3>
        <form id="add-form">
          <input name="name" placeholder="Name des Vertrags" required>
          <select name="category" required>
            <option>Handy</option>
            <option>Strom</option>
            <option>Gas</option>
            <option>Internet</option>
            <option>Miete</option>
            <option>Versicherung</option>
            <option>Streaming</option>
            <option>Fitness</option>
            <option>Software</option>
            <option>Sonstiges</option>
          </select>
          <input name="provider" placeholder="Anbieter" required>
          <input name="cost" type="number" step="0.01" placeholder="Kosten pro Zyklus" required>
          <select name="cycle" required>
            <option>monatlich</option>
            <option>jährlich</option>
          </select>
          <input name="start_date" type="date" required>
          <input name="notice_days" type="number" value="30" required>
          <input name="duration_months" type="number" value="12" required>
	  <label style="display:inline-flex; align-items:center; gap:8px;">
	    <input name="auto_renew" type="checkbox" checked style="margin:0;">
	    Automatische Verlängerung
	  </label>
          <input name="contract_number" placeholder="Vertragsnummer">
          <input name="customer_number" placeholder="Kundennummer">
          <input name="notice_period_text" placeholder="Kündigungsfrist als Text">
          <input name="payment_day" placeholder="Abbuchungstag">
          <input name="portal_url" placeholder="Portal-URL">
          <input name="email" placeholder="Kontakt-E-Mail">
          <input name="phone" placeholder="Telefonnummer">
          <textarea name="notes" placeholder="Notizen"></textarea>
          <div class="actions">
            <button class="primary" type="submit">Vertrag anlegen</button>
            <span class="hint" id="result"></span>
          </div>
        </form>
      </div>
    `;
  }

  bindForm() {
    const form = this.querySelector("#add-form");
    if (!form || form.dataset.bound) return;
    form.dataset.bound = "1";

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const result = this.querySelector("#result");
      const data = Object.fromEntries(new FormData(form).entries());
      data.auto_renew = form.querySelector('[name="auto_renew"]').checked;
      data.cost = Number(data.cost || 0);
      data.notice_days = Number(data.notice_days || 0);
      data.duration_months = Number(data.duration_months || 0);

      try {
        await this._hass.callService("vertragsmanager", "create_contract", data);
        result.textContent = "Vertrag wurde angelegt.";
        form.reset();
      } catch (err) {
        result.textContent = `Fehler: ${err}`;
      }
    });
  }

  render() {
    if (!this._hass) return;

    const contracts = this.contracts();
    const pages = [
      ["overview", "Übersicht"],
      ["contracts", "Alle Verträge"],
      ["costs", "Kosten"],
      ["deadlines", "Fristen"],
      ["add", "Hinzufügen"]
    ];

    this.querySelector("#nav").innerHTML = pages.map(([key, label]) => `
      <button class="${this._page === key ? "active" : ""}" data-page="${key}">${label}</button>
    `).join("");

    let content = "";
    if (this._page === "overview") content = this.renderOverview(contracts);
    if (this._page === "contracts") content = this.renderContracts(contracts);
    if (this._page === "costs") content = this.renderCosts(contracts);
    if (this._page === "deadlines") content = this.renderDeadlines(contracts);
    if (this._page === "add") content = this.renderAdd();

    this.querySelector("#content").innerHTML = content;
    this.bindForm();
  }
}

if (!customElements.get("vertragsmanager-panel")) {
  customElements.define("vertragsmanager-panel", VertragsmanagerPanel);
}
