# Ingredient screening and food-photo limitations

The 122-term dictionary is a transparent ingredient screening vocabulary, not a toxic-ingredient blacklist. It includes allergen terms, additives requiring context, nutrition-watch terms, dietary preference terms and contaminant names. Contaminants such as lead, arsenic and aflatoxins cannot be identified from a normal barcode ingredient list; they require laboratory analysis.

A match does not mean that a product is unsafe. Additive permissions and maximum levels depend on current FSSAI rules, food category, formulation and jurisdiction. Keep source references and review dates current before public release. User allergy matches are high-priority prompts, but ingredient databases can be incomplete and cross-contact information may be absent. Always advise users to verify the physical label and follow qualified allergy guidance.

The local-food photo page currently captures a photo and asks the user to confirm a food category. Its nutrition values are generic reference estimates with a preparation multiplier, not computer-vision measurements. It does not yet contain a trained food recognition or portion-weight model. A production model needs a suitable dataset, validation on Indian foods, confidence thresholds, user confirmation and uncertainty ranges. A single RGB photo cannot reliably infer hidden oil, sugar, salt or exact weight.


## Consumption decision labels
- **YES**: the available record includes basic nutrition and ingredient fields and no match was found against allergies entered in the user's profile. It does not mean medically safe, healthy, or suitable for every person.
- **NO**: a possible match was found between a declared ingredient/allergen and an allergy entered by the user. Users should avoid the product pending qualified advice.
- **UNKNOWN**: key ingredient/nutrition data is missing. Do not interpret missing data as safe.

The serving guide uses the product's declared serving size when a compatible g/ml value can be parsed. Otherwise it uses a generic 30 g solid-food or 200 ml beverage starting reference. These are UI defaults, not individualized dietary prescriptions. Nutrition is scaled from per-100 g/ml data. High nutrient amounts generate review notes rather than automatic danger classifications. Beverage identification is heuristic and should be checked against the product packaging.
