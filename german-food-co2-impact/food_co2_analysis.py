#!/usr/bin/env python3
"""
CO2 Impact Analysis of Typical Food in Germany

Data sources:
- IFEU (2020): "Ökologische Fußabdrücke von Lebensmitteln und Gerichten in Deutschland"
  Commissioned by the German Federal Environment Agency (Umweltbundesamt)
- Poore & Nemecek (2018): "Reducing food's environmental impacts through producers and consumers", Science
- Our World in Data: Environmental Impacts of Food Production
- BMEL / BLE: German per capita food consumption statistics (2023/2024)
- Umweltbundesamt (UBA): German diet and climate data
"""

import json
import csv

# =============================================================================
# CO2 EMISSION FACTORS (kg CO2eq per kg of food product)
# Primarily based on IFEU 2020 Germany-specific data, supplemented with
# Poore & Nemecek 2018 global averages where German data unavailable
# =============================================================================

FOOD_CO2_DATA = {
    # --- VEGETABLES (German IFEU data where available) ---
    "Carrots": {"co2_per_kg": 0.1, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Karotten"},
    "White cabbage": {"co2_per_kg": 0.1, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Weißkohl"},
    "Potatoes": {"co2_per_kg": 0.2, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Kartoffeln"},
    "Aubergine": {"co2_per_kg": 0.2, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Aubergine"},
    "Onions": {"co2_per_kg": 0.2, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Zwiebeln"},
    "Spinach": {"co2_per_kg": 0.3, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Spinat"},
    "Broccoli": {"co2_per_kg": 0.3, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Brokkoli"},
    "Zucchini": {"co2_per_kg": 0.3, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Zucchini"},
    "Pumpkin": {"co2_per_kg": 0.3, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Kürbis"},
    "Brussels sprouts (fresh)": {"co2_per_kg": 0.4, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Rosenkohl (frisch)"},
    "Brussels sprouts (frozen)": {"co2_per_kg": 0.7, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Rosenkohl (tiefgefroren)"},
    "Tomatoes (seasonal, regional)": {"co2_per_kg": 0.4, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Tomaten (saisonal)"},
    "Tomatoes (greenhouse, heated)": {"co2_per_kg": 2.9, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Tomaten (Gewächshaus)"},
    "Lettuce": {"co2_per_kg": 0.3, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Kopfsalat"},
    "Bell peppers": {"co2_per_kg": 0.5, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Paprika"},
    "Asparagus (regional)": {"co2_per_kg": 0.5, "category": "Vegetables", "source": "IFEU 2020", "german_name": "Spargel (regional)"},
    "Asparagus (air-freighted)": {"co2_per_kg": 5.0, "category": "Vegetables", "source": "IFEU 2020 est.", "german_name": "Spargel (Flugware)"},

    # --- FRUITS ---
    "Apples (regional)": {"co2_per_kg": 0.3, "category": "Fruits", "source": "IFEU 2020", "german_name": "Äpfel (regional)"},
    "Pears": {"co2_per_kg": 0.3, "category": "Fruits", "source": "IFEU 2020", "german_name": "Birnen"},
    "Strawberries (seasonal)": {"co2_per_kg": 0.3, "category": "Fruits", "source": "IFEU 2020", "german_name": "Erdbeeren (saisonal)"},
    "Bananas": {"co2_per_kg": 0.8, "category": "Fruits", "source": "Poore 2018", "german_name": "Bananen"},
    "Oranges": {"co2_per_kg": 0.4, "category": "Fruits", "source": "IFEU 2020", "german_name": "Orangen"},
    "Peaches (fresh)": {"co2_per_kg": 0.2, "category": "Fruits", "source": "IFEU 2020", "german_name": "Pfirsiche (frisch)"},
    "Peaches (canned)": {"co2_per_kg": 1.6, "category": "Fruits", "source": "IFEU 2020", "german_name": "Pfirsiche (Dose)"},
    "Pineapple (ship)": {"co2_per_kg": 0.6, "category": "Fruits", "source": "IFEU 2020", "german_name": "Ananas (Schiff)"},
    "Pineapple (air freight)": {"co2_per_kg": 15.1, "category": "Fruits", "source": "IFEU 2020", "german_name": "Ananas (Flugware)"},
    "Avocado": {"co2_per_kg": 0.8, "category": "Fruits", "source": "IFEU 2020", "german_name": "Avocado"},
    "Berries (air-freighted)": {"co2_per_kg": 10.0, "category": "Fruits", "source": "IFEU 2020 est.", "german_name": "Beeren (Flugware)"},

    # --- GRAINS & LEGUMES ---
    "Wheat bread": {"co2_per_kg": 0.6, "category": "Grains & Legumes", "source": "IFEU 2020", "german_name": "Weizenbrot"},
    "Rye bread": {"co2_per_kg": 0.6, "category": "Grains & Legumes", "source": "IFEU 2020", "german_name": "Roggenbrot"},
    "Pasta": {"co2_per_kg": 0.8, "category": "Grains & Legumes", "source": "IFEU 2020", "german_name": "Nudeln"},
    "Rice": {"co2_per_kg": 3.6, "category": "Grains & Legumes", "source": "IFEU 2020", "german_name": "Reis"},
    "Oats": {"co2_per_kg": 0.5, "category": "Grains & Legumes", "source": "IFEU 2020", "german_name": "Haferflocken"},
    "Lentils": {"co2_per_kg": 0.7, "category": "Grains & Legumes", "source": "Poore 2018", "german_name": "Linsen"},
    "Peas": {"co2_per_kg": 0.4, "category": "Grains & Legumes", "source": "Poore 2018", "german_name": "Erbsen"},
    "Tofu": {"co2_per_kg": 2.0, "category": "Grains & Legumes", "source": "Poore 2018", "german_name": "Tofu"},

    # --- DAIRY ---
    "Cow's milk": {"co2_per_kg": 1.4, "category": "Dairy", "source": "IFEU 2020", "german_name": "Kuhmilch"},
    "Yogurt": {"co2_per_kg": 1.7, "category": "Dairy", "source": "IFEU 2020", "german_name": "Joghurt"},
    "Cheese (hard)": {"co2_per_kg": 8.5, "category": "Dairy", "source": "IFEU 2020", "german_name": "Käse (Hart)"},
    "Cheese (soft, e.g. Quark)": {"co2_per_kg": 5.0, "category": "Dairy", "source": "IFEU 2020", "german_name": "Quark / Weichkäse"},
    "Butter": {"co2_per_kg": 9.0, "category": "Dairy", "source": "IFEU 2020", "german_name": "Butter"},
    "Cream": {"co2_per_kg": 4.2, "category": "Dairy", "source": "IFEU 2020", "german_name": "Sahne"},
    "Eggs": {"co2_per_kg": 3.0, "category": "Eggs", "source": "IFEU 2020", "german_name": "Eier"},

    # --- PLANT-BASED ALTERNATIVES ---
    "Oat milk": {"co2_per_kg": 0.3, "category": "Plant-based", "source": "IFEU 2020", "german_name": "Hafermilch"},
    "Soy milk": {"co2_per_kg": 0.4, "category": "Plant-based", "source": "IFEU 2020", "german_name": "Sojamilch"},
    "Almond milk": {"co2_per_kg": 0.3, "category": "Plant-based", "source": "IFEU 2020", "german_name": "Mandelmilch"},
    "Margarine": {"co2_per_kg": 1.3, "category": "Plant-based", "source": "IFEU 2020", "german_name": "Margarine"},

    # --- MEAT ---
    "Beef": {"co2_per_kg": 13.6, "category": "Meat", "source": "IFEU 2020 (DE avg)", "german_name": "Rindfleisch"},
    "Pork": {"co2_per_kg": 4.6, "category": "Meat", "source": "IFEU 2020", "german_name": "Schweinefleisch"},
    "Chicken": {"co2_per_kg": 5.5, "category": "Meat", "source": "IFEU 2020", "german_name": "Hähnchen"},
    "Lamb": {"co2_per_kg": 25.0, "category": "Meat", "source": "Poore 2018 (EU)", "german_name": "Lammfleisch"},
    "Turkey": {"co2_per_kg": 5.0, "category": "Meat", "source": "IFEU 2020", "german_name": "Putenfleisch"},
    "Processed sausage (Wurst)": {"co2_per_kg": 4.8, "category": "Meat", "source": "IFEU 2020", "german_name": "Wurst"},

    # --- FISH ---
    "Fish (wild-caught, avg)": {"co2_per_kg": 3.5, "category": "Fish", "source": "Poore 2018", "german_name": "Fisch (Wildfang)"},
    "Fish (farmed, avg)": {"co2_per_kg": 5.0, "category": "Fish", "source": "Poore 2018", "german_name": "Fisch (Zucht)"},
    "Shrimp (farmed)": {"co2_per_kg": 12.0, "category": "Fish", "source": "Poore 2018", "german_name": "Garnelen (Zucht)"},

    # --- BEVERAGES ---
    "Coffee": {"co2_per_kg": 5.6, "category": "Beverages", "source": "IFEU 2020", "german_name": "Kaffee"},
    "Beer": {"co2_per_kg": 0.5, "category": "Beverages", "source": "IFEU 2020", "german_name": "Bier"},
    "Wine": {"co2_per_kg": 1.0, "category": "Beverages", "source": "IFEU 2020", "german_name": "Wein"},
    "Orange juice": {"co2_per_kg": 0.7, "category": "Beverages", "source": "IFEU 2020", "german_name": "Orangensaft"},

    # --- OTHER ---
    "Sugar": {"co2_per_kg": 0.5, "category": "Other", "source": "IFEU 2020", "german_name": "Zucker"},
    "Chocolate (dark)": {"co2_per_kg": 4.5, "category": "Other", "source": "IFEU 2020", "german_name": "Schokolade (dunkel)"},
    "Nuts (mixed)": {"co2_per_kg": 1.2, "category": "Other", "source": "IFEU 2020", "german_name": "Nüsse (gemischt)"},
    "Olive oil": {"co2_per_kg": 3.5, "category": "Other", "source": "Poore 2018", "german_name": "Olivenöl"},
    "Rapeseed oil": {"co2_per_kg": 2.5, "category": "Other", "source": "IFEU 2020", "german_name": "Rapsöl"},
}


# =============================================================================
# GERMAN PER CAPITA FOOD CONSUMPTION (kg/year)
# Based on BMEL / BLE supply balance data 2023/2024
# =============================================================================

GERMAN_CONSUMPTION_KG_PER_YEAR = {
    # Meat (total ~52 kg in 2024)
    "Pork": 27.5,
    "Chicken": 13.1,
    "Beef": 8.9,
    "Turkey": 2.0,
    "Processed sausage (Wurst)": 5.0,  # additional processed meat est.
    "Lamb": 0.7,

    # Dairy
    "Cow's milk": 46.2,
    "Yogurt": 15.0,
    "Cheese (hard)": 14.0,
    "Cheese (soft, e.g. Quark)": 10.0,
    "Butter": 5.5,
    "Cream": 7.0,

    # Eggs
    "Eggs": 13.5,  # ~230 eggs/year, ~60g each

    # Vegetables (~105 kg total)
    "Tomatoes (seasonal, regional)": 30.0,
    "Carrots": 10.0,
    "Onions": 8.0,
    "White cabbage": 4.0,
    "Bell peppers": 5.0,
    "Lettuce": 5.0,
    "Potatoes": 63.5,
    "Broccoli": 2.0,
    "Spinach": 1.5,
    "Zucchini": 2.0,
    "Asparagus (regional)": 1.5,

    # Fruits (~67 kg total)
    "Apples (regional)": 20.0,
    "Bananas": 12.0,
    "Oranges": 8.0,
    "Strawberries (seasonal)": 3.5,
    "Pears": 3.0,
    "Avocado": 1.5,
    "Pineapple (ship)": 2.0,

    # Grains
    "Wheat bread": 40.0,
    "Rye bread": 15.0,
    "Pasta": 8.0,
    "Rice": 6.5,
    "Oats": 3.0,

    # Beverages
    "Coffee": 4.0,  # ~500g/month dry weight
    "Beer": 80.0,  # ~92 liters/year (Germany!)
    "Wine": 20.0,
    "Orange juice": 8.0,

    # Other
    "Sugar": 30.4,
    "Chocolate (dark)": 3.0,
    "Nuts (mixed)": 5.2,
    "Rapeseed oil": 5.0,
    "Margarine": 3.0,
}


# =============================================================================
# TYPICAL GERMAN DISHES - Estimated CO2 per serving
# =============================================================================

GERMAN_DISHES = {
    "Schweineschnitzel mit Kartoffelsalat": {
        "description": "Breaded pork cutlet with potato salad",
        "ingredients": [
            ("Pork", 0.200),
            ("Wheat bread", 0.030),  # breading
            ("Eggs", 0.030),
            ("Potatoes", 0.250),
            ("Onions", 0.030),
            ("Rapeseed oil", 0.030),
        ],
    },
    "Bratwurst mit Brötchen und Senf": {
        "description": "Grilled pork sausage with bread roll and mustard",
        "ingredients": [
            ("Processed sausage (Wurst)", 0.150),
            ("Wheat bread", 0.060),
        ],
    },
    "Currywurst mit Pommes": {
        "description": "Curry sausage with fries",
        "ingredients": [
            ("Processed sausage (Wurst)", 0.170),
            ("Potatoes", 0.200),  # fries
            ("Rapeseed oil", 0.020),  # deep frying
            ("Sugar", 0.010),  # ketchup/sauce
        ],
    },
    "Sauerbraten mit Rotkohl und Klößen": {
        "description": "Marinated pot roast with red cabbage and dumplings",
        "ingredients": [
            ("Beef", 0.250),
            ("White cabbage", 0.200),  # red cabbage similar
            ("Potatoes", 0.200),  # Klöße
            ("Onions", 0.030),
            ("Wine", 0.050),  # marinade
        ],
    },
    "Spaghetti Bolognese": {
        "description": "Pasta with meat sauce (very popular in Germany)",
        "ingredients": [
            ("Pasta", 0.125),
            ("Beef", 0.100),
            ("Pork", 0.050),
            ("Tomatoes (seasonal, regional)", 0.150),
            ("Onions", 0.030),
            ("Olive oil", 0.015),
        ],
    },
    "Käsespätzle": {
        "description": "Swabian cheese noodles",
        "ingredients": [
            ("Pasta", 0.200),  # Spätzle
            ("Cheese (hard)", 0.100),
            ("Eggs", 0.050),
            ("Onions", 0.040),
            ("Butter", 0.020),
        ],
    },
    "Kartoffelsuppe": {
        "description": "Potato soup",
        "ingredients": [
            ("Potatoes", 0.300),
            ("Carrots", 0.050),
            ("Onions", 0.050),
            ("Cream", 0.050),
            ("Wheat bread", 0.060),  # bread on the side
        ],
    },
    "Gemüsepfanne (vegan)": {
        "description": "Vegetable stir-fry with rice (vegan)",
        "ingredients": [
            ("Rice", 0.100),
            ("Bell peppers", 0.100),
            ("Zucchini", 0.100),
            ("Broccoli", 0.100),
            ("Carrots", 0.080),
            ("Rapeseed oil", 0.015),
        ],
    },
    "Butterbrot mit Käse": {
        "description": "Bread with butter and cheese (classic German breakfast/Abendbrot)",
        "ingredients": [
            ("Rye bread", 0.100),
            ("Butter", 0.015),
            ("Cheese (hard)", 0.040),
        ],
    },
    "Frühstück (typisch)": {
        "description": "Typical German breakfast: bread, butter, jam, cheese, egg, coffee",
        "ingredients": [
            ("Wheat bread", 0.100),
            ("Butter", 0.020),
            ("Cheese (hard)", 0.030),
            ("Eggs", 0.060),  # 1 egg
            ("Sugar", 0.020),  # jam
            ("Coffee", 0.010),
        ],
    },
}


def calc_dish_co2(dish_data):
    """Calculate total CO2 for a dish based on its ingredients."""
    total = 0.0
    breakdown = []
    for food_name, weight_kg in dish_data["ingredients"]:
        co2_factor = FOOD_CO2_DATA[food_name]["co2_per_kg"]
        co2 = weight_kg * co2_factor
        total += co2
        breakdown.append((food_name, weight_kg, co2_factor, co2))
    return total, breakdown


def calc_annual_diet_co2():
    """Calculate the annual CO2 footprint of the average German diet."""
    total = 0.0
    by_category = {}
    items = []
    for food_name, kg_per_year in GERMAN_CONSUMPTION_KG_PER_YEAR.items():
        if food_name in FOOD_CO2_DATA:
            co2_factor = FOOD_CO2_DATA[food_name]["co2_per_kg"]
            annual_co2 = kg_per_year * co2_factor
            category = FOOD_CO2_DATA[food_name]["category"]
            total += annual_co2
            by_category[category] = by_category.get(category, 0) + annual_co2
            items.append((food_name, kg_per_year, co2_factor, annual_co2, category))
    return total, by_category, items


def print_food_table():
    """Print all food items sorted by CO2 per kg."""
    print("=" * 80)
    print("CO2 EMISSIONS PER KG OF FOOD PRODUCTS IN GERMANY")
    print("=" * 80)
    print(f"{'Food':<35} {'German Name':<25} {'kg CO2eq/kg':>12} {'Source':<18}")
    print("-" * 80)

    sorted_foods = sorted(FOOD_CO2_DATA.items(), key=lambda x: x[1]["co2_per_kg"])
    current_cat = None
    for name, data in sorted_foods:
        if data["category"] != current_cat:
            current_cat = data["category"]
        print(f"{name:<35} {data['german_name']:<25} {data['co2_per_kg']:>10.1f}   {data['source']:<18}")
    print()


def print_dish_analysis():
    """Print CO2 analysis of typical German dishes."""
    print("=" * 80)
    print("CO2 FOOTPRINT OF TYPICAL GERMAN DISHES")
    print("=" * 80)

    dishes_sorted = []
    for dish_name, dish_data in GERMAN_DISHES.items():
        total, breakdown = calc_dish_co2(dish_data)
        dishes_sorted.append((dish_name, dish_data, total, breakdown))

    dishes_sorted.sort(key=lambda x: x[2])

    for dish_name, dish_data, total, breakdown in dishes_sorted:
        print(f"\n  {dish_name}")
        print(f"  {dish_data['description']}")
        print(f"  {'Ingredient':<30} {'Weight':>8} {'CO2/kg':>8} {'CO2':>10}")
        print(f"  {'-'*58}")
        for food_name, weight, factor, co2 in breakdown:
            print(f"  {food_name:<30} {weight*1000:>6.0f}g  {factor:>6.1f}   {co2*1000:>7.0f}g")
        print(f"  {'':30} {'':>8} {'TOTAL:':>8} {total*1000:>7.0f}g CO2eq")
    print()


def print_annual_diet():
    """Print annual diet CO2 analysis."""
    total, by_category, items = calc_annual_diet_co2()

    print("=" * 80)
    print("ANNUAL CO2 FOOTPRINT OF THE AVERAGE GERMAN DIET")
    print("=" * 80)

    print(f"\nTotal estimated annual food CO2: {total:.0f} kg CO2eq/person/year")
    print(f"  (Literature value: ~1,700-2,300 kg CO2eq/person/year)")
    print()

    print("Breakdown by food category:")
    print(f"  {'Category':<20} {'kg CO2eq/year':>15} {'Share':>8}")
    print(f"  {'-'*45}")
    for cat, co2 in sorted(by_category.items(), key=lambda x: -x[1]):
        pct = co2 / total * 100
        bar = "#" * int(pct / 2)
        print(f"  {cat:<20} {co2:>13.1f}   {pct:>5.1f}%  {bar}")
    print()

    print("Top 10 individual food items by annual CO2 contribution:")
    print(f"  {'Food':<35} {'kg/year':>8} {'CO2/kg':>8} {'Annual CO2':>12}")
    print(f"  {'-'*65}")
    items.sort(key=lambda x: -x[3])
    for name, kg, factor, annual, cat in items[:10]:
        print(f"  {name:<35} {kg:>6.1f}   {factor:>6.1f}   {annual:>10.1f} kg")
    print()


def print_diet_comparison():
    """Print comparison of different diet scenarios."""
    print("=" * 80)
    print("DIET SCENARIO COMPARISON (kg CO2eq/person/year)")
    print("=" * 80)

    scenarios = {
        "Average German diet (current)": 2000,
        "DGE recommended diet": 1400,
        "Flexitarian (Planetary Health Diet)": 1100,
        "Vegetarian": 1160,
        "Vegan": 940,
        "1.5°C compatible target (IPCC)": 590,
    }

    max_val = max(scenarios.values())
    for name, val in scenarios.items():
        bar_len = int(val / max_val * 40)
        bar = "█" * bar_len
        print(f"  {name:<40} {val:>6} kg  {bar}")

    print(f"\n  Reduction needed for 1.5°C target: {(1-590/2000)*100:.0f}% from current diet")
    print()


def print_seasonal_impact():
    """Show the impact of seasonality and transport mode."""
    print("=" * 80)
    print("IMPACT OF SEASONALITY AND TRANSPORT ON CO2")
    print("=" * 80)

    comparisons = [
        ("Tomatoes seasonal/regional", 0.4, "Tomatoes heated greenhouse", 2.9),
        ("Asparagus regional", 0.5, "Asparagus air-freighted", 5.0),
        ("Pineapple by ship", 0.6, "Pineapple by air", 15.1),
        ("Berries seasonal local", 0.3, "Berries air-freighted", 10.0),
        ("Peaches fresh", 0.2, "Peaches canned", 1.6),
        ("Brussels sprouts fresh", 0.4, "Brussels sprouts frozen", 0.7),
        ("Cow's milk", 1.4, "Oat milk", 0.3),
        ("Butter", 9.0, "Margarine", 1.3),
        ("Beef", 13.6, "Tofu", 2.0),
        ("Cheese (hard)", 8.5, "Lentils", 0.7),
    ]

    print(f"\n  {'Option A':<28} {'CO2':>6}   {'Option B':<28} {'CO2':>6}   {'Savings':>8}")
    print(f"  {'-'*85}")
    for a_name, a_co2, b_name, b_co2, in comparisons:
        if a_co2 > b_co2:
            high, low = a_co2, b_co2
            saving = (1 - low/high) * 100
            print(f"  {b_name:<28} {b_co2:>5.1f}   {a_name:<28} {a_co2:>5.1f}   {saving:>6.0f}%")
        else:
            high, low = b_co2, a_co2
            saving = (1 - low/high) * 100
            print(f"  {a_name:<28} {a_co2:>5.1f}   {b_name:<28} {b_co2:>5.1f}   {saving:>6.0f}%")
    print()


def export_data_csv():
    """Export food CO2 data as CSV for further use."""
    filepath = "/home/user/research/german-food-co2-impact/food_co2_data.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Food", "German Name", "Category", "kg_CO2eq_per_kg", "Source"])
        for name, data in sorted(FOOD_CO2_DATA.items(), key=lambda x: (x[1]["category"], x[1]["co2_per_kg"])):
            writer.writerow([name, data["german_name"], data["category"], data["co2_per_kg"], data["source"]])
    print(f"Exported food CO2 data to {filepath}")

    # Export dish data
    filepath2 = "/home/user/research/german-food-co2-impact/dish_co2_data.csv"
    with open(filepath2, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Dish", "Description", "Total_kg_CO2eq"])
        for dish_name, dish_data in GERMAN_DISHES.items():
            total, _ = calc_dish_co2(dish_data)
            writer.writerow([dish_name, dish_data["description"], round(total, 3)])
    print(f"Exported dish CO2 data to {filepath2}")


if __name__ == "__main__":
    print_food_table()
    print_dish_analysis()
    print_annual_diet()
    print_diet_comparison()
    print_seasonal_impact()
    export_data_csv()
