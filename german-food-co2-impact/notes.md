# Research Notes: CO2 Impact of Food in Germany

## Research Process

### Starting Point
Investigated the CO2 impact of typical food consumed in Germany using publicly available data from German government agencies, research institutes, and peer-reviewed studies.

### Key Sources Identified

1. **IFEU (2020)** - "Ökologische Fußabdrücke von Lebensmitteln und Gerichten in Deutschland"
   - Commissioned by the Umweltbundesamt (German Federal Environment Agency)
   - Most authoritative Germany-specific dataset
   - Covers 188 food products and 8 dishes
   - Available at: https://www.ifeu.de/fileadmin/uploads/Reinhardt-Gaertner-Wagner-2020-Environmental-footprints-of-food-products-and-dishes-in-Germany-ifeu-2020.pdf

2. **Poore & Nemecek (2018)** - "Reducing food's environmental impacts through producers and consumers", Science
   - Global meta-analysis covering 38,700 farms in 119 countries
   - Used for foods where Germany-specific data was unavailable
   - Data accessible via Our World in Data: https://ourworldindata.org/environmental-impacts-of-food

3. **BMEL / BLE** - German Federal Ministry of Food and Agriculture
   - Per capita food consumption statistics (supply balance sheets)
   - 2023/2024 data on meat, dairy, vegetables, fruits
   - https://www.bmel-statistik.de/ernaehrung/versorgungsbilanzen

4. **Umweltbundesamt (UBA)** - German Environment Agency
   - "German diet is a strain on the climate" (press release)
   - "Towards healthy and sustainable diets in Germany" (2023 report)
   - https://www.umweltbundesamt.de/en/press/pressinformation/german-diet-is-a-strain-on-the-climate

5. **Bavarian Diet Study (2024)** - Published in PMC
   - Real dietary data from Bavaria showing 6.14 kg CO2eq per 2,500 kcal average
   - https://pmc.ncbi.nlm.nih.gov/articles/PMC12014458/

### Key Findings

#### Per-kg emission factors
- Enormous range: from 0.1 kg CO2eq/kg (carrots, cabbage) to 25+ kg CO2eq/kg (lamb)
- German beef averages ~13.6 kg CO2eq/kg (lower than global average of ~60 due to European production efficiency)
- Pork at 4.6 kg CO2eq/kg is much lower than beef but still much higher than plant foods
- Dairy products are surprisingly impactful: butter (9.0), hard cheese (8.5) rival some meats
- Air-freighted produce can be dramatically worse: pineapple by air is 15.1 vs 0.6 by ship (25x difference)

#### German diet composition
- Germans eat ~52-53 kg meat/year (declining trend since 2011, but ticked up in 2024)
- Pork dominates at 27.5 kg, but chicken is growing
- Very high dairy consumption: 46 kg milk, 24 kg cheese, 5.5 kg butter
- 63.5 kg potatoes, ~105 kg vegetables, ~67 kg fruit
- 80+ liters of beer per person per year

#### Annual dietary footprint
- Current average German diet: ~2,000-2,300 kg CO2eq/person/year
- Two-thirds to three-quarters of emissions come from animal products
- My bottom-up calculation from consumption data yields ~1,011 kg, which underestimates because it excludes food waste (~30%), processing, retail energy, cooking energy, and other supply chain stages
- Meat + dairy alone account for ~70% of the food CO2 footprint

#### Reduction potential
- Vegan diet: ~940 kg CO2eq/year (53% reduction)
- Vegetarian: ~1,160 kg (42% reduction)
- Planetary Health Diet: ~1,100 kg (45% reduction)
- 1.5°C compatible target: 590 kg/year (70% reduction needed!)

#### Seasonality and transport
- What you eat matters far more than where it comes from (transport is <10% of most foods' footprint)
- Exception: air freight multiplies emissions 50x vs. sea transport
- Heated greenhouses in winter can be worse than importing from Southern Europe
- Fresh vs. canned/frozen processing adds significant emissions

### What I Built
- `food_co2_analysis.py`: Python script with comprehensive data tables and analysis functions
  - 65+ food items with CO2 emission factors, German names, and sources
  - 10 typical German dishes with ingredient-level CO2 breakdown
  - Annual diet calculation based on BMEL consumption data
  - Diet scenario comparison (omnivore through vegan)
  - Seasonality and transport mode comparison
- `food_co2_data.csv`: Exported food-level CO2 data
- `dish_co2_data.csv`: Exported dish-level CO2 data

### Interesting Observations
1. Beer at 80 kg/year contributes 40 kg CO2eq — more than all vegetables combined (34 kg)
2. Cheese is a "hidden" high-emitter that many people overlook when thinking about dietary change
3. A single Sauerbraten dinner (~3.5 kg CO2eq) has roughly the same footprint as a week of vegan lunches
4. The gap between current German diet and 1.5°C-compatible eating is enormous (70% reduction)
5. Simply following existing DGE dietary guidelines would already reduce emissions by ~30%
6. Germany's self-sufficiency varies hugely by product — nearly self-sufficient in pork and dairy, heavily dependent on imports for fruit and vegetables, especially in winter
