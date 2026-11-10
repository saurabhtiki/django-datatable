/* Pop-ups for the server-side table (templates/django_datatable/).
   The panel uses position: fixed so the table's sideways scroll box can't cut it off.
   Loaded before Alpine starts (both deferred, this one first). */
/* Small helpers: the browser may block storage (private window), so never let it break the page. */
const dtRead = (key, fallback) => {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? fallback;
  } catch (error) {
    return fallback;
  }
};
const dtWrite = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    /* not remembered, still works for this page */
  }
};

/* Row height is set on <html> at once (before the table is drawn), so there is no flicker. */
const DT_LEVELS = ["compact", "normal", "roomy"];
const dtLevel = () => {
  const saved = dtRead("dt-density", "normal");
  return DT_LEVELS.includes(saved) ? saved : "normal";
};
document.documentElement.dataset.dtDensity = dtLevel();

document.addEventListener("alpine:init", () => {
  Alpine.data("dtDensity", () => ({
    level: dtLevel(),
    set(level) {
      this.level = level;
      document.documentElement.dataset.dtDensity = level;
      dtWrite("dt-density", level);
    },
  }));

  // "Columns" menu. Hidden column names are remembered per table; the toolbar is redrawn with
  // the table on every click, so init() hides them again each time.
  Alpine.data("dtColumns", (tableId) => ({
    open: false,
    hidden: [],
    init() {
      this.hidden = dtRead(`dt-cols:${tableId}`, []);
      this.apply();
    },
    toggle(name) {
      this.hidden = this.hidden.includes(name)
        ? this.hidden.filter((item) => item !== name)
        : [...this.hidden, name];
      dtWrite(`dt-cols:${tableId}`, this.hidden);
      this.apply();
    },
    showAll() {
      this.hidden = [];
      dtWrite(`dt-cols:${tableId}`, []);
      this.apply();
    },
    apply() {
      const table = document.querySelector(`#${CSS.escape(tableId)} table`);
      if (!table) return;
      const heads = [...table.querySelectorAll("thead th")];
      heads.forEach((head, index) => {
        const name = head.dataset.dtCol;
        if (!name) return; // e.g. the Actions column: always shown
        const hide = this.hidden.includes(name);
        table.querySelectorAll("tr").forEach((row) => {
          const cell = row.children[index];
          // Skip the "Nothing matches" row, whose one cell spans every column.
          if (cell && row.children.length === heads.length) cell.hidden = hide;
        });
      });
    },
  }));

  Alpine.data("dtPopup", () => ({
    open: false,
    style: {},
    toggle() {
      if (this.open) return this.close();
      this.place();
      this.open = true;
      this.$nextTick(() => this.$refs.panel.querySelector("input:not([type=hidden])")?.focus());
    },
    close() {
      this.open = false;
    },
    place() {
      const box = this.$refs.button.getBoundingClientRect();
      const screen = window.innerWidth;
      const phone = screen < 640;
      const width = phone ? screen - 32 : 288;
      const left = phone ? 16 : Math.max(16, Math.min(box.left, screen - width - 16));
      let top = box.bottom + 6;
      // Little room below the button (short screen): move the pop-up up so it stays on screen.
      if (window.innerHeight - top < 320) top = Math.max(16, window.innerHeight - 16 - 400);
      const height = window.innerHeight - top - 16;
      // An object (not a string) so Alpine merges it with x-show's display: none.
      this.style = { top: `${top}px`, left: `${left}px`, width: `${width}px`, maxHeight: `${height}px` };
    },
  }));

  Alpine.data("dtChoice", () => ({
    search: "",
    matches(label) {
      return label.toLowerCase().includes(this.search.trim().toLowerCase());
    },
    // Ticks or unticks only the values still shown after "Find a value".
    setAll(on) {
      this.$root.querySelectorAll("label[data-label]").forEach((row) => {
        if (this.matches(row.dataset.label)) row.querySelector("input").checked = on;
      });
    },
  }));
});
