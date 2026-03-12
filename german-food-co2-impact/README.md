# CO2 Impact of Food in Germany

<!-- AI-GENERATED-NOTE -->
> [!NOTE]
> This is an AI-generated research report. All text and code in this report was created by an LLM (Large Language Model). For more information on how these reports are created, see the [main research repository](https://github.com/simonw/research).
<!-- /AI-GENERATED-NOTE -->

## Overview

This investigation examines the greenhouse gas emissions (measured in kg CO2-equivalents) associated with food production and consumption in Germany. It covers individual food products, typical German dishes, the annual dietary footprint, and reduction strategies.

Germany's food system is responsible for approximately **25% of the country's total greenhouse gas emissions** when the full supply chain is considered. The average German diet produces roughly **2,000 kg CO2eq per person per year** — equivalent to driving a petrol car for about 6,500 km.

## Key Findings

### 1. CO2 Emissions Per Kilogram of Food

Based primarily on the IFEU (2020) study commissioned by the German Federal Environment Agency, emissions per kilogram vary by more than **two orders of magnitude**:

| Category | Examples | Range (kg CO2eq/kg) |
|---|---|---|
| Root vegetables | Carrots, potatoes, cabbage | 0.1 – 0.3 |
| Other vegetables | Broccoli, peppers, lettuce | 0.3 – 0.5 |
| Fruits (regional, seasonal) | Apples, pears, strawberries | 0.2 – 0.8 |
| Grains & bread | Wheat bread, oats, pasta | 0.5 – 0.8 |
| Legumes | Peas, lentils | 0.4 – 0.7 |
| Rice | Paddy rice (methane!) | 3.6 |
| Milk | Cow's milk | 1.4 |
| Cheese | Hard cheese, Quark | 5.0 – 8.5 |
| Butter | | 9.0 |
| Eggs | | 3.0 |
| Poultry | Chicken, turkey | 5.0 – 5.5 |
| Pork | Including sausage/Wurst | 4.6 – 4.8 |
| Beef | German average | 13.6 |
| Lamb | | 25.0 |
| Air-freighted produce | Berries, pineapple, asparagus | 5.0 – 15.1 |

### 2. Typical German Dishes

CO2 footprint per serving of popular German meals:

| Dish | CO2eq per Serving | Key Driver |
|---|---|---|
| Kartoffelsuppe (potato soup) | ~320 g | Cream |
| Gemüsepfanne vegan (veggie stir-fry) | ~520 g | Rice |
| Butterbrot mit Käse (bread & cheese) | ~540 g | Cheese, butter |
| Frühstück typisch (typical breakfast) | ~740 g | Cheese, butter, egg |
| Bratwurst mit Brötchen | ~760 g | Sausage |
| Currywurst mit Pommes | ~910 g | Sausage |
| Schweineschnitzel mit Kartoffelsalat | ~1,160 g | Pork |
| Käsespätzle | ~1,350 g | Cheese, butter |
| Spaghetti Bolognese | ~1,810 g | Beef |
| Sauerbraten mit Rotkohl und Klößen | ~3,520 g | Beef (250g) |

A sustainable meal target is **< 800 g CO2eq per serving**. Beef-based dishes consistently exceed this, while plant-based and pork-based dishes can stay within range.

### 3. Annual Diet Breakdown

The top contributors to the average German diet's annual CO2 footprint:

| Category | Annual CO2 (kg) | Share |
|---|---|---|
| **Meat** | ~371 | ~37% |
| **Dairy** | ~338 | ~33% |
| Beverages | ~88 | ~9% |
| Grains & legumes | ~64 | ~6% |
| Other (sugar, oils, chocolate) | ~47 | ~5% |
| Eggs | ~41 | ~4% |
| Vegetables | ~34 | ~3% |
| Fruits | ~23 | ~2% |

**Meat and dairy together account for ~70% of food-related emissions** — consistent with findings from the Umweltbundesamt. The top 3 individual items by annual contribution are pork (127 kg CO2eq), beef (121 kg), and hard cheese (119 kg).

### 4. Diet Scenarios

| Diet Pattern | Annual CO2eq | vs. Current |
|---|---|---|
| Average German diet (current) | ~2,000 kg | baseline |
| DGE recommended diet | ~1,400 kg | -30% |
| Flexitarian (Planetary Health Diet) | ~1,100 kg | -45% |
| Vegetarian | ~1,160 kg | -42% |
| Vegan | ~940 kg | -53% |
| **1.5°C compatible target** | **590 kg** | **-70%** |

Even the vegan diet exceeds the 1.5°C-compatible target of 590 kg CO2eq/year. Achieving climate targets requires systemic changes beyond individual diet choices — including agricultural reform, renewable energy in food processing, and reduced food waste.

### 5. Seasonality and Processing Matter

| Better Choice | CO2/kg | Worse Choice | CO2/kg | Savings |
|---|---|---|---|---|
| Seasonal tomatoes | 0.4 | Heated greenhouse tomatoes | 2.9 | 86% |
| Regional asparagus | 0.5 | Air-freighted asparagus | 5.0 | 90% |
| Pineapple by ship | 0.6 | Pineapple by air | 15.1 | 96% |
| Fresh peaches | 0.2 | Canned peaches | 1.6 | 88% |
| Oat milk | 0.3 | Cow's milk | 1.4 | 79% |
| Tofu | 2.0 | Beef | 13.6 | 85% |

**What you eat matters far more than where it comes from.** Transport accounts for less than 10% of most foods' emissions. The major exception is air freight, which increases emissions ~50x compared to sea transport. However, only ~0.16% of food miles globally involve air freight.

Counterintuitively, **locally grown greenhouse vegetables in winter can have a higher footprint than imports** from Southern Europe where the same crops grow outdoors in season.

## Methodology

- CO2 emission factors primarily from the **IFEU 2020** study (Germany-specific), supplemented with **Poore & Nemecek 2018** global averages
- German per capita consumption data from **BMEL/BLE** supply balance sheets (2023/2024)
- Diet scenario data from **Umweltbundesamt** and peer-reviewed literature
- All values in **kg CO2-equivalents** (includes CO2, CH4, N2O weighted by 100-year global warming potential per ISO 14067)
- Bottom-up calculations cover farm-to-retail emissions; the gap vs. literature values (~1,000 vs. ~2,000 kg) is explained by food waste (~30% of food purchased is wasted), cooking energy, retail refrigeration, and other downstream factors not captured in per-kg factors

## Files

| File | Description |
|---|---|
| `README.md` | This report |
| `notes.md` | Research notes and process documentation |
| `food_co2_analysis.py` | Python analysis script with all data and calculations |
| `food_co2_data.csv` | CO2 emission factors for 65+ food products |
| `dish_co2_data.csv` | CO2 footprint of 10 typical German dishes |

## Sources

- IFEU (2020): [Ökologische Fußabdrücke von Lebensmitteln und Gerichten in Deutschland](https://www.ifeu.de/fileadmin/uploads/Reinhardt-Gaertner-Wagner-2020-Environmental-footprints-of-food-products-and-dishes-in-Germany-ifeu-2020.pdf)
- Poore & Nemecek (2018): [Reducing food's environmental impacts through producers and consumers](https://ourworldindata.org/environmental-impacts-of-food), Science
- Our World in Data: [GHG emissions per kg of food product](https://ourworldindata.org/grapher/ghg-per-kg-poore)
- Our World in Data: [Food emissions across the supply chain](https://ourworldindata.org/grapher/food-emissions-supply-chain)
- Umweltbundesamt: [German diet is a strain on the climate](https://www.umweltbundesamt.de/en/press/pressinformation/german-diet-is-a-strain-on-the-climate)
- Umweltbundesamt: [Towards healthy and sustainable diets in Germany](https://www.umweltbundesamt.de/sites/default/files/medien/11740/publikationen/2023-05-10_texte_67-2023_towards_healthy_1.pdf)
- BMEL-Statistik: [Versorgungsbilanzen](https://www.bmel-statistik.de/ernaehrung/versorgungsbilanzen)
- BLE (2024): [Consumption of meat per capita falls below 52 kilograms](https://www.ble.de/SharedDocs/Meldungen/EN/2024/240510_Meat-Consumption.html)
- BZL: [Pro-Kopf-Verbrauch ausgewählter Lebensmittel](https://www.landwirtschaft.de/infothek/infografiken/uebersicht-aller-infografiken/pro-kopf-verbrauch-ausgewaehlter-lebensmittel-in-deutschland-2022)
- Springer (2024): [Reduction potential of German environmental food impacts due to a planetary health diet](https://link.springer.com/article/10.1007/s11367-024-02352-4)
- PMC: [Dietary GHG emissions among Bavarian adults](https://pmc.ncbi.nlm.nih.gov/articles/PMC12014458/)
- nachhaltigkeit-mit-kopf.de: [CO2-Fußabdruck Lebensmittel Tabelle](https://nachhaltigkeit-mit-kopf.de/ernaehrung/co2-fussabdruck-lebensmittel/)
- Our World in Data: [Food choice vs. eating local](https://ourworldindata.org/food-choice-vs-eating-local)
- Our World in Data: [Very little of global food is transported by air](https://ourworldindata.org/food-transport-by-mode)
