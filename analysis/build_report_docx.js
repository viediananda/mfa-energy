// Builds reports/MFA Group2 Report Updated.docx from the draft text, the model tables and the figures.
// Run: NODE_PATH=<dir with docx installed> node analysis/build_report_docx.js
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, AlignmentType, HeadingLevel,
  WidthType, BorderStyle, ShadingType, LevelFormat, Footer, PageNumber, PageBreak,
} = require('docx');

const ROOT = path.resolve(__dirname, '..');
const FIG = path.join(ROOT, 'reports', 'figures');
const OUT = path.join(ROOT, 'reports', 'MFA Group2 Report Updated.docx');
const PAGE_W = 9026; // A4 text width in DXA with 1" margins

// ---------------------------------------------------------------- helpers
const children = [];
let figN = 0, tabN = 0;
const run = (t, o = {}) => new TextRun({ text: t, ...o });
function runs(text, extra = {}) {
  // *italic* and **bold** spans; extra = options applied to every run (size, bold, italics)
  const parts = []; const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g; let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) parts.push(run(text.slice(last, m.index), extra));
    const s = m[0];
    parts.push(s.startsWith('**') ? run(s.slice(2, -2), { ...extra, bold: true }) : run(s.slice(1, -1), { ...extra, italics: true }));
    last = m.index + s.length;
  }
  if (last < text.length) parts.push(run(text.slice(last), extra));
  return parts;
}
const P = (t, o = {}) => children.push(new Paragraph({ children: runs(t), spacing: { after: 140, line: 300 }, ...o }));
const H1 = t => children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [run(t)], spacing: { before: 360, after: 160 } }));
const H2 = t => children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [run(t)], spacing: { before: 240, after: 120 } }));
const H3 = t => children.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: [run(t)], spacing: { before: 180, after: 80 } }));
const B = items => items.forEach(t => children.push(new Paragraph({ numbering: { reference: 'bul', level: 0 }, children: runs(t), spacing: { after: 80, line: 290 } })));
const EQ = t => children.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [run(t, { italics: true })], spacing: { before: 60, after: 140 } }));
const brk = () => children.push(new Paragraph({ children: [new PageBreak()] }));

function pngSize(file) { const b = fs.readFileSync(file); return [b.readUInt32BE(16), b.readUInt32BE(20)]; }
function FIGURE(name, caption, widthIn = 6.2) {
  const file = path.join(FIG, name + '.png'); const [w, h] = pngSize(file);
  const wpx = Math.round(widthIn * 96), hpx = Math.round(wpx * h / w);
  figN += 1;
  children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: true,
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(file), transformation: { width: wpx, height: hpx },
      altText: { title: `Figure ${figN}`, description: caption, name: name } })] }));
  children.push(new Paragraph({ alignment: AlignmentType.LEFT, spacing: { after: 200, line: 260 },
    children: [run(`Figure ${figN}. `, { bold: true, size: 19 }), ...runs(caption, { size: 19 })] }));
  return figN;
}
const border = { style: BorderStyle.SINGLE, size: 4, color: 'BFC5C1' };
const borders = { top: border, bottom: border, left: border, right: border };
function TABLE(caption, cols, rows, widths, opts = {}) {
  tabN += 1;
  children.push(new Paragraph({ keepNext: true, spacing: { before: 160, after: 80 }, children: [run(`Table ${tabN}. `, { bold: true, size: 19 }), run(caption, { size: 19 })] }));
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, i, head) => new TableCell({
    borders, width: { size: widths[i], type: WidthType.DXA }, margins: { top: 60, bottom: 60, left: 100, right: 100 },
    shading: head ? { fill: 'E2EEE9', type: ShadingType.CLEAR } : undefined,
    children: [new Paragraph({ alignment: (!head && opts.numCols && opts.numCols.includes(i)) ? AlignmentType.RIGHT : AlignmentType.LEFT,
      children: runs(String(t), head ? { bold: true, size: 18 } : { size: 19 }), spacing: { after: 0 } })],
  });
  const tr = (r, head) => new TableRow({ tableHeader: head, cantSplit: true, children: r.map((t, i) => cell(t, i, head)) });
  children.push(new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: [tr(cols, true), ...rows.map(r => tr(r, false))] }));
  if (opts.note) children.push(new Paragraph({ spacing: { before: 60, after: 200 }, children: runs(opts.note, { italics: true, size: 18 }) }));
  else children.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
  return tabN;
}

// ---------------------------------------------------------------- numbers (from reports/tables)
function csv(name) {
  const lines = fs.readFileSync(path.join(ROOT, 'reports', 'tables', name), 'utf8').trim().split(/\r?\n/);
  const parse = l => { const out = []; let cur = '', q = false; for (const ch of l) { if (ch === '"') q = !q; else if (ch === ',' && !q) { out.push(cur); cur = ''; } else cur += ch; } out.push(cur); return out; };
  const head = parse(lines[0]); return lines.slice(1).map(l => Object.fromEntries(parse(l).map((v, i) => [head[i], v])));
}
const f0 = x => Math.round(+x).toLocaleString('en-GB');
const f1 = x => (+x).toLocaleString('en-GB', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const H = Object.fromEntries(csv('headline.csv').map(r => [r.metric, r]));
const h = (m, d = 0) => { const r = H[m]; const f = d ? f1 : f0; return { b: f(r.base), r: `${f(r.P5)}-${f(r.P95)}` }; };
const MT = Object.fromEntries(csv('model_measures.csv').map(r => [r.measure, r]));
const EXITS = csv('model_exits_draft_format.csv');
const HOT = Object.fromEntries(csv('model_exergy_hotspots.csv').map(r => [r.process, r]));

// ---------------------------------------------------------------- title page
children.push(new Paragraph({ spacing: { before: 2400, after: 200 }, alignment: AlignmentType.CENTER, children: [run('Industrial Energy Flow Analysis', { bold: true, size: 40 })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [run('Case Study of Holmen Hallsta Paper Mill', { size: 30 })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 800 }, children: [run('Material Flow Analysis (AL2144)', { size: 24 })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [run('Authors: Aman Dawar, Miao Long, Valliammai Meyyappan, Viedi Ananda Rizqia, Yuhe Yang', { size: 22 })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [run('Date: 14 October 2026', { size: 22 })] }));
brk();

// ---------------------------------------------------------------- summary
H1('Summary');
P(`Holmen's Hallsta mill near Norrtälje makes paper from thermo-mechanical pulp (TMP) and runs almost entirely on purchased electricity: 1,450 GWh in 2023, plus 2.8 GWh of diesel for vehicles. We built an annual energy and exergy balance for the mill, checked every input against the available sources, and tested the results with 10,000 Monte Carlo runs.`);
P(`TMP refining takes about 70 % of the electricity (1,015 GWh) and returns 430 GWh of it as recovered steam. Electric boilers add 130 GWh, so TMP supplies 77 % of the mill's steam, which fits Holmen's own statement that recovery covers 70-90 % of steam need. Almost all energy leaves as low-temperature heat. About 684 GWh/y can be assigned to a specific exit and 769 GWh/y has to be found by difference. In exergy terms, 1,328 GWh (92 %) of the electricity's ability to do work is destroyed inside the mill, mostly in TMP refining (802 GWh), then the paper machines (290 GWh) and the electric boilers (100 GWh). This order held in every accepted Monte Carlo run.`);
P(`Three measures that reduce boiler electricity were assessed. Better TMP steam recovery saves about 48 GWh/y, a 2-point increase in press dryness about 38 GWh/y, and a high-temperature heat pump in place of the boilers 88-104 GWh/y. Together they could save 94-126 GWh/y, lowering specific electricity use from 3.26 to 2.98-3.05 MWh per tonne of paper. The lower figure allows for summer months when the mill already has surplus steam.`);

// ---------------------------------------------------------------- 1
H1('1. Introduction and background');
P(`Sweden is pushing for full electrification in industry, transport and buildings (Swedish Government, 2022). This puts increasing strain on the country's grids. The pulp and paper industry is one of Sweden's biggest industrial electricity users, and thermo-mechanical pulping (TMP) is known as one of the most power-intensive industrial processes in the world (Talebjedi et al., 2021).`);
P(`Holmen's Hallsta paper mill, near Norrtälje, is a large TMP-based mill. It stopped burning fossil fuels on site in 2014, and today almost all its energy comes from purchased electricity. A small amount of diesel is used by vehicles and machines in the wood yard (Holmen Paper AB, 2024). In the TMP process, refiners use large amounts of electricity to separate the wood fibres, and most of that electricity ends up as heat. Part of this heat is recovered as steam and reused for paper drying and heating (Holmen Q&A, 2019).`);
P(`The TMP refiners are therefore the mill's biggest electricity user and also its main source of steam. This creates a trade-off: if the refiners use less electricity, they also produce less recoverable heat, and the electric boilers have to make up the difference. An energy audit that looks at single pieces of equipment cannot capture this link, so we analysed the energy flows of the whole mill. Lower electricity demand at large users like Hallsta also frees grid capacity, which matters for Sweden's electrification goals (Swedish Government, 2022).`);

// ---------------------------------------------------------------- 2
H1('2. Aim and objectives');
H2('2.1 Aim');
P(`This project maps the energy and exergy flows at Holmen's Hallsta paper mill, identifies where energy is lost and where its quality is destroyed, and tests how much the results depend on uncertain data. The goal is to support well-founded decisions on energy efficiency at the mill.`);
H2('2.2 Objectives');
P(`The study answers three research questions:`);
B(['How does energy flow through the Hallsta mill?', 'Where do the energy and exergy analyses locate the main hotspots?', 'How robust are these findings?']);

// ---------------------------------------------------------------- 3
H1('3. Hallsta paper mill, system boundary and delimitations');
H2('3.1 Mill description');
P(`Hallsta paper mill is located near Norrtälje, Sweden, and produces paper from thermo-mechanical pulp. In 2023 the mill produced 444,494 tonnes of finished paper and 421,883 tonnes of TMP pulp (Holmen Paper AB, 2024, Table 3). Pulp is made in the TMP3 and TMP12 refiner lines and paper on two Valmet paper machines, PM11 and PM12. The mill has not burned fossil fuels for production since 2014. Wood is debarked on site, and the bark is sold as fuel.`);
H2('3.2 Energy system');
P(`Electricity is the mill's main energy source, 1,450 GWh in 2023 (Holmen Paper AB, 2024, Table 13). According to Holmen, it is split between four groups of users (Holmen Q&A, 2025):`);
B([`TMP refining, about 70 % of the electricity. Most of this electricity ends up as heat, and about 100 t/h of steam is recovered from the refiners.`,
   `Electric boilers EP1 and EP2, about 10 %. They produce about 1.5 t of steam per MWh of electricity.`,
   `Paper machines including bleaching, about 15 %. The drying section is the main steam user, at about 80-110 t/h.`,
   `Other processes, about 5 %, including the wastewater treatment plant (WWTP), wood handling, compressors and other utilities.`]);
H2('3.3 System boundary');
P(`The system boundary is the mill gate (Figure 1). Inside it are TMP refining, the electric boilers, the steam network, the paper machines with their drying sections, the WWTP and the supporting operations. Purchased electricity (1,450 GWh/y) and diesel (2.8 GWh/y) are the energy inputs that cross the boundary. Paper is the product. Energy leaves as district heat delivered to Norrtälje Energi and as waste heat in wastewater, cooling water and exhaust air. Recovered TMP steam, boiler steam and the heat-recovery loops (warm water, preheating) are internal flows. They are balanced inside the boundary and are not counted as inputs.`);
P(`The energy content of the wood raw material, and of the bark sold as fuel (about 204 GWh in 2023), is outside the scope. The analysis follows purchased electricity and diesel.`);
FIGURE('diagram_system_boundary', 'System boundary and main energy flows at Hallsta paper mill, 2023. Values are annual flows from the baseline model described in Section 4. Dashed items are outside the energy analysis.');
H2('3.4 Reference year and delimitations');
P(`2023 is the most recent year covered by the mill's environmental report (Holmen Paper AB, 2024). The model is steady-state and annual. Steam flows given in tonnes per hour are annualised with 7,200 operating hours, which is the production-weighted running time of PM11 (285.3 days) and PM12 (314 days) in 2023, 7,174 hours, rounded (Holmen Paper AB, 2024, Table 4).`);
P(`2023 was not a typical year. Production (444 kt) was the second lowest of 2019-2023 and specific electricity use (3.26 MWh/t) the highest. The environmental report explains this with planned stops when electricity prices were high, market-related stops, a three-month outage of the biological treatment stage, and extra refining on line L12 to hold pulp quality (Holmen Paper AB, 2024, section 1.2.1). Per-tonne figures in this report are therefore somewhat above those of a typical year (Section 4.2).`);
P(`Delimitations:`);
B([`Short-term dynamics are not modelled. This includes start-ups and shutdowns, seasonal changes and variations in electricity prices.`,
   `Upstream effects (wood supply, electricity generation) and downstream effects (use and disposal of the paper) are outside the energy boundary. They are only discussed qualitatively in the screening LCA (Section 8).`,
   `Steam flows, temperatures and the split of electricity between processes are mill estimates or standard values rather than measurements. Section 6 treats them as uncertain.`]);

// ---------------------------------------------------------------- 4
H1('4. Methodology and data sources');
P(`Figure 2 shows how the work was done. We first collected every relevant number from the sources and screened them for trends and conflicts. The chosen inputs then feed an energy balance, an exergy analysis and a Monte Carlo uncertainty analysis. The improvement measures and the screening LCA build on these results.`);
FIGURE('diagram_method', 'Workflow of the study. The shaded steps are calculated in the Python model; every table and figure in Sections 5-7 is produced by it.', 6.4);
H2('4.1 Data sources and data quality');
P(`The analysis draws on the mill's environmental report for 2023 (Miljörapport), Holmen's written answers to student questions from 2019 and 2025, and an undated Holmen slide on the mill's main energy flows (Table 1). Every value used was entered in a source register with its document, location and year, so it can be traced.`);
TABLE('Data sources used in the study.', ['Source', 'What it provides', 'Data year', 'Quality'], [
  ['Miljörapport 2023, Hallsta (Holmen Paper AB, 2024)', 'Electricity, diesel, production, operating days, effluent volumes, district heat, five-year energy table', '2023 (2019-2023)', 'High: audited report'],
  ['Holmen Q&A (2025)', 'Electricity shares, steam flows, boiler steam yield, electric loads, TMP energy per tonne, water balance', '2024-2025', 'Medium: rounded estimates'],
  ['Holmen Q&A (2019)', 'Steam pressure and condensate temperature, effluent temperature, metered line electricity for August 2019', '2019', 'Medium-low: older data'],
  ['Holmen study visit answers (2019)', 'Three-year average electricity split, district heat 2019', '2019', 'Medium-low'],
  ['Holmen slide "Viktiga energiflöden" (n.d.)', 'Energy flows per tonne of paper, used for cross-checks', 'Undated, probably 2015-2017', 'Medium'],
], [2500, 3700, 1300, 1526]);
P(`Total electricity, diesel, paper production, wastewater volume and district heat come from the audited report and are reliable. The electricity split and the steam flows are Holmen's estimates given in 2025 and applied to 2023, and some temperatures date from 2019. Where sources disagree, Appendix A lists the value used and the reason.`);

H2('4.2 Data screening');
P(`Before building the model, we compared the source data across years and documents. This screening answers three practical questions: is 2023 a fair reference year, how far can Holmen's rounded shares be trusted, and are the steam and water figures consistent with each other.`);
P(`Figure 3 shows the five-year record from the environmental report. Electricity use and production move together, but in 2023 production fell more than electricity, so specific use rose to the highest value in the period. The environmental report adds that specific use also increased in periods of full production, so the stops are not the whole explanation (Holmen Paper AB, 2024, section 1.2.1). We kept 2023 as the reference year because it has the most complete data, and we note that its per-tonne figures are on the high side.`);
FIGURE('eda_context', 'Electricity use, paper production and specific energy consumption at Hallsta, 2019-2023 (Miljörapport Table 13). Production for 2019-2022 is derived from electricity divided by specific consumption; for 2023 the reported value (444,494 t) is also shown. 2023 is shaded.');
P(`Figure 4 compares the electricity split from four sources. TMP stays at about 2.2-2.3 MWh per tonne of paper in all of them. The electric boilers, however, rise from 0.12 MWh/t on the undated Holmen slide to about 0.33 MWh/t when Holmen's 2025 shares are applied to 2023. This matches the environmental report, which says that shortfalls in TMP steam recovery and hot-water heat recovery lead to high electricity use in the boilers (Holmen Paper AB, 2024, section 1.2.1). The spread between the sources is also the reason why the uncertainty analysis gives the electricity shares a coefficient of variation of 10 %.`);
FIGURE('eda_electricity_split', 'Electricity split by process in four data sources, in MWh per tonne of paper (left) and as shares (right). The August 2019 meter values cover one month and only TMP and the paper machines, so they are shown as shares only.');
P(`Figure 5 compares recovered TMP steam per tonne of paper. The Holmen slide gives 1.2 MWh per tonne (1.8 t of steam), while Holmen's 2025 figure of 100 t/h gives about 1.06 MWh per tonne on the same full-heat basis. Recovery per tonne has fallen by roughly 12 %, which again points to the boilers covering a larger part of steam demand. Two other steam figures in the sources, about 10,000 GJ per month and 145,000 GJ with no period stated, are far too small to describe all recovered TMP steam unless the larger one is read as a monthly figure. They were used only as cross-checks.`);
FIGURE('eda_tmp_steam', 'Recovered TMP steam per tonne of paper (left) and relative to TMP electricity (right), for each source. Hatched bars use an assumed period where the source gives none. Bars use the full heat of steam (2.35 GJ/t) so they can be compared with the slide; on the latent-heat basis used in the model, TMP returns 42 % of its electricity as steam.');
P(`Figure 6 summarises the water flows that carry heat out of the mill. The audited 2023 effluent volume (7.29 Mm³) agrees with Holmen's rough 2024 balance (7 Mm³). The 2024 balance also shows 4 Mm³/y of cooling water and other unaffected water released without treatment, which the draft of this study could only estimate. District heat deliveries rose from about 4.4 GWh in 2019 to 11.9 GWh in 2023.`);
FIGURE('eda_water_heat', 'Water volumes in 2023 (Miljörapport) and in Holmen\'s rough 2024 balance (top), effluent flow 2019-2023 (bottom left) and district heat delivered in 2019 and 2023 (bottom right).');

H2('4.3 Energy balance');
P(`We built a steady-state annual energy balance for 2023 inside the mill boundary. All flows are in GWh per year, and specific energy is given in MWh per tonne of finished paper. Based on conservation of energy, we compute the external inputs, the recovered internal heat, the useful outputs and the waste-heat exits. The balance has three layers: where the electricity goes, how steam is produced and used, and where the energy finally leaves the mill. The results are shown as a Sankey diagram.`);
H2('4.4 Steam and heat flow estimation');
P(`Steam flows are converted to energy with 7,200 operating hours per year and a latent heat of 2.15 GJ per tonne, the heat released when steam at 2.4 bar(g) and 138 °C condenses. Counting the full heat down to the 90 °C condensate that Holmen reports (2.35 GJ/t) would raise all steam flows by about 9 %, but it does not change the exergy results or the savings of the measures (sensitivity case S5 in Section 6). The steam demand of the drying section is cross-checked against the heat needed to evaporate the water, using a post-press dryness of 48 % and a final moisture content of 7 %.`);
H2('4.5 Exergy analysis');
P(`Exergy is the part of an energy flow that could still do useful work. It complements the first-law energy balance by showing where the quality of energy is lost. The reference environment is set to 7 °C (280 K), a typical annual mean for the surroundings, inside the 2-25 °C range Holmen gives for incoming water. We calculate the exergy efficiency of the main process units, including the electric boilers and TMP refining. This shows where high-quality electricity is turned into low-value heat, and which waste-heat flows are worth recovering. Diesel (0.2 % of the energy input, used by vehicles) is included in the energy balance but not in the exergy analysis. Table 2 lists the equations.`);
TABLE('Exergy equations.', ['Energy carrier', 'Exergy equation'], [
  ['Electricity', 'Ex = E'], ['Heat at constant temperature', 'Ex = Q(1 - T0/T)'],
  ['Warm water or wastewater', 'Ex = m·cp·[(T - T0) - T0·ln(T/T0)]'], ['Steam', 'Ex = m·(Δh - T0·Δs)'],
  ['Process exergy efficiency', 'ηex = Ex,useful / Ex,in'], ['Improvement potential', 'IP = (1 - ηex)·(Ex,in - Ex,useful)'],
], [3500, 5526]);
H2('4.6 Uncertainty analysis');
P(`Many internal process values are mill estimates rather than measurements, so we tested how much they matter. The analysis has three stages: classifying the inputs by data quality, propagating their uncertainty with Monte Carlo simulation, and ranking the inputs by influence. Each input gets a probability distribution based on the quality of its source (Table 6 in Section 6). Values from the audited report get narrow normal distributions, and estimates and assumptions get wider triangular or uniform ones.`);
P(`The simulation runs 10,000 trials. In each trial every input is drawn from its distribution, the electricity shares are rescaled so that the total stays at 1,450 GWh, and one value of operating hours is used for all steam flows, since steam generation and drying run on the same schedule. A trial is kept only if it agrees with what is known about the mill: TMP supplies 70-90 % of the steam, as Holmen reports, no steam flow becomes negative, and the boilers do not deliver more steam heat than the electricity they use. Spearman rank correlation and one-at-a-time sensitivity show which inputs drive the results, which in turn shows which data are worth measuring.`);
H2('4.7 Improvement measures');
P(`We use the baseline energy and exergy results to assess measures that reduce the electricity used by the electric boilers. The measures are compared by electricity saved per year and per tonne of paper, with ranges from the Monte Carlo analysis and a lower bound for seasons with surplus steam. The assessment keeps in view the core trade-off: cutting TMP electricity reduces load on the grid, but it also reduces the steam recovered.`);
H2('4.8 Screening LCA');
P(`A screening-level, qualitative LCA was carried out for the selected measures. It looks at mill-gate operations and the main upstream and downstream links, to find early environmental trade-offs related to electricity use and waste-heat recovery. It does not produce quantitative LCA results.`);

// ---------------------------------------------------------------- 5
H1('5. Baseline results');
H2('5.1 Energy');
P(`The energy balance follows the first law of thermodynamics. In steady state, the energy entering the mill equals the energy leaving it; steam circulating inside the mill is an internal flow and does not appear in the external balance:`);
EQ('E_in = E_out');
H3('Electricity allocation');
P(`Hallsta used 1,450 GWh of electricity in 2023 and about 2.82 GWh of diesel for internal transport, mainly heavy vehicles in the wood yard. The total operational energy input is:`);
EQ('E_in = E_electricity + E_diesel = 1,450 + 2.82 ≈ 1,453 GWh/y');
P(`The electricity is divided between the processes using Holmen's shares: TMP 70 %, paper machines including bleaching 15 %, electric boilers 10 %, and other processes including the WWTP, utilities, wood handling and internal grid losses 5 %. These shares are approximate operating values from Holmen, not measurements. Appendix B gives the details.`);
EQ('E_electricity = E_TMP + E_PM + E_EB + E_other = 1,015 + 218 + 145 + 73 = 1,450 GWh/y');
H3('Steam loop');
P(`A large part of the electricity supplied to TMP becomes heat, and about 100 t/h of steam is recovered from it (Holmen Q&A, 2025). With 7,200 operating hours and a latent heat of 2.15 GJ/t:`);
EQ('E_TMP,steam = 100 t/h × 7,200 h × 2.15 GJ/t ÷ 3,600 ≈ 430 GWh/y');
EQ('E_TMP,residual = 1,015 - 430 = 585 GWh/y');
P(`So 42 % of the electricity used in TMP comes back as useful steam. The rest leaves as heat in the pulp and process water, in exhaust vapour, and as steam vented in summer.`);
P(`The electric boilers make steam when recovered TMP steam is insufficient. Holmen states that they produce 1.5 tonnes of steam per MWh of electricity. With 145 GWh/y of boiler electricity:`);
EQ('E_EB,steam = 145,000 MWh × 1.5 t/MWh × 2.15 GJ/t ÷ 3,600 ≈ 130 GWh/y');
P(`The remaining 15 GWh/y is not a boiler loss; electric boilers turn about 98 % of their electricity into steam heat. It is the heat used to raise the feedwater from 90 °C condensate to boiling, which the latent-heat convention does not count as steam.`);
P(`The estimated steam supply is therefore 430 + 130 = 560 GWh/y. TMP supplies 77 % of it, within the 70-90 % recovery rate that Holmen reports (Holmen Q&A, 2025). This independent check supports the estimated steam flows.`);
P(`PM drying uses about 408 GWh/y, taking the middle of Holmen's range of 80-110 t/h:`);
EQ('E_PM,drying = 95 t/h × 7,200 h × 2.15 GJ/t ÷ 3,600 ≈ 408 GWh/y');
P(`The remaining steam, 560 - 408 - 22 (distribution losses) = 130 GWh/y, goes to other heat uses: warm-water production, wood handling and building heat. In summer, when no heavy preheating of fresh water is needed, excess steam may be vented. Only about 16 GWh/y of these other uses is documented (11.9 GWh of district heat and about 4.4 GWh of domestic heating). The size of this term depends mostly on the drying steam, which is known only as a range; at 110 t/h it falls to about 60 GWh/y. Heat is also recovered outside the steam system: heat from the drying section preheats incoming process water, and heat from wastewater and compressor cooling produces warm water and district heat.`);
H3('Check of the drying steam');
P(`Finished paper has about 7 % moisture, and the paper leaves the Valmet press section at about 48 % dryness. For 444,494 t of paper this means that 416,700 t of water must be evaporated per year. With an evaporation heat of about 2.4 GJ per tonne of water (including heating it to boiling):`);
EQ('Q_evap = 416,700 t × 2.4 GJ/t ÷ 3,600 ≈ 278 GWh/y');
P(`So 278 GWh of the 408 GWh/y of drying steam evaporates water, and about 130 GWh/y heats the paper web and air or leaves with the hood exhaust. This 68 % share is in the normal range for paper dryers, which supports the estimate of 95 t/h.`);
H3('Where the energy leaves the mill');
P(`In steady state, all of the 1,453 GWh/y of electricity and diesel entering the mill leaves it, almost all as heat. Table 3 lists the exits. About 47 % of the input can be assigned to a specific exit. The largest is the dryer exhaust air (408 GWh/y), since all steam delivered to the dryers ends up in the moist exhaust air; part of this heat is recovered to preheat incoming water before it leaves. The dryer rows are estimated from the drying steam flow rather than measured. The wastewater is the second-largest assigned exit, 212 GWh/y.`);
const exitRows = EXITS.map(r => {
  const label = r.exit.replace('Electric boiler residual (condensate heat not counted at latent basis)', 'Electric boiler residual (condensate heat, see 5.1)').replace('  of which: cooling water, estimated (4 Mm3/y, 5-15 K)', '   of which cooling water, estimated (4 Mm³/y, 5-15 K)');
  const basis = {
    'District heat to Norrtälje Energi': 'Miljörapport 2023 (11,877 MWh)',
    'Dryer exhaust air: latent heat in evaporated water': '416,700 t water × 2.4 GJ/t',
    'Dryer exhaust air and hood losses: residual drying heat': '408 - 278 GWh/y drying steam',
    'Wastewater to Edeboviken': '7.29 Mm³ × 4.18 MJ/m³K × (32 - 7) K',
    'Electric boiler residual (condensate heat not counted at latent basis)': '145 - 130 GWh/y',
    'Steam distribution losses': '4 % of 560 GWh/y (assumption)',
    'Internal electrical grid losses': '1 % of electricity (assumption)',
    'Not individually quantified (by difference)': '1,453 - 684',
    '  of which: cooling water, estimated (4 Mm3/y, 5-15 K)': 'Holmen water balance 2024',
    'Total = energy input': '= energy input',
  }[r.exit] || '';
  return [label, f1(r.base_GWh), `${f0(r.P5)}-${f0(r.P95)}`, basis];
});
TABLE('Energy exits from the mill (GWh/y). The range is the P5-P95 interval from the Monte Carlo analysis (Section 6).', ['Exit route', 'GWh/y', 'Range', 'Basis'], exitRows, [3500, 1000, 1100, 3426], { numCols: [1, 2] });
P(`The remaining 769 GWh/y (53 %) could not be assigned to a single exit and was calculated by difference. This is not missing energy. It is heat leaving the mill through routes that are not measured. Based on the process description, it is mostly:`);
B([`Unrecovered TMP heat. Of the 1,015 GWh/y supplied to TMP, about 585 GWh/y is not recovered as steam. It leaves as heat in the hot pulp and process water (about 80 °C), in exhaust vapour from refining and steam recovery, and as steam vented in summer when supply exceeds demand.`,
   `Heat from the paper-machine drives. The 218 GWh/y of paper-machine electricity drives pumps, vacuum systems, fans and rolls, and ends up as heat in process water and hall ventilation air.`,
   `Cooling water. Holmen's 2024 water balance shows about 4 Mm³/y of cooling water and other unaffected water released without treatment. At a temperature rise of 5-15 K it carries an estimated 25-70 GWh/y (46 GWh/y at 10 K).`,
   `Other heat uses: the 130 GWh/y of other steam uses, and heat lost through building ventilation and radiation from hot equipment and pipes.`]);
P(`The by-difference term also absorbs any error in the assigned exits. If the effluent were at 20 °C instead of 32 °C, it would rise to about 870 GWh/y. Narrowing it would require measured data on summer steam venting, cooling-water temperature and exhaust-air conditions.`);

H2('5.2 Specific energy consumption');
P(`Because electricity is the main energy input, specific electricity consumption was calculated on the 2023 production of 444,494 tonnes of finished paper:`);
EQ('SEC_electricity = 1,450,000 MWh ÷ 444,494 t = 3.26 MWh/t paper');
P(`Applied to each process, the result is 2.28 MWh/t for TMP, 0.49 MWh/t for the paper machines and 0.33 MWh/t for the electric boilers.`);
P(`Per tonne of pulp, TMP uses 2,406 kWh/t (70 % of 1,450 GWh over 421,883 t). This is above the 1,500-2,000 kWh/t that Holmen describes as a normal span for refining, plus 150 kWh/t for auxiliary drives (Holmen Q&A, 2025). Two independent plant-level figures, the undated Holmen energy-flow slide (about 2,320 kWh/t) and the metered line data for August 2019 (about 2,330 kWh/t), both point to roughly 2,320 kWh/t. This suggests that Holmen's normal span describes refiner operation rather than the plant's annual average, which also includes reject refining, idling and restarts. The 2023 value is about 4 % higher, consistent with the extra refining on line L12 and the price-driven stops described in the environmental report. We therefore keep the 70 % share. Using the top of Holmen's normal span instead (2,150 kWh/t) would leave about 108 GWh/y of electricity with no identified user (sensitivity case S6).`);

H2('5.3 Exergy');
P(`Energy measures quantity, while exergy measures quality: the share of energy that could still do work relative to the surroundings at T0 = 7 °C. Exergy is calculated from the temperature of each energy carrier using the equations in Table 2. Table 4 gives the resulting exergy factors. For steam, the factor is given per unit of latent heat so that it can be applied directly to the steam flows in Section 5.1.`);
TABLE('Exergy per unit of energy for each energy carrier.', ['Energy carrier', 'Temperature', 'Exergy per unit energy'], [
  ['Electricity', '-', '1'], ['Steam, 2.4 bar(g), condensing to 90 °C (per unit of latent heat)', '138 °C', '0.344'],
  ['District heat (supply/return)', '85/45 °C', '0.171'], ['Unrecovered TMP heat (pulp, water)', '80 °C', '0.111'],
  ['Hot process water', '60 °C', '0.084'], ['Paper-machine waste heat', '55 °C', '0.077'], ['Effluent', '32 °C', '0.042'],
], [5000, 1800, 2226], { numCols: [2] });
P(`Paper-machine waste heat is taken at 55 °C, between the roughly 50 °C of the paper-machine wastewater (Holmen Q&A, 2019) and the warmer dryer exhaust air.`);
P(`Of the 1,450 GWh of exergy supplied as electricity, 1,328 GWh (92 %) is destroyed inside the mill. About 120 GWh leaves with waste heat (111 GWh to air, 9 GWh to water) and only 2 GWh leaves as district heat.`);
H2('5.4 Hotspots');
P(`The energy view shows where heat leaves without being reused, and it points at the paper machines: all the drying steam ends up as warm exhaust. That heat is at about 55 °C, so it carries only about 47 GWh of exergy. It is useful for preheating fresh water or for district heating, not for making steam. The exergy view shows where high-quality electricity is degraded, and it points at TMP refining and the electric boilers (Table 5 and Figure 7).`);
const hot = (k, lab) => { const r = HOT[k]; return [lab, f0(r['Exergy in']), f0(r['Useful out']), `${Math.round(r.psi * 100)} %`, f0(r['Improvement potential'])]; };
const other = ['Bleaching', 'WWTP', 'Wood handling', 'Utilities & other (residual / unexplained)', 'Internal grid losses'].reduce((s, k) => s + +HOT[k]['Exergy in'], 0);
TABLE('Exergy by process (GWh/y). IP is the improvement potential from Table 2: it ranks where exergy is lost and is not an achievable saving.', ['Process', 'Exergy in', 'Useful exergy out', 'Exergy efficiency ψ', 'IP'], [
  hot('TMP plant', 'TMP plant'), hot('Paper machines', 'Paper machines'), hot('Electric boilers', 'Electric boilers'),
  hot('Steam to hot water, heating and venting (unallocated)', 'Hot water and heating'),
  ['Bleaching, WWTP, wood handling, utilities, grid losses', f0(other), '0', '0 %', `${f0(other)} (no single item above 22)`],
  hot('Steam network', 'Steam network'),
], [3300, 1300, 1500, 1500, 1426], { numCols: [1, 2, 3, 4] });
P(`Units without a useful exergy output, such as the paper machines, bleaching, the WWTP and wood handling, have ψ = 0 by convention. Separating fibres and drying paper are real work, but they have no standard exergy value, so their exergy counts as destroyed. This affects ψ and IP but not the ranking by exergy destroyed.`);
FIGURE('model_hotspots', 'Heat leaving each process (energy view, grey) and exergy destroyed in each process (red), GWh/y. The boiler energy-view value reflects the latent-heat convention and is not a measured boiler loss.', 6.0);
H2('5.5 Sankey diagrams');
P(`Figure 8 shows the energy flows. Of the 1,452.8 GWh/y entering the mill, TMP refining uses 1,015 GWh/y (70 %) and returns 430 GWh/y as recovered steam. Together with 130 GWh/y from the electric boilers, this gives a steam supply of 560 GWh/y (77 % from TMP), mainly for paper drying (408 GWh/y). Almost all energy finally leaves as low-grade heat. The largest assigned exits are the dryer exhaust air (408 GWh/y) and the wastewater (212 GWh/y), and only 11.9 GWh/y is delivered as district heat. In total, 47 % of the input can be assigned to a specific exit; the remaining 769 GWh/y (53 %) is found by difference.`);
FIGURE('model_sankey_energy', 'Energy flows at Hallsta paper mill, 2023 (GWh/y). Blue: electricity. Orange: steam (latent heat, 2.15 GJ/t). Grey: low-grade waste heat. Green: water and district heat. "Other users" are bleaching, the WWTP, wood handling, utilities and grid losses.', 6.4);
P(`Figure 9 shows the same system in exergy terms. Most of the electricity's exergy is destroyed in TMP refining. The steam that TMP and the boilers hand on carries only about a third of its energy as exergy, and almost none of it is left by the time the heat leaves the mill.`);
FIGURE('model_sankey_exergy', 'Exergy flows at Hallsta paper mill, 2023 (GWh/y of exergy; diesel excluded). Steam exergy factor 0.344 per unit of latent heat. "Useful hot water" (10 GWh) is used in the mill and for district heat (2 GWh); apart from the district heat it also ends as waste heat.', 6.4);

// ---------------------------------------------------------------- 6
H1('6. Uncertainty analysis');
H2('6.1 Purpose and approach');
P(`The baseline in Section 5 uses single values, but several of them are mill estimates or standard values. This section tests how robust the energy and exergy results and the hotspot ranking are to those inputs. The method has three steps: classify the inputs by data quality, propagate their uncertainty with Monte Carlo simulation, and rank the inputs by influence.`);
H2('6.2 Input uncertainty classification');
P(`Inputs are grouped by source quality, and each group gets a distribution and a coefficient of variation (CV), as shown in Table 6. Inputs not listed (for example the electric loads of the WWTP and wood handling, and the waste-heat temperatures) get ranges around their stated values; Appendix A lists them all.`);
TABLE('Input uncertainty classification for the Monte Carlo simulation.', ['Input', 'Baseline value', 'Source quality', 'Distribution'], [
  ['Total electricity', '1,450 GWh/y', 'Official report', 'Normal, CV 2 %'], ['Diesel', '2.82 GWh/y', 'Official report', 'Normal, CV 5 %'],
  ['Paper production', '444,494 t/y', 'Official report', 'Normal, CV 1 %'], ['Wastewater volume', '7,288,861 m³/y', 'Official report', 'Normal, CV 2 %'],
  ['Wastewater temperature', '32 °C (20 in long shutdowns)', 'Holmen statement', 'Triangular (20, 32, 32)'],
  ['Electricity shares (TMP/PM/EB/other)', '70/15/10/5 %', 'Mill estimate', 'Normal, CV 10 %, rescaled to 100 %'],
  ['TMP steam recovery', '100 t/h', 'Mill estimate', 'Triangular (85, 100, 115)'], ['PM drying steam', '95 t/h (80-110)', 'Reported range', 'Triangular (80, 95, 110)'],
  ['Electric boiler steam yield', '1.5 t steam/MWh', 'Mill statement', 'Normal, CV 5 %'],
  ['Operating hours', '7,200 h/y', 'Derived (7,174 h)', 'Triangular (6,800, 7,200, 7,800), one value per trial for all steam flows'],
  ['Steam latent heat', '2.15 GJ/t', 'Standard value', 'Normal, CV 3 %'], ['Evaporation heat', '2.4 GJ/t', 'Standard value', 'Normal, CV 2 %'],
  ['Post-press dryness', '48 %', 'Typical value', 'Triangular (45, 48, 51) %'], ['Reference temperature T0', '7 °C (280 K)', 'Assumption', 'Uniform (5, 10) °C'],
], [2500, 2100, 1700, 2726]);
H2('6.3 Monte Carlo simulation');
P(`10,000 trials were run with a fixed random seed, so the results can be reproduced. In each trial every input is drawn from its distribution and the full energy and exergy balance is recalculated. The electricity shares are rescaled in each trial so that they add up to 1,450 GWh; otherwise the balance would not close. Operating hours are drawn once per trial and used for TMP steam, boiler steam and drying steam alike, since these are not independent.`);
P(`A trial is kept only if it is consistent with what is known about the mill. TMP must supply 70-90 % of the steam (Holmen Q&A, 2025), no steam flow may be negative, no process may destroy negative exergy, and the boilers may not deliver more steam heat than the electricity they use. About 97 % of the trials pass. The rejected trials combine low TMP recovery with high drying steam, or draw a boiler steam yield and latent heat whose product exceeds the electricity input.`);
H2('6.4 Results');
const R = (m, lab, d) => { const x = h(m, d); return [lab, x.b, x.r]; };
TABLE('Monte Carlo results: baseline value and the range containing 90 % of accepted trials (P5-P95).', ['Result', 'Baseline', 'P5-P95'], [
  R('Electricity to TMP plant', 'Electricity to TMP (GWh/y)'), R('Electricity to electric boilers', 'Electricity to electric boilers (GWh/y)'),
  R('Recovered TMP steam', 'Recovered TMP steam (GWh/y)'), R('Electric-boiler steam', 'Electric-boiler steam (GWh/y)'),
  R('Share of steam from TMP', 'Share of steam from TMP (%)', 1), R('Steam to hot water, heating and venting (unallocated)', 'Other steam uses, unallocated (GWh/y)'),
  ['Wastewater heat (GWh/y)', f0(EXITS.find(r => r.exit.startsWith('Wastewater')).base_GWh), `${f0(EXITS.find(r => r.exit.startsWith('Wastewater')).P5)}-${f0(EXITS.find(r => r.exit.startsWith('Wastewater')).P95)}`],
  ['Not individually quantified (GWh/y)', f0(EXITS.find(r => r.exit.startsWith('Not individually')).base_GWh), `${f0(EXITS.find(r => r.exit.startsWith('Not individually')).P5)}-${f0(EXITS.find(r => r.exit.startsWith('Not individually')).P95)}`],
  R('Exergy destroyed, total', 'Exergy destroyed, total (GWh/y)'), R('Exergy destroyed, TMP plant', 'Exergy destroyed, TMP (GWh/y)'),
  R('Exergy destroyed, paper machines', 'Exergy destroyed, paper machines (GWh/y)'), R('Exergy destroyed, electric boilers', 'Exergy destroyed, electric boilers (GWh/y)'),
  R('Exergy efficiency of electric boilers', 'Exergy efficiency of electric boilers (%)', 1), R('TMP specific electricity', 'TMP specific electricity (kWh/t pulp)'),
], [5000, 1800, 2226], { numCols: [1, 2] });
P(`Table 7 gives the results. The main conclusions hold across the whole range. TMP refining ranks first in exergy destroyed in 100 % of accepted trials, followed by the paper machines and then the electric boilers, also in every trial. TMP supplies 73-81 % of the steam, inside Holmen's 70-90 %. Exergy destruction stays at 91-92 % of the electricity input. The least certain results are the unallocated steam (55-190 GWh/y) and the wastewater heat, which depends on the effluent temperature. Figure 10 shows the distributions.`);
FIGURE('model_mc_hist', 'Distribution of selected results across accepted Monte Carlo trials. The orange line is the baseline and the dashed lines are P5 and P95.', 6.4);
H2('6.5 Sensitivity ranking');
P(`Figure 11 moves each input to its own P5 and P95 values while holding the others at baseline, for the two measure results that depend most on uncertain data. Spearman rank correlations across all accepted trials give the same picture. The findings for each result are:`);
B([`*Other steam uses (steam surplus).* Whether the mill has spare steam depends mostly on two estimates that pull in opposite directions: the PM drying steam (ρ = -0.65) and the TMP steam recovered (ρ = +0.62). Neither is measured.`,
   `*PM drying residual.* This is the drying steam minus the heat needed for evaporation. It depends mainly on the drying steam and then on the post-press dryness; wetter paper after the press leaves a smaller residual.`,
   `*Wastewater heat loss.* This depends almost only on the effluent temperature, which we know only as about 32 °C, falling to 20 °C in long shutdowns. The loss lies between about 123 and 214 GWh/y (P5-P95). The volume hardly matters.`,
   `*TMP exergy efficiency.* It goes up with the steam recovered from the refiners and down with the TMP share of electricity.`,
   `*TMP exergy loss and specific energy.* These depend mainly on the TMP share of electricity (70 %) and on total electricity. The share is a mill estimate, so a different true share would shift both results.`,
   `*Savings from the measures.* All measures replace boiler steam, so their savings depend most on the boiler share of electricity (ρ ≈ 0.73), then on the TMP share. Holmen's 2019 and 2025 answers differ on the boiler share (6 % and 10 %).`]);
FIGURE('model_tornado', 'One-at-a-time sensitivity: each input moved to its own P5 (grey) and P95 (blue) with the others at baseline. Left: saving if TMP supplied 90 % of the steam. Right: combined saving of all measures.', 6.4);
H2('6.6 Sensitivity cases');
P(`Some questions cannot be expressed as a range, so they were run as separate cases (Table 8). None of them changes the hotspot ranking.`);
TABLE('Sensitivity cases and their effect on the main results (GWh/y).', ['Case', 'What changes'], [
  ['S1: 2019 electricity split (72/22/6 %)', 'Boiler electricity falls to 84 GWh/y, TMP supplies 85 % of steam, combined savings fall to 84 GWh/y.'],
  ['S3: drying steam 110 t/h', 'Other steam uses fall from 123 to 58 GWh/y.'],
  ['S5: steam counted to 90 °C condensate (2.35 GJ/t)', 'All steam flows rise 9 %; exergy results and measure savings unchanged.'],
  ['S6: TMP at 2,150 kWh/t (Holmen normal span)', 'TMP electricity 907 GWh/y; 126 GWh/y of electricity has no identified user.'],
  ['S7 and S10: effluent at 39 °C or 20 °C', 'Wastewater heat about 271 or 110 GWh/y; only the split between water and air changes.'],
  ['S8: steam flows over 8,760 h', 'TMP share of steam 80 %; combined savings 133 GWh/y.'],
  ['S2: reference temperature 25 °C', 'Exergy destroyed rises to 1,367 GWh/y.'],
], [3600, 5426]);

// ---------------------------------------------------------------- 7
H1('7. Assessment of improvement measures');
P(`All three measures aim to reduce the use of the electric boilers, which turn high-quality electricity into steam at about 31 % exergy efficiency. With the baseline values, every tonne per hour of boiler steam avoided saves about 4.8 GWh/y of electricity (7,200 h ÷ 1.5 t/MWh). The boilers currently supply about 30 t/h, which caps the total saving at about 145 GWh/y, so the measures are not fully additive.`);
P(`The savings below assume that the boilers would otherwise run all year. Holmen reports that surplus steam is sometimes vented in summer but rarely in winter (Holmen Q&A, 2025). When steam is vented, the boilers are off and none of the measures saves electricity. We therefore also give a lower bound with no saving in June-August (75 % of the full-year value). The true saving lies between the two.`);
P(`**Measure 1: improved TMP steam recovery.** Only 42 % of TMP electricity is recovered as steam, and the environmental report names TMP steam recovery as the mill's main improvement potential (Holmen Paper AB, 2024). Raising recovery from 100 to 110 t/h would replace 10 t/h of boiler steam and save about 48 GWh/y (0.11 MWh/t paper), or 36 GWh/y with the seasonal lower bound.`);
P(`**Measure 2: heat pump instead of electric boilers.** A high-temperature heat pump could upgrade TMP waste heat (about 80 °C) to 138 °C steam. Industrial heat pumps reach a coefficient of performance (COP) of about 2.2-2.8 at a temperature lift of 70 K and more at smaller lifts (Arpagaus et al., 2018); the lift here is about 58 K, so we use a COP of 2.5-3.5. The heat pump has to supply the full heat of the steam, including raising the feedwater from 90 °C, which is about 142 GWh/y. Replacing all boiler steam would then save 88-104 GWh/y (0.20-0.23 MWh/t) and also reduce the heat discharged to Edeboviken. The technology is still emerging at this temperature, investment costs are high, and synthetic refrigerants may add a leakage risk.`);
P(`**Measure 3: higher press dryness.** Increasing paper dryness after the press from 48 % to 50 % (for example with a shoe press or better felts) reduces the water the dryers must evaporate by about 8 %. Assuming drying steam scales with the water evaporated, this saves about 7.9 t/h of steam, or 38 GWh/y (0.09 MWh/t); counting only the evaporation heat it would be about 5 t/h. Harder pressing may reduce paper bulk, which matters for book paper.`);
const m = k => MT[k];
TABLE('Electricity saved by each measure (GWh/y). The full-year value assumes the boilers run all year; the seasonal lower bound assumes no saving in June-August. P5-P95 is the Monte Carlo range of the full-year value.', ['Measure', 'Full year', 'Seasonal lower bound', 'P5-P95', 'MWh/t paper', 'Main trade-off'], [
  ['1. TMP steam recovery +10 t/h', f0(m('M1').base_GWh), f0(m('M1').base_GWh * 0.75), `${f0(m('M1').P5_GWh)}-${f0(m('M1').P95_GWh)}`, (+m('M1').base_MWh_t).toFixed(2), 'No saving during summer surplus'],
  ['2. Heat pump (COP 2.5-3.5)', '88-104', '66-78', `${f0(m('M2').P5_GWh)}-${f0(m('M2').P95_GWh)}`, '0.20-0.23', 'Emerging technology, cost, less grid flexibility'],
  ['3. Press dryness 48 to 50 %', f0(m('M3').base_GWh), f0(m('M3').base_GWh * 0.75), `${f0(m('M3').P5_GWh)}-${f0(m('M3').P95_GWh)}`, (+m('M3').base_MWh_t).toFixed(2), 'Paper quality (bulk)'],
  ['Combined (3, then 1, then heat pump)', f0(m('M4').base_GWh), f0(m('M4').base_GWh * 0.75), `${f0(m('M4').P5_GWh)}-${f0(m('M4').P95_GWh)}`, (+m('M4').base_MWh_t).toFixed(2), 'Less grid flexibility'],
], [2500, 950, 1150, 1000, 1000, 2426], { numCols: [1, 2, 3, 4] });
FIGURE('model_measures', 'Electricity saved by each measure, full-year values, baseline with P5-P95 ranges. M1b shows the saving if TMP supplied 90 % of the steam, the top of Holmen\'s range; M3b counts only the evaporation heat saved by Measure 3.', 6.2);
P(`Table 9 and Figure 12 summarise the savings. The heat pump gives the largest saving but carries the most risk, while improved steam recovery builds on existing systems. Combined, the measures could reduce specific electricity use from 3.26 to 2.98-3.05 MWh/t. Reducing refining energy directly is less effective than it seems: a 10 % cut saves about 95 GWh/y in refining, but about half of that is lost because less steam is recovered and the boilers must make up the difference.`);
H2('7.1 Comparison of measures');
P(`The three measures differ in size, certainty and risk. The heat pump (Measure 2) gives the largest saving, 88-104 GWh/y, and the largest exergy gain, since it upgrades existing waste heat instead of converting electricity directly into steam. However, it is the least mature option at the required steam temperature and needs the highest investment. Improved TMP steam recovery (Measure 1) saves about half as much (48 GWh/y) but builds on existing systems and directly targets the mill's largest exergy loss. Higher press dryness (Measure 3) gives the smallest saving (38 GWh/y) and may affect paper bulk, but it reduces steam demand rather than changing the steam supply, so it works independently of the other two.`);
P(`Because all three measures replace the same boiler steam (about 30 t/h), their savings cannot simply be added. Combined, they could save 94-126 GWh/y. The size of every saving depends most on how much electricity the boilers really use, which is the least certain of Holmen's three shares (Section 6.5). Measures 1 and 3 are the most realistic short-term options, while the heat pump is a longer-term option once the technology is proven at this scale.`);

// ---------------------------------------------------------------- 8
H1('8. Screening LCA');
H2('8.1 Scope, system boundary and baseline');
P(`The assessment is qualitative. It looks at the possible effects of the measures on climate and environment at different stages of the life cycle, without detailed quantitative calculations.`);
P(`The scope covers the mill itself and the related upstream and downstream stages. Upstream are electricity generation and the supply of pulpwood. Downstream are the effect of drying on paper properties, the thermal load of the wastewater, and the use of surplus heat. The baseline is the mill's operation in 2023: 1,450 GWh of purchased electricity, 2.82 GWh/y of diesel on site, and the electric boilers EP1 and EP2 using 145 GWh/y of electricity to supply about 130 GWh/y (about 30 t/h) of production steam. All measures are judged by how much of this boiler load they avoid.`);
H2('8.2 Climate impact');
P(`**Measure 1: improved TMP steam recovery.** Lower boiler electricity directly reduces the mill's indirect (Scope 2) greenhouse gas emissions. At the level of the power system, the freed capacity can be used elsewhere on the grid and may displace marginal fossil generation. The measure only improves heat recovery; it does not change refining intensity or pulp yield, so the amount of wood harvested is not affected. Its limitation is that it assumes a steam shortage all year. In summer the mill already has surplus steam that is vented, and more recovery then saves nothing. Rebuilding equipment and pipes also brings some embodied emissions from metal.`);
P(`**Measure 2: heat pump instead of electric boilers.** A heat pump upgrades waste heat in the TMP process water (about 80 °C) to 138 °C steam and replaces the resistive electric boilers. This reduces the electricity footprint of the mill. It can also reduce thermal pollution downstream: heat taken from the process water is not discharged to Edeboviken bay, which lowers the risk of local warming and reduced dissolved oxygen. The obstacles are cost and engineering complexity. If the heat pump uses synthetic fluorinated refrigerants, small leaks during operation may offset part of the emission reduction. Electric boilers can also start and stop quickly and help balance the grid, which the mill uses today when it offers demand flexibility (Holmen Paper AB, 2024); a compressor heat pump is much less flexible.`);
P(`**Measure 3: higher press dryness.** This measure reduces energy demand at the source, so the dryers need less steam without any extra heat-exchange loop. On the other hand, harder pressing compresses the fibres and reduces the bulk (thickness) of the paper. If product quality suffers, scrap and rework in printing may increase, which adds material and energy use later in the life cycle.`);
H2('8.3 LCA comparison');
P(`In terms of possible emission reductions, Measure 2 has the largest single effect, with a net electricity saving of 88-104 GWh/y. Taking heat from the process water also clearly reduces the thermal load on Edeboviken bay. Measures 1 and 3 save 48 and 38 GWh/y. Their savings are smaller, but they do not depend on complex new thermal equipment and are easier to carry out.`);

// ---------------------------------------------------------------- 9
H1('9. Discussion');
H2('9.1 Which improvements look most promising');
P(`Taking both emissions and practical constraints into account, the measures have different risks and returns over different time frames.`);
P(`In the short term, Measure 1 is the most promising. It builds on the existing heat-recovery units and pipes, the cost of the changes can be controlled, and it hardly disturbs daily production. Steam surplus in summer reduces its annual benefit (to about 36 GWh/y in the lower bound), but its technical maturity and low process risk make it the most reliable saving.`);
P(`Measure 2 has the largest theoretical saving but needs a high investment and complex integration. High-temperature industrial heat pumps are still at the demonstration stage, and the choice and maintenance of working fluids make a large-scale rebuild uncertain both technically and financially. Measure 3 changes the core settings of the paper machines' press section, where there is little room for process changes that affect quality.`);
H2('9.2 How uncertainty affects the results');
P(`The Monte Carlo analysis shows a clear difference between mill-level and process-level results. The mill-level conclusions are robust. Total electricity, diesel and paper production come from the audited environmental report, and the central findings hold in every accepted trial: the mill runs almost entirely on electricity, TMP is the largest user, and the ranking of exergy destruction (TMP, then the paper machines, then the electric boilers) never changes. A mill-level decarbonisation target can rely on these conclusions.`);
P(`The steam balance is less certain. Whether the mill has surplus steam depends on the difference between TMP steam recovery and the drying demand, and both are estimates based on operating experience. The unallocated steam varies from about 55 to 190 GWh/y across the trials. Depending on the combination, the electric boilers could be a regular source of steam or an occasional backup, and the size of every saving depends most on the boiler share of electricity. Before deciding to retire the electric boilers, the mill would need measured steam flows to avoid a risk of steam shortage.`);
H2('9.3 Limitations');
P(`The model is an annual steady-state calculation over 7,200 operating hours. It smooths out hourly peaks and troughs, as well as price variations on the Nordic electricity market (Nord Pool). It does not cover seasonal mismatches such as high heating demand in very cold winters or steam venting in summer, nor the transient behaviour during start-ups, stops and maintenance. The other main limitations are:`);
B([`The 2023 TMP share is an estimate. Holmen's 70 % share and its normal refining range disagree; we keep 70 %, which is supported by two independent plant-level figures (Section 5.2). This does not change the ranking, since TMP is first in every case.`,
   `Steam flows are rounded estimates, and only about 16 GWh/y of the 130 GWh/y of other steam uses is documented.`,
   `Every saving scales with the boiler share of electricity, which Holmen gave as 6 % in 2019 and 10 % in 2025. The order of the measures does not change.`,
   `53 % of the energy outflow is found by difference, because there are no measurements of exhaust air or cooling-water temperature.`,
   `The effluent and condensate temperatures date from 2019, before the treatment plant was rebuilt in 2020.`,
   `The heat pump COP comes from a literature review, so the savings of Measure 2 are indicative.`,
   `The data come from different years: core 2023 data from the environmental report, electricity shares and steam flows from 2025, and some temperatures from 2019. 2023 itself was an unusual year.`]);

// ---------------------------------------------------------------- 10
H1('10. Conclusions');
P(`This study carried out an energy and exergy analysis of Holmen's Hallsta paper mill for the reference year 2023. A steady-state annual energy balance was built within the mill-gate boundary to find the energy and exergy hotspots, and a Monte Carlo analysis tested how robust they are. Improvement measures and a qualitative screening LCA were also assessed for this fully electrified TMP mill.`);
P(`The mill's total energy input was 1,453 GWh in 2023, almost all of it purchased electricity (1,450 GWh). TMP refining uses about 70 % of the electricity and is also the mill's main source of steam. This creates a trade-off: less electricity to TMP reduces grid load but also reduces the recovered steam available for drying and heating. Specific electricity use was 3.26 MWh per tonne of paper, high for the mill because of the stops in 2023. About 47 % of the energy outflow could be assigned to specific exits, while more than half (769 GWh/y) could only be calculated by difference, mainly unrecovered TMP heat, heat from the paper-machine drives and cooling water.`);
P(`The exergy results show that 92 % of the electricity's exergy is destroyed in the mill, above all in the TMP refiners and the electric boilers, which are the main improvement hotspots. These conclusions held in every accepted Monte Carlo trial. The internal steam figures are less certain, which makes the steam surplus and the role of the electric boilers harder to pin down.`);
P(`Of the three measures, the heat pump offers the largest saving (88-104 GWh/y), but the technology is not yet mature at this temperature and the investment is high. Improved TMP steam recovery and higher press dryness are lower-risk options that build on the existing equipment. Together, the measures could reduce specific electricity use from 3.26 to 2.98-3.05 MWh per tonne of paper. The screening LCA is qualitative, and it points to the heat pump's lower thermal load on Edeboviken bay and to the loss of grid flexibility as the main trade-offs.`);
P(`The work is limited by its annual steady-state model, which ignores hourly dynamics and seasonal steam venting. Future work could add dynamic simulation and a full life-cycle assessment to weigh energy efficiency upgrades against grid capacity relief.`);

// ---------------------------------------------------------------- 11
H1('11. Contribution and self-reflection');
P(`Aman Dawar: system boundary and delimitation, energy system and time frame, uncertainty analysis, Monte Carlo simulation in Excel and a Python script run in Visual Studio Code, Sankey diagram and tornado charts.`);
P(`Miao Long: took part in the early stages of the energy system boundary flow chart and the definition of data quality. Wrote the screening LCA and the Discussion.`);
P(`Valliammai Meyyappan: contributed to the baseline energy results and carried out the calculations for the electricity allocation, the steam loop (TMP steam recovery, electric boilers and PM drying) and the loss accounting, including the table of final energy and exergy exits.`);
P(`Viedi Ananda Rizqia: carried out the energy and exergy calculations and created the energy and exergy diagrams.`);
P(`Yuhe Yang: took part in the preliminary definition of the system boundary, and drafted the introduction, aims, methodology and conclusions.`);

// ---------------------------------------------------------------- 12
H1('12. References');
const refs = [
  'Arpagaus, C., Bless, F., Uhlmann, M., Schiffmann, J. and Bertsch, S.S. (2018). High temperature heat pumps: Market overview, state of the art, research status, refrigerants, and application potentials. *Energy*, 152, pp. 985-1010. https://doi.org/10.1016/j.energy.2018.03.166',
  'Holmen Paper AB (2024). *Miljörapport 2023, Hallsta pappersbruk*. Annual environmental report for Hallsta paper mill, Norrtälje.',
  'Holmen Q&A (2019). Answers to compiled student questions, Hallsta paper mill. Personal communication.',
  'Holmen (2019). Questions for the study visit, answers from Hallsta. Personal communication.',
  'Holmen Q&A (2025). Answers to student questions after the Hallsta study visit (ANRA 251021). Personal communication.',
  'Holmen (n.d.). *Viktiga energiflöden, Hallsta PB*. Presentation slide. Unpublished.',
  'Morris, A.E., Geiger, G. and Fine, H.A. (2011). *Handbook on Material and Energy Balance Calculations in Materials Processing*. 3rd edn. Hoboken, NJ: John Wiley & Sons/The Minerals, Metals & Materials Society.',
  'Spirax Sarco (n.d.). Steam and the organisation. Available at: https://www.spiraxsarco.com/learn-about-steam/introduction/steam-and-the-organisation (Accessed: 5 October 2026).',
  'Swedish Government (2022). *National Electrification Strategy: a summary*. Ministry of Rural Affairs and Infrastructure. Available at: https://www.regeringen.se/informationsmaterial/2022/09/national-electrification-strategy---a-summary/ (Accessed: 4 October 2026).',
  'Talebjedi, B., Laukkanen, T., Holmberg, H., Vakkilainen, E. and Syri, S. (2021). Energy efficiency analysis of the refining unit in thermo-mechanical pulp mill. *Energies*, 14(6), 1664. https://doi.org/10.3390/en14061664',
  'U.S. Department of Energy (2012). *Eliminate Excessive In-Plant Distribution System Voltage Drops*. Motor Systems Tip Sheet #8. Washington, DC: U.S. Department of Energy, Advanced Manufacturing Office.',
];
refs.forEach(r => children.push(new Paragraph({ children: runs(r), indent: { left: 360, hanging: 360 }, spacing: { after: 120, line: 280 } })));

// ---------------------------------------------------------------- appendices
brk();
H1('Appendix A: Data sources and input values');
TABLE('Model inputs, values and sources.', ['Input', 'Value', 'Source'], [
  ['Total electricity', '1,450 GWh', 'Miljörapport 2023, Table 13'], ['Diesel', '2.82 GWh', 'Miljörapport 2023, Table 13'],
  ['Paper production', '444,494 t', 'Miljörapport 2023, Table 3'], ['TMP pulp production', '421,883 t (air-dry)', 'Miljörapport 2023, Table 3'],
  ['District heat exported', '11.9 GWh', 'Miljörapport 2023, 8.3.3'], ['Effluent volume', '6.68 Mm³ (WWTP) + 0.61 Mm³ (second outlet)', 'Miljörapport 2023, 5.2'],
  ['Cooling and unaffected water', 'about 4 Mm³/y', 'Holmen Q&A 2025 (water balance 2024)'],
  ['TMP share of electricity', '70 %', 'Holmen Q&A 2025 (2019: 72 %)'], ['Paper machines incl. bleaching', '15 %', 'Holmen Q&A 2025 (2019: 22 %)'],
  ['Electric boilers', '10 %', 'Holmen Q&A 2025 (2019: 6 %)'], ['Other users', '5 %', 'Remainder of the 2025 split'],
  ['WWTP, wood handling, bleaching', '2.5 / 2.5 / 3 MW', 'Holmen Q&A 2025'], ['TMP auxiliary drives', '150 kWh/t', 'Holmen Q&A 2025'],
  ['TMP refining, normal span', '1,500-2,000 kWh/t', 'Holmen Q&A 2025 (see Section 5.2)'],
  ['Recovered TMP steam', '100 t/h', 'Holmen Q&A 2025'], ['Steam recovery rate', '70-90 % of steam need', 'Holmen Q&A 2025'],
  ['Electric-boiler steam yield', '1.5 t/MWh', 'Holmen Q&A 2025'], ['Paper-machine drying steam', '95 t/h (80-110 t/h)', 'Holmen Q&A 2025'],
  ['Wood-handling steam', '1.5 t/h', 'Holmen Q&A 2025'], ['Steam state', '2.4 bar(g), 138 °C', 'Holmen Q&A 2019'],
  ['Condensate return', '90 °C', 'Holmen Q&A 2019'], ['PM11 share of PM electricity', '64 %', 'Holmen Q&A 2019 (August 2019)'],
  ['Production hours', '7,200 h', 'Derived: PM11 285.3 d, PM12 314 d (7,174 h)'],
  ['Internal grid losses', '1 % of input', 'Assumption; DOE reports below 1 % to above 4 % (U.S. Department of Energy, 2012)'],
  ['Steam network losses', '4 % of supply', 'Assumption; distribution losses should generally stay below about 5 % (Spirax Sarco, n.d.)'],
  ['Effluent temperature', '32 °C (about 20 °C in long shutdowns)', 'Holmen Q&A 2019; treatment plant rebuilt 2020'],
  ['Waste-heat temperatures', 'TMP 80 °C, PM 55 °C, hot water 60 °C', 'Holmen Q&A 2019 and 2025 (pulp 80 °C, PM wastewater about 50 °C)'],
  ['Heat pump COP', '2.5-3.5', 'Arpagaus et al. (2018)'],
], [2900, 2600, 3526]);
P(`Where sources disagree, the model uses the value above for these reasons. The 2025 electricity split is closest in time to 2023 and is the only one given with the current total. Steam figures quoted in GJ without a period (2019: 145,000 GJ for TMP and 155,000 GJ for the paper machines; undated: about 10,000 GJ per month) are used only as cross-checks; read as monthly values, the TMP figure is within 12 % of the model. The 2023 production from Table 3 is used rather than the value implied by the rounded specific consumption in Table 13 (3.3 MWh/t).`);
H1('Appendix B: Electricity use by process');
TABLE('Electricity use by process, 2023.', ['Process', 'GWh/y', 'Share', 'How it is calculated'], [
  ['TMP refiners', '952', '65.6 %', 'TMP 70 % minus auxiliary drives'], ['TMP auxiliary drives', '63', '4.4 %', '150 kWh/t × 421,883 t'],
  ['Paper machines', '196', '13.5 %', '15 % minus bleaching'], ['Electric boilers', '145', '10.0 %', '10 %'],
  ['WWTP', '22', '1.5 %', '2.5 MW × 8,760 h'], ['Bleaching', '22', '1.5 %', '3 MW × 7,200 h'],
  ['Utilities and other', '18', '1.2 %', 'Rest of the 5 %'], ['Wood handling', '18', '1.2 %', '2.5 MW × 7,200 h'],
  ['Internal grid losses', '15', '1.0 %', '1 % assumption'], ['Total', '1,450', '100 %', 'Miljörapport 2023'],
], [2600, 1200, 1200, 4026], { numCols: [1, 2] });

// ---------------------------------------------------------------- document
const doc = new Document({
  creator: 'AL2144 Group 2', title: 'Industrial Energy Flow Analysis: Holmen Hallsta Paper Mill',
  styles: {
    default: { document: { run: { font: 'Arial', size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 30, bold: true, font: 'Arial', color: '1F3A31' }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 25, bold: true, font: 'Arial', color: '1F3A31' }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 22, bold: true, italics: true, font: 'Arial' }, paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: '7C8782' })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log(`wrote ${OUT}: ${figN} figures, ${tabN} tables`); });
