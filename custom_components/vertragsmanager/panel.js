class VertragsmanagerPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) {
      this._initialized = true;
      this._page = this._getPageFromUrl() || "overview";
      this.innerHTML = `
        <style>
          :host {
            display: block;
            padding: 16px;
            background: var(--primary-background-color);
            color: var(--primary-text-color);
            font-family: var(--primary-font-family);
          }
          .wrap {
            max-width: 1400px;
            margin: 0 auto;
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
          .card {
            background: var(--card-background-color);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid var(--divider-color);
          }
          .card h3 {
            margin: 0 0 12px 0;
          }
          .value {
            font-size: 1.8rem;
            font-weight: 700;
          }
          .layout {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 16px;
          }
          .list table {
            width: 100%;
            border-collapse: collapse;
          }
          .list th, .list td {
            text-align: left;
            padding: 10px 8px;
            border-bottom: 1px solid var(--divider-color);
          }
          .bar-row {
            display: grid;
            grid-template-columns: 160px 1fr 70px;
            gap: 12px;
            align-items: center;
            margin-bottom: 8px;
          }
          .bar {
            height: 12px;
            background: rgba(120,120,120,0.18);
            border-radius: 999px;
            overflow: hidden;
          }
          .bar > div {
            height: 100%;
            background: var(--primary-color);
          }
          form {
            display: grid;
            gap: 12px;
          }
          input, select, textarea {
            width: 100%;
            padding: 10px 12px;
            border-radius: 10px;
            border: 1px solid var(--divider-color);
            background: var(--card-background-color);
            color: var(--primary-text-color);
            box-sizing: border-box;
          }
          textarea {
            min-height: 100px;
            resize: vertical;
          }
          .actions {
            display: flex;
            gap: 12px;
            align-items: center;
          }
          .primary {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 12px 16px;
            border-radius: 10px;
            cursor: pointer;
          }
          .hint {
            color: var(--secondary-text-color);
            font-size: 0.95rem;
          }
          @media (max-width: 900px) {
            .layout {
              grid-template-columns: 1fr;
            }
          }
        </style>
        <div class="wrap">
          <div class="nav" id="nav"></div>
          <div id="content"></div>
        </div>
      `;
      this.querySelector("#nav").addEventListener("click", (e) => {
        const btn = e.target.closest("button[data-page]");
        if (!btn) return;
        this._page = btn.dataset.page;
        history.replaceState(null, "", `/vertragsmanager?page=${this._page}`);
        this._render();
      });
    }
    this._render();
  }

  _getPageFromUrl() {
    const url = new URL(window.location.href);
    return url.searchParams.get("page");
  }

  _contracts() {
    return Object.values(this._hass.states)
      .filter((s) => s.entity_id.startsWith("sensor.") && s.attributes.kündigungsfrist_datum)
      .map((s) => ({
        entity_id: s.entity_id,
        name: s.attributes.friendly_name || s.entity_id,
        provider: s.attributes.anbieter || "",
        category: s.attributes.kategorie || "",
        cost: Number(s.attributes.monatliche_kosten || 0),
        deadline_days: Number(s.state || 0),
        deadline_date: s.attributes.kündigungsfrist_datum || "",
        renewal: s.attributes.nächste_verlängerung || "",
      }))
      .sort((a, b) => a.deadline_days - b.deadline_days);
  }

  _summary(contracts) {
    const total = contracts.reduce((sum, c) => sum + c.cost, 0);
    const urgent = contracts.filter((c) => c.deadline_days <= 30).length;
    const next = contracts.length ? contracts[0] : null;
    return { total, urgent, next };
  }

  _groupByCategory(contracts) {
    const groups = {};
    for (const c of contracts) {
      groups[c.category] = (groups[c.category] || 0) + c.cost;
    }
    return Object.entries(groups)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }

  _renderBars(items, suffix = "€") {
    if (!items.length) return `<p class="hint">Noch keine Daten vorhanden.</p>`;
    const max = Math.max(...items.map((i) => i.value), 1);
    return items.map((i) => `
      <div class="bar-row">
        <div>${i.name}</div>
        <div class="bar"><div style="width:${(i.value / max) * 100}%"></div></div>
        <div>${i.value.toFixed(2)} ${suffix}</div>
      </div>
    `).join("");
  }

  _renderOverview(contracts) {
    const summary = this._summary(contracts);
    const contractBars = contracts.map((c) => ({ name: c.name, value: c.cost }));
    const categories = this._groupByCategory(contracts);

    return `
      <div class="grid">
        <div class="card"><h3>Verträge</h3><div class="value">${contracts.length}</div></div>
        <div class="card"><h3>Gesamtkosten / Monat</h3><div class="value">${summary.total.toFixed(2)} €</div></div>
        <div class="card"><h3>Kündigung in ≤ 30 Tagen</h3><div class="value">${summary.urgent}</div></div>
        <div class="card"><h3>Nächste Frist</h3><div class="value">${summary.next ? summary.next.deadline_days : "-"}${summary.next ? " Tage" : ""}</div></div>
      </div>

      <div class="layout">
        <div class="card">
          <h3>Kosten pro Vertrag</h3>
          ${this._renderBars(contractBars)}
        </div>
        <div class="card">
          <h3>Kosten nach Kategorie</h3>
          ${this._renderBars(categories)}
        </div>
      </div>
    `;
  }

  _renderContracts(contracts) {
    return `
      <div class="card list">
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
            ${contracts.map((c) => `
              <tr>
                <td>${c.name}</td>
                <td>${c.provider}</td>
                <td>${c.category}</td>
                <td>${c.cost.toFixed(2)} €</td>
                <td>${c.deadline_days} Tage</td>
                <td>${c.deadline_date}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  _renderCosts(contracts) {
    const contractBars = contracts.map((c) => ({ name: c.name, value: c.cost }));
    const categories = this._groupByCategory(contracts);

    return `
      <div class="layout">
        <div class="card">
          <h3>Monatliche Kosten je Vertrag</h3>
          ${this._renderBars(contractBars)}
        </div>
        <div class="card">
          <h3>Kosten je Kategorie</h3>
          ${this._renderBars(categories)}
        </div>
      </div>
    `;
  }

  _renderDeadlines(contracts) {
    const items = contracts.map((c) => ({
      name: c.name,
      value: Math.max(0, 365 - c.deadline_days),
      deadline_days: c.deadline_days,
      deadline_date: c.deadline_date,
    }));

    return `
      <div class="card">
        <h3>Fristen</h3>
        ${contracts.length ? contracts.map((c) => `
          <div class="bar-row">
            <div>${c.name}</div>
            <div class="bar"><div style="width:${Math.max(3, Math.min(100, ((365 - c.deadline_days) / 365) * 100))}%"></div></div>
            <div>${c.deadline_days} T</div>
          </div>
        `).join("") : `<p class="hint">Noch keine Fristen vorhanden.</p>`}
      </div>
      <div class="card" style="margin-top:16px;">
        <h3>Nächste Kündigungstermine</h3>
        <table>
          <thead>
            <tr><th>Vertrag</th><th>Frist in</th><th>Datum</th></tr>
          </thead>
          <tbody>
            ${contracts.map((c) => `
              <tr>
                <td>${c.name}</td>
                <td>${c.deadline_days} Tage</td>
                <td>${c.deadline_date}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  _renderAdd() {
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
          <input name="notice_days" type="number" step="1" placeholder="Kündigungsfrist in Tagen" required value="30">
          <input name="duration_months" type="number" step="1" placeholder="Laufzeit in Monaten" required value="12">
          <label><input name="auto_renew" type="checkbox" checked> Automatische Verlängerung</label>
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

  _bindForm() {
    const form = this.querySelector("#add-form");
    if (!form || form.dataset.bound) return;
    form.dataset.bound = "1";

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
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

  _render() {
    if (!this._hass) return;

    const contracts = this._contracts();
    const navItems = [
      ["overview", "Übersicht"],
      ["contracts", "Alle Verträge"],
      ["costs", "Kosten"],
      ["deadlines", "Fristen"],
      ["add", "Hinzufügen"],
    ];

    this.querySelector("#nav").innerHTML = navItems.map(([key, label]) => `
      <button class="${this._page === key ? "active" : ""}" data-page="${key}">${label}</button>
    `).join("");

    let html = "";
    if (this._page === "overview") html = this._renderOverview(contracts);
    if (this._page === "contracts") html = this._renderContracts(contracts);
    if (this._page === "costs") html = this._renderCosts(contracts);
    if (this._page === "deadlines") html = this._renderDeadlines(contracts);
    if (this._page === "add") html = this._renderAdd();

    this.querySelector("#content").innerHTML = html;
    this._bindForm();
  }
}

customElements.define("vertragsmanager-panel", VertragsmanagerPanel);
