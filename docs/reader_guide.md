# A beginner’s guide to the Hallsta analysis

This guide assumes no previous experience with data analysis or statistics. You can understand the study without reading Python. The notebooks put calculations beside explanations so that someone who wants to check the work can follow it. Knowing what a method can establish is as important as knowing how to calculate its answer.

## 1. The question and the reading order

The mill buys electricity, uses it to make pulp and paper, and recovers some of the resulting heat as steam. We ask where that energy goes, where its ability to do useful work is lost, and which changes could reduce purchased electricity. We also ask how much those answers depend on uncertain inputs.

Read the EDA notebook first: it checks the source information before choosing model inputs. Read the model notebook second: it calculates the flows, tests uncertainty, and compares measures. In Word, start with Sections 3–5 to understand the mill and the baseline, then Section 6 for uncertainty and Section 7 for measures. Appendix E explains the methods in more detail. The data appendix is a reference for checking individual numbers; it is not intended as a first reading.

In a notebook, a text cell explains an idea; a code cell carries out a calculation; its output appears underneath. Saved outputs can be read without running anything. If you run the notebook, use the project Python environment and run cells from top to bottom: later cells use values created earlier. Running cells out of order can mix old and new results. The final model cell and several EDA cells write report tables and figures, so running them refreshes files rather than merely displaying them.

## 2. Units, inputs and outputs

Power describes how quickly energy is used. Energy describes how much is used over a period. A 2.5 MW process operating for 7,200 hours uses 18,000 MWh, or 18 GWh. One GWh equals 1,000 MWh or one million kWh. The suffix /y means per year. A tonne is written t; kt means one thousand tonnes. Mm³ means one million cubic metres of water. A temperature difference of 10 K has the same numerical size as a difference of 10 °C.

Specific electricity consumption, or SEC, means electricity per tonne of product. Dividing 1,450,000 MWh by 444,494 tonnes of paper gives 3.262 MWh/t. This allows comparison across production volumes. A smaller annual electricity bill does not necessarily mean better efficiency: if production falls even more, electricity per tonne can rise. Always check whether a per-tonne figure refers to finished paper or pulp; the denominators differ.

An input is a number supplied to the model, such as electricity consumption, steam flow or temperature. An output is calculated from those inputs, such as recovered heat or electricity saved. The baseline is one chosen set of input values. A scenario changes specified baseline assumptions to answer a particular “what if?” question. Neither a baseline calculation nor a scenario is a new measurement of the mill.

## 3. EDA: checking the information before calculating

EDA stands for exploratory data analysis. Here it means organising the source numbers, drawing simple comparisons, and checking whether the values can reasonably be used together. It is not machine learning, and it does not automatically choose the correct answer.

The source register is a list of numbers with their documents, years, units and source IDs. A source ID is an address for finding the evidence again. “Reported” means supplied by the source. “Derived” means calculated from other numbers. “Assumed” means chosen by the analysts where a suitable measurement is unavailable. Source-quality classes A–D describe provenance; they are not statistical grades or guarantees that an input is correct.

The five-year context chart places year on the horizontal axis. Its panels show production, total electricity and electricity per tonne. Compare the same quantity across years within a panel; do not compare the heights of different panels because their units differ. The shaded year is 2023. The chart uses a rounded reported SEC of 3.3 MWh/t for 2023, while the model calculates 3.262 from reported production. Dividing electricity by rounded SEC implies about 439 kt; the directly reported output is 444.494 kt. This rounding difference is explained rather than treated as a second measurement.

The electricity-split chart uses stacked horizontal bars. Each coloured segment represents a process category. The intensity panel gives MWh per tonne; the share panel gives percentages. A zero or absent segment in the August 2019 comparison does not establish zero boiler demand: that source does not cover boilers. Its shares describe only the covered lines. The sources also describe different years and operating conditions, so their differences do not prove a measured time trend.

The steam chart compares sources with different units and sometimes missing periods. Hatched bars mark assumed periods. Reading a quantity as monthly rather than annual can change its annual equivalent by a factor of twelve. The EDA comparison counts about 2.35 GJ per tonne of steam, whereas the main model counts 2.15 GJ/t of latent heat. Consequently, the chart’s recovered heat divided by TMP electricity is about 46%, while the main model’s ratio is about 42%. These ratios also differ from the 77% share of total steam supplied by TMP: each divides by a different total.

The water chart compares flows from 2023 and a rough 2024 balance. A water volume does not itself tell us heat loss: the temperature difference is needed too. Inputs, internal uses and outputs cannot all be added as if they were separate exits. Mixing years and potentially overlapping outlet categories can prevent an exact balance.

The reconciliation table puts competing source values beside the chosen input. Read the source, period, unit, conversion and warning together. A blank common value means a conversion was not justified; it is not zero. A conflict flag means the values need interpretation; it does not prove that the source is wrong.

## 4. Energy, exergy and residuals

Energy is conserved: at steady state, operational energy entering the mill leaves through the counted outputs. Steam recovered inside the mill is reused energy, not another purchase. Adding 430 GWh of recovered steam to purchased electricity would count part of the same energy twice.

Exergy is the maximum useful work an energy flow could provide relative to the surroundings. Electricity can run a motor directly. Warm water at a temperature close to the surroundings has much less ability to do work, even when it contains the same amount of energy. Exergy can be destroyed by irreversible conversion; energy cannot. Thus 1,328 GWh/y of exergy destruction does not mean 1,328 GWh/y of energy disappeared or could all be saved.

At baseline, boiler electricity is 145 GWh/y. On the model’s latent-heat basis, boiler steam is 129.9 GWh/y. The 15.1 GWh difference mainly reflects feedwater heating outside that accounting convention, plus a small conversion loss; it is not a measured 10% boiler loss. A boiler can be close to 98% energy efficient on the full-heat basis and only 31% exergy efficient because electricity is converted into lower-quality heat.

Latent heat is heat released when steam changes into liquid water without changing its temperature. Sensible heat changes the temperature of the water. Condensate is water formed when steam condenses. Enthalpy is the thermodynamic quantity used to account for heat carried by flowing steam or water. The full enthalpy drop includes condensation and cooling; the latent-only account includes condensation heat. This choice changes the number called steam energy, rather than describing a different physical steam flow.

In the equations, m is mass, Q is heat, E is energy, Ex is exergy, T is temperature and T₀ is the surroundings reference temperature. The symbol Δ means a difference; cₚ is heat capacity; s is entropy, a thermodynamic property used with temperature to determine work potential; ln is the natural logarithm. Temperature ratios and thermodynamic exergy equations use kelvin: add 273.15 to °C. ψ or ηex is defined useful exergy divided by incoming exergy. IP means improvement potential, the ranking indicator described in the report. LCA means life-cycle assessment; this study’s screening LCA is a qualitative discussion of environmental trade-offs, not a calculation of emissions.

A residual is calculated as the total minus the categories already assigned. If a budget is 100 and named expenses total 70, the remaining 30 is a residual; the subtraction does not identify what was bought. Likewise, the report’s 769 GWh/y unassigned output does not identify a measured recoverable heat source. A balance can close perfectly because a residual was defined to make it close, even when some inputs are wrong. Comparison with separate evidence is therefore needed as well as checking arithmetic.

## 5. Why use Monte Carlo?

Suppose drying steam is estimated at 95 t/h, but the source gives a range of 80–110 t/h. Calculating only at 95 hides how much the result might change. Monte Carlo repeats the same calculation with many plausible combinations of inputs. It propagates the uncertainty we specify; it does not discover the true values or generate new observations.

A distribution describes which input values the model samples more often. A normal distribution is a bell shape around a mean. Its standard deviation describes the spread. A coefficient of variation, or CV, is standard deviation divided by the mean: 2% of 1,450 GWh is 29 GWh. That 29 GWh is one standard deviation, not a hard maximum error or a statement that all draws lie within ±2%.

A triangular distribution has a minimum, a most-favoured value called the mode, and a maximum. Triangular (80, 95, 110) favours values near 95 over values near the limits. A uniform distribution gives equal probability to equal-width intervals across its range, as used for COP between 2.5 and 3.5. With continuous distributions, no individual exact decimal value has a positive probability. These distribution choices express modelling judgements, not measured frequency curves for Hallsta.

## 6. One trial, repeated 10,000 times

In one trial, the computer draws input values from their distributions, normalises the electricity shares, calculates all flows and measures, then checks consistency. Consider a teaching example: 100 t/h of recovered steam and 95 t/h of drying steam over 7,200 hours give 430 and 408.5 GWh/y on the latent basis. Holding everything else fixed, choosing 110 t/h for drying raises demand to 473 GWh/y and reduces the unallocated steam from 122.55 to 58.05 GWh/y. A full Monte Carlo trial samples the other uncertain inputs too; this teaching example isolates just one effect.

The sampled electricity shares are divided by their sum so that they add to 100%. For example, proposed shares of 72, 15, 10 and 5 sum to 102, so the TMP share becomes 72/102 = 70.59%. The shares are then multiplied by the total electricity sampled in that trial. The total is also uncertain; it is not held at 1,450 in every trial.

Some inputs must move together. One sampled production-hours value is used for both recovered TMP steam and drying steam. Both effluent outlets use the same sampled temperature. Sampling a shared physical quantity independently for each use would describe inconsistent versions of the same mill. Boiler steam follows annual boiler electricity and yield, rather than receiving another production-hours multiplier.

A trial is accepted only if TMP supplies 70–90% of steam, the unallocated steam is non-negative, process exergy destruction is non-negative within numerical tolerance, and counted boiler-steam heat does not exceed boiler electricity. A negative steam residual would mean the chosen uses exceed the chosen supply. These checks remove internally inconsistent combinations; they do not prove that every remaining combination occurred at the mill.

Of 10,000 trials, 9,698 pass: 96.98%. This percentage is not the probability that the model is correct or a plant reliability figure. The seed, 2023, starts the random-number generator reproducibly; it is not another source-year assumption. Repeating with the same code, seed and sampling order reproduces the draws. More trials generally reduce numerical sampling noise, but cannot repair poor source data or missing assumptions.

## 7. Percentiles and uncertainty ranges

Imagine sorting the accepted results from smallest to largest. P5 is the value below which approximately 5% lie; P50 is the middle value, called the median; P95 is the value below which approximately 95% lie. Therefore approximately 90% of accepted simulated results lie between P5 and P95. Percentiles are calculated by interpolation, so a percentile can lie between two simulated values.

For combined saving M4, the baseline is 125.6 GWh/y, while accepted P5 and P95 are approximately 107.2 and 146.1 GWh/y. A suitable interpretation is: “Under the chosen input distributions and acceptance rules, the middle 90% of simulated full-year savings lies between about 107 and 146 GWh/y.” It is not a guaranteed operating range, an interval containing every possible real outcome, or proof of a 90% chance that the actual saving will lie there. Unsampled structural assumptions and seasonal mismatch can move the real result outside it.

The baseline is a calculation at chosen central inputs. The median is the middle simulated output after varying inputs and rejecting inconsistent combinations. They need not match, especially with asymmetric distributions, nonlinear calculations and constraints. Do not add percentile endpoints across rows: each row’s endpoint may come from a different trial. Sum flows within each trial before calculating a percentile for their total.

A histogram groups outputs into intervals called bins. The horizontal axis gives an output value; taller bars contain more accepted trials. The current plots omit numerical vertical-axis ticks, so use the bars to compare relative concentration, not to read exact probabilities. The solid reference line is the baseline; dashed lines mark P5 and P95. A histogram shows the assumed uncertainty propagated through the model, not measured year-to-year variation.

## 8. Sensitivity, scenarios and ranking

Sensitivity asks which uncertain inputs most affect an output. In a tornado chart, one input is moved from its P5 to P95 while the others stay at baseline. A longer span means a larger change in that output over the chosen input range. The two plotted panels concern recovery to 90% of supply (M1b) and combined saving (M4); other sensitivity calculations are in the CSV table. The output at input P5 can be larger than the output at input P95 if the relationship is negative. These two outputs are not the output’s Monte Carlo P5 and P95.

Spearman correlation compares the order, or rank, of input and output values across accepted trials. A coefficient near +1 means larger inputs tend to accompany larger outputs; near −1 means larger inputs tend to accompany smaller outputs. Near zero means little monotonic association in these samples, not necessarily no relationship. A value of 0.8 does not mean an input explains 80% of uncertainty or causes 80% of the output. Normalised shares, tied inputs and acceptance conditions affect these associations.

The rank-stability chart asks how often a process occupies each hotspot rank. TMP is first, paper machines second, and boilers third in every accepted baseline trial. This means the ordering is stable under the specified model and distributions. It does not mean those quantities are known exactly or that the ordering must hold under every different system definition. S6, a separate source-interpretation scenario, moves the unexplained category into third place.

A scenario changes an explicit assumption rather than repeatedly sampling the same uncertainty model. S3 uses 110 t/h drying steam; S5 changes the steam heat basis and boiler formulation; S6 reallocates TMP electricity without reducing the total; S4 is an infeasible stress case. A scenario is not a percentile, and its output is not assigned a probability unless a probability model is explicitly supplied.

## 9. Three different ranges for savings

For M2, the fixed-input COP range of 2.5–3.5 gives about 88–104 GWh/y of electricity saving. Only COP changes in that comparison. The Monte Carlo P5–P95 is wider, about 78–119 GWh/y, because boiler demand and other uncertain inputs also change. The seasonal case is a third question: what if there is no saving in June–August? Applying 75% to the baseline saving of 97.6 gives 73.2 GWh/y. These ranges should be named separately rather than combined into one supposedly equivalent range.

For M4, the baseline full-year saving is 125.616 GWh/y. The seasonal calculation is 125.616 × 0.75 = 94.212 GWh/y. Subtract these savings from 1,450 GWh and divide by the same paper output: (1,450 − 125.616) × 1,000 / 444,494 = 2.980 MWh/t, and (1,450 − 94.212) × 1,000 / 444,494 = 3.050 MWh/t. Thus 2.98–3.05 describes two availability assumptions at baseline, not the Monte Carlo interval. The 75% case is illustrative and is not a guaranteed lower bound.

COP is heat delivered divided by electricity consumed. COP 3 means that 1 unit of electricity supports delivery of 3 units of heat, including heat taken from the source; the heat pump does not create energy. M2 must deliver full steam heat, including heating condensate, which is why its heat duty is about 142 GWh rather than the latent-only 130 GWh.

Measures share the same boiler demand. M4 first reduces drying demand with M3, then adds recovery with M1, then uses a heat pump for the remainder. Adding the separate M1, M2 and M3 savings would count some displaced boiler electricity more than once. In the sampled M3 case the improvement is always two percentage points above the sampled starting dryness: 50% becomes 52%, rather than giving zero saving at a fixed 50% target.

## 10. What conclusions can we defend?

The strongest model-supported conclusion is the priority of the electricity–steam system: TMP is the largest electricity user and exergy-destruction hotspot, while displacing marginal boiler electricity offers substantial potential. The exact annual saving, equipment size, heat-source availability, paper-quality effect and investment return need additional evidence. Exergy improvement potential is a ranking indicator, not an achievable saving, and the qualitative LCA does not calculate tonnes of avoided greenhouse-gas emissions.

When reading a result, ask: what is the quantity and unit; what evidence or assumption supplies the inputs; what is held fixed; what varies; is the number measured, calculated or found by difference; and what limitation would change its interpretation? A clear presentation should make each answer findable without requiring Python knowledge.
