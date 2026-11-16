// Transparent, local matcher for the existing "Find a site" widget.
// It uses the generated public CSVs; it does not call an AI service or invent scores.

const MISSION_CANDIDATES = {
  rover: ["Kharga yardangs (Western Desert), Egypt", "Lut Desert (Dasht-e Lut), Iran", "Western Qaidam Basin, China"],
  dust: ["Bodélé Depression, Chad"],
  heat: ["Lut Desert (Dasht-e Lut), Iran"],
  cold: ["East Antarctic Plateau cold spots"],
  ice: ["Haughton Crater, Devon Island, Canada"],
  cave: ["Harrat Khaybar and Umm Jirsan lava tube, Saudi Arabia"],
  impact: ["Kamil Crater, Egypt", "Lonar Crater, India", "Haughton Crater, Devon Island, Canada"],
  life: ["Atacama Desert (Yungay), Chile", "Dallol, Danakil Depression, Ethiopia", "Río Tinto (Peña de Hierro), Spain", "Western Qaidam Basin, China"],
  drilling: ["Río Tinto (Peña de Hierro), Spain"],
};

const TASK_PATTERNS = [
  ["life", /\b(life detection|biosignature|biosignatures|habitability)\b/],
  ["cave", /\b(cave|caves|lava tube|lava tubes|shelter|underground habitat)\b/],
  ["impact", /\b(impact geology|crater sampling|ejecta|impact crater|crater)\b/],
  ["ice", /\b(ground ice|ice drilling|permafrost|ice mining)\b/],
  ["rover", /\b(rover|mobility|yardang driving)\b/],
  ["dust", /\b(dust mitigation|dust forecasting|dust storm|dust storms)\b/],
  ["heat", /\b(heat|thermal cycling|thermal stress|temperature cycling)\b/],
  ["cold", /\b(cold soak|cold-soak|cold testing)\b/],
  ["drilling", /\b(robotic drilling|drilling)\b/],
];

function parseCsv(text) {
  const rows = [];
  let row = [], cell = "", quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted && ch === '"' && text[i + 1] === '"') {
      cell += '"';
      i += 1;
    } else if (ch === '"') {
      quoted = !quoted;
    } else if (!quoted && ch === ",") {
      row.push(cell); cell = "";
    } else if (!quoted && (ch === "\n" || ch === "\r")) {
      if (ch === "\r" && text[i + 1] === "\n") i += 1;
      row.push(cell); rows.push(row); row = []; cell = "";
    } else {
      cell += ch;
    }
  }
  if (cell.length || row.length) { row.push(cell); rows.push(row); }
  const headers = (rows.shift() || []).map((value) => value.trim().replace(/^\uFEFF/, ""));
  return rows.filter((values) => values.some((value) => value.trim())).map((values) =>
    Object.fromEntries(headers.map((header, index) => [header, (values[index] || "").trim()]))
  );
}

let siteRowsPromise;
async function loadSites() {
  if (!siteRowsPromise) {
    siteRowsPromise = fetch(new URL("./data/sites.csv", import.meta.url))
      .then((response) => {
        if (!response.ok) throw new Error("The published site data could not be loaded.");
        return response.text();
      })
      .then(parseCsv)
      .then((rows) => rows.filter((row) => row.type === "earth"));
  }
  return siteRowsPromise;
}

function number(value) {
  if (value === undefined || value === null || value.trim() === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function bodyInQuery(query) {
  if (/\b(moon|lunar)\b/.test(query)) return "moon";
  if (/\b(mars|martian)\b/.test(query)) return "mars";
  return "";
}

function supportsBody(site, body) {
  if (!body) return true;
  const analog = (site.analog_for || "").toLowerCase();
  return analog.includes(body) || analog.includes("both");
}

function missionInQuery(query) {
  return TASK_PATTERNS.find(([, pattern]) => pattern.test(query))?.[0] || "";
}

function noMatch(message) {
  const result = [];
  result.message = message;
  return result;
}

export async function findMatches(query, limit = 2) {
  const text = query.toLowerCase();
  const body = bodyInQuery(text);
  const task = missionInQuery(text);
  const sites = await loadSites();

  if (task) {
    let candidates = sites.filter((site) =>
      MISSION_CANDIDATES[task].some((name) => name.toLowerCase() === site.name.toLowerCase()) &&
      supportsBody(site, body)
    );
    if (!candidates.length) {
      return noMatch(body
        ? `The team has no draft candidate for that task on ${body === "moon" ? "the Moon" : "Mars"} yet.`
        : "The team has no draft candidate for that task yet.");
    }
    const taskLabel = {
      rover: "rover mobility", dust: "dust mitigation and forecasting",
      heat: "heat and thermal cycling", cold: "cold-soak testing",
      ice: "ground-ice drilling", cave: "shelter in caves",
      impact: "impact geology and sampling", life: "life detection and biosignatures",
      drilling: "robotic drilling",
    }[task];
    return candidates.slice(0, limit).map((site) => ({
      name: site.name,
      ranked: false,
      reason: `Team-suggested candidate for ${taskLabel}; the project has no comparable score for this task, so candidates are unranked.`,
    }));
  }

  const criteria = [];
  if (/\b(low|less|little|minimal)\s+dust\b/.test(text)) criteria.push({ key: "dust_aod", label: "Dust optical depth (AOD)", unit: "", direction: 1 });
  else if (/\b(dust|dusty)\b/.test(text)) criteria.push({ key: "dust_aod", label: "Dust optical depth (AOD)", unit: "", direction: -1 });
  if (/\b(hot|hottest|warm|heat)\b/.test(text)) criteria.push({ key: "temp_max_c", label: "Maximum ground temperature", unit: " °C", direction: -1 });
  if (/\b(flat|flattest|gentle slope|low slope)\b/.test(text)) criteria.push({ key: body === "mars" ? "slope_463m_deg" : "slope_deg", label: "Slope", unit: "°", direction: 1 });
  if (/\b(steep|steepest|high slope)\b/.test(text)) criteria.push({ key: body === "mars" ? "slope_463m_deg" : "slope_deg", label: "Slope", unit: "°", direction: -1 });
  if (/\b(high sun|more sunlight|sunlight|sun angle)\b/.test(text)) criteria.push({ key: "sun_max_elev_deg", label: "Highest Sun angle", unit: "°", direction: -1 });
  if (/\b(low sun|less sunlight)\b/.test(text)) criteria.push({ key: "sun_max_elev_deg", label: "Highest Sun angle", unit: "°", direction: 1 });

  if (criteria.length > 1) {
    return noMatch("The project keeps conditions separate instead of combining them into one score. Ask about one measured condition at a time, or ask for a mission task.");
  }
  if (criteria.length === 0 && /\b(cold|coldest|freezing)\b/.test(text)) {
    return noMatch("Minimum ground-temperature values are not comparable in the current dataset. Try “cold-soak testing” for the team's unranked field-site suggestion.");
  }
  if (criteria.length === 0) {
    return noMatch("Try one measured condition (hot, flat for Moon, flat for Mars, dusty, low dust, high Sun) or a mission task (rover mobility, cave shelter, ground ice, impact sampling, life detection).");
  }

  const criterion = criteria[0];
  if ((criterion.key.startsWith("slope")) && !body) {
    return noMatch("For a slope comparison, specify the target body: for example, “flat for Moon” or “flat for Mars.”");
  }
  const ranked = sites
    .filter((site) => supportsBody(site, body))
    .map((site) => ({ site, value: number(site[criterion.key]) }))
    .filter((item) => item.value !== null)
    .sort((a, b) => criterion.direction * (a.value - b.value));
  if (!ranked.length) return noMatch("There are no comparable measurements for that condition in the current data.");

  return ranked.slice(0, limit).map(({ site, value }) => ({
    name: site.name,
    ranked: true,
    metric: { label: criterion.label, value, unit: criterion.unit },
    reason: `Ranked by this measured condition alone; other conditions are not combined.`,
  }));
}
