# data/sources.csv

Single data register of literal values from the Hallsta paper mill source documents (MFA, reference year 2023). One row per value, no interpretation or computation (only unit labelling). 298 rows.

## Columns
- `id`: unique snake_case key. Suffixes: `_YYYY` data year; `_t6`/`_t9`/`_t13` = Miljörapport table; `_aq` = "Answers to questions-1".
- `quantity`: what the value is.
- `value`: number as in the source (dot decimal). Blank when the source gives a range (then `value_low`/`value_high` are filled) or when the row is a note/label.
- `value_low`, `value_high`: range ends.
- `unit`: unit as written in the source.
- `source_file`, `location`: file under `resources/`, and table/section/question/image.
- `source_year`: year of the document. `data_year`: year the value refers to, as stated ("n/a", "not stated" when unknown).
- `quote`: verbatim snippet (<=200 chars). For multi-year tables (Tabell 6, 8, 13) the quote is a row/column label plus value, not a literal line.
- `notes`: ambiguities and cross-references to conflicting rows.

## Source files and assigned years
| File | source_year |
|---|---|
| Miljörapport 2023 Hallsta-1.pdf | 2023 |
| Compiled questions to Holmen 2019.docx | 2019 (some answers refer to 2018 or Aug 2019) |
| Questions for the study visit (Answers Hallsta).docx | 2019/2020 (2019 data; mentions June 2020 WWTP) |
| Student questions to Holmen 2025 (ANRA 251021).docx | 2025 (water balance image is "for 2024") |
| Answers to questions-1.docx | unknown (~2025); some data stated as 2023 |
| Viktiga Energiflöden-1 (1)-1.pptx | unknown |

Notes on coverage: Tabell 7 (monthly) pollutant columns were skipped; Tabell 7 has no flow column, only EDTA per month (not entered). Images in "Answers to questions-1.docx": image1/image2 are water-consumption charts (L11, L12) with no numeric labels (not transcribed, noted as rows); image3/image4 are Holmen logos. WWTP process diagrams in the study-visit file contain no numbers.

## Known conflicts and ambiguities
1. Electricity split: 2019 doc (avg last 3 years) boiler 6 %, TMP 72 %, PM 22 % (`el_split_*_2019`) vs 2025 doc boiler ~10 %, TMP ~70 %, PM ~15 % (`el_split_*_2025`). 2025 shares sum to 95 %. pptx implies EP 0.12/3.02 MWh/F-ton (~4 %) and TMP 2.20/3.02 (~73 %).
2. TMP steam: `tmp_steam_recycled_2025` ~100 t/h recycled; `steam_tmp_net_2019` 145 000 GJ (period not stated; maybe per month); `steam_tmp_10000GJ_month_unknown` ~10 000 GJ/month "steam production"; `tmp3_steam_use_aq` 500-5000 GJ/month; `pptx_steam_recovered` 1.2 MWh/F-ton (~1.8 t steam/F-ton). Scales disagree and periods are not always stated.
3. PM steam: `steam_pm_2019` 155 000 GJ (period not stated) vs `pm_steam_2025` 80-110 t/h.
4. Effluent "32 degrees" (`effluent_dT_sea_2019`, 20 under long shutdowns): asked as a temperature difference to the sea but could be an absolute temperature.
5. Paper production: Tabell 3 444 494 t (2023); Tabell 13 implied (1453 GWh / 3.3 MWh/t = ~440 kt; 1450/3.3 = 439 kt); pptx 565 kF-ton/yr; 2018 547 585 t; image `img_2019_1_paper_adt` 900 ADT/d (~328 kt/yr). Tabell 13 specific energy values imply other years' production: 2019 1454/3.18 = 457 kt, 2020 1343/3.10 = 433 kt, 2021 1610/3.21 = 502 kt, 2022 1656/3.19 = 519 kt (derived, not stated in source).
6. Electricity total: Tabell 13 2019 1451, 2020 1340, 2021 1607, 2022 1653, 2023 1450 GWh; 2025 doc ~1.5 TWh/yr; Aug 2019 monthly values (TMP3 46 000 + TMP12 38 000 + PM11 14 000 + PM12 8 000 MWh/month) sum to 106 000 MWh vs ~121 GWh/month implied by 2019 annual.
7. Specific energy: Tabell 13 3.3 MWh/F-ton (2023) vs pptx 3.02 MWh/F-ton vs energy-cost target 3.0 MWh/F-ton (Dec 2023, different metric).
8. District heat: 11 877 MWh (2023, `dh_export_2023`) vs approx 16 000 GJ (= 4.4 GWh, 2019, `dh_2019`).
9. Effluent flow: Tabell 6 2023 20 000 m3/d; WWTP outlet only 18 300 m3/d; total 7 288 861 m3/yr (~19 970 m3/d); 2019 doc 11.5-12.0 m3/min (~17 000 m3/d); 2025 doc 13.5 m3/min (~19 400 m3/d) and water-balance image 7 Mm3/yr.
10. Water balance (2025 doc image) inflow 11.8 Mm3/yr vs Tabell 12 raw water 11.047 Mm3 (2023); year differs. Fresh water: 6.3 m3/min (2019 doc, production incl. sealing water) vs 12.8 m3/min (2023 "renvatten") vs 30 266 m3/d raw water (~21 m3/min). Specific: 15.2 m3/t (target-comparison metric) vs 24.8 m3/t raw water.
11. Bark: 135 500 t (2018 bark from debarking) vs 109 061 t sold (2023) vs 12 % of log removed as bark; dry/wet basis not stated.
12. Nutrients added at WWTP: 300 t N and 30 t P per year (2019/2020 doc) vs 700 kg N/d and 70 kg P/d (2023). Urea 690 000 t (2019 doc, 2018) is of implausible magnitude as written.
13. Sludge: ~60 000 t wet/yr at 27 % dryness (2019/2020) vs ~33 t TS/d at 28 % (answers-1) vs 45 456 t to Norra plan (2023).
14. Loads quoted as energies: 2025 doc answers kWh questions with MW (wood handling 2.5 MW, bleaching 3 MW, WWTP 2.5 MW).
15. TMP capacity: TMP3 50 ADT/h, TMP12 35 ADT/h consistent across 2025 doc and answers-1.
16. Tabell 4 operating time PM11 285.3 d, PM12 314 d; WWTP 365 d ("motsvarar pappersbrukets drifttid") while PM days are fewer.
17. Boiler shutdown year: Tabell 5 gives oil boilers off since 2015, HP3 off May 2014; intro says no solid-fuel boiler since 2014.
18. Temperature ranges: incoming water 2-25 degC; pulp after refiners 170-200 degC; refiner inlet ~85 degC; PM wastewater ~50 degC; warm water to process ~56 degC; PM condensate ~90 degC; steam 138 degC at 2.4 bar (2.5 bar elsewhere, gauge/absolute not stated).
