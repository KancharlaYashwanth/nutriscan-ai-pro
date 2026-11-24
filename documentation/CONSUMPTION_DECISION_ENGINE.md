# Consumption Decision Engine

## What it does
- Classifies a product as a solid food or beverage using Open Food Facts product categories, product name and package unit clues.
- Displays EDIBLE / NOT EDIBLE for solid foods, DRINKABLE / NOT DRINKABLE for beverages, or UNKNOWN when the product type or evidence is insufficient.
- Checks the signed-in user's saved allergy terms against declared allergens and ingredient text. A match produces a do-not-consume warning.
- Suggests a portion using the package serving size where available, then applies transparent educational nutrient caps where data exists (approximately 10 g sugars, 400 mg sodium and 200 kcal per suggested portion).
- Preserves age, height, weight, activity, diet, allergies, health conditions and goals in the existing profile. Health conditions add caution notes; they do not generate medical prescriptions.

## Important limitations
This is a transparent rule-based screening feature, not a validated machine-learning model or food-safety certification. A positive EDIBLE/DRINKABLE result means only that the database classifies the item as food/beverage and no saved-allergy text match was detected. It cannot verify contamination, spoilage, cross-contact, undeclared allergens or individual medical suitability. Product data may be incomplete or incorrect. Always check the physical package and follow qualified medical advice for allergies or health conditions.

## Portion calculation
The calculation starts with the package serving size if supplied; otherwise it starts with 30 g for solids or 200 ml for beverages. Where available, the portion is reduced to keep the estimated portion near or below 10 g sugars, 400 mg sodium and 200 kcal. These are screening heuristics, not universal dietary limits. The interface labels the result as educational guidance.
