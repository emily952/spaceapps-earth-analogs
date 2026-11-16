const sites = [
  { name: "Harrat Khaybar and Umm Jirsan lava tube, Saudi Arabia", slope: 3.78, maxTemp: 60.03, dust: 0.34, sunAngle: 87.94 },
  { name: "Kamil Crater, Egypt", slope: 2.94, maxTemp: 57.69, dust: 0.3, sunAngle: 90 },
  { name: "Lonar Crater, India", slope: 2, maxTemp: 51.95, dust: 0.52, sunAngle: 90 },
  { name: "East Antarctic Plateau cold spots", slope: 1.04, maxTemp: -24.19, dust: 0, sunAngle: 33.07 },
  { name: "Lut Desert (Dasht-e Lut), Iran", slope: 0.64, maxTemp: 73.25, dust: 0.32, sunAngle: 82.84 },
  { name: "Kharga yardangs (Western Desert), Egypt", slope: 2.15, maxTemp: 55.49, dust: 0.32, sunAngle: 87.99 },
  { name: "Western Qaidam Basin, China", slope: 3.46, maxTemp: 59.51, dust: 0.27, sunAngle: 75.4 },
  { name: "Bodélé Depression, Chad", slope: 1.08, maxTemp: 62.87, dust: 0.57, sunAngle: 90 },
  { name: "Dallol, Danakil Depression, Ethiopia", slope: 0.45, maxTemp: 58.31, dust: 0.4, sunAngle: 90 },
  { name: "Río Tinto (Peña de Hierro), Spain", slope: 11.04, maxTemp: 50.93, dust: 0.16, sunAngle: 75.72 },
  { name: "Atacama Desert (Yungay), Chile", slope: 5.3, maxTemp: 56.89, dust: 0.04, sunAngle: 89.37 },
  { name: "Haughton Crater, Devon Island, Canada", slope: 7.42, maxTemp: 14.91, dust: 0.07, sunAngle: 38.06 },
];

// words the user might type -> which number they care about
const traits = [
  { words: ["flat", "low slope", "smooth"], key: "slope", want: "low" },
  { words: ["steep", "high slope", "rugged"], key: "slope", want: "high" },
  { words: ["hot", "high temp", "warm", "heat"], key: "maxTemp", want: "high" },
  { words: ["cold", "low temp", "freezing", "cool"], key: "maxTemp", want: "low" },
  { words: ["dusty", "high dust"], key: "dust", want: "high" },
  { words: ["low dust", "clear", "clean air"], key: "dust", want: "low" },
  { words: ["high sun", "bright"], key: "sunAngle", want: "high" },
  { words: ["low sun", "dim"], key: "sunAngle", want: "low" },
];

function range(key) {
  const vals = sites.map((s) => s[key]);
  return [Math.min(...vals), Math.max(...vals)];
}

export function findMatches(userInput, topN = 3) {
  const text = userInput.toLowerCase();
  const wanted = traits.filter((t) => t.words.some((w) => text.includes(w)));

  return sites
    .map((s) => {
      let score = 0;
      for (const t of wanted) {
        const [min, max] = range(t.key);
        const n = (s[t.key] - min) / (max - min); // 0 to 1
        score += t.want === "high" ? n : 1 - n;
      }
      return { ...s, score: wanted.length ? score / wanted.length : 0 };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, topN);
}
