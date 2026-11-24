# NutriScan AI — Dataset and model-training plan

## Key principle
Not every feature needs a trained dataset. Barcode lookup is a database/API operation, not a deep-learning task. Open Food Facts can provide product records and nutrient fields when a record exists. Its records can be incomplete or community-contributed; always show missing fields and verify packaging.

## Dataset plan

### 1. Food-101 — first CNN experiment
- Use: image classification of 101 prepared-food categories.
- Size: 101,000 images.
- Limitation: this is not a packaged-brand/barcode dataset. It will not recognize every biscuit/chips brand.
- Source: https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/
- Alternative hosted dataset card: https://huggingface.co/datasets/ethz/food101
- Start with transfer learning (MobileNetV3 or EfficientNet) rather than training a large CNN from scratch.

### 2. Nutrition5k — optional advanced research
- Use: visual nutrition estimation research on plated foods.
- About 5,006 plates with visual data and nutrient/mass annotations.
- Download is about 181 GB; do not download for the first milestone.
- Source: https://github.com/google-research-datasets/Nutrition5k
- Limitation: mostly cafeteria plates, not packaged snack labels.

### 3. OCR label data — later
- Start with a pretrained OCR model (PaddleOCR) and validate extracted values.
- For fine-tuning, build a small, licensed, consented set of packaging-label photos with annotations for nutrient name, value, unit, serving size and ingredients.
- Split by product/package into train/validation/test to avoid nearly identical images leaking across splits.
- Do not use OCR output as ground truth without human verification.

### 4. Ingredient and allergen NLP — later
- Begin with a curated ingredient/allergen dictionary and transparent rules.
- If training BERT/DistilBERT, create or obtain a legally usable labeled dataset with ingredient spans/classes (e.g. milk, peanut, soy, wheat/gluten, additive categories).
- Labels must be reviewed. An absent allergen word does not prove a product is safe.
- Do not invent a dataset or report performance without evaluation.

### 5. Recommendation model — later
- Start with deterministic ranking using product nutrients, user preferences and hard constraints.
- For a trained recommendation model, collect consented, de-identified preference/feedback data and product features.
- Never train a model to decide medical safety. Enforce medically reviewed rules separately.

## What to download now
Nothing is required to run the current starter. For the first deep-learning milestone, download Food-101 only when ready to train the CNN. Nutrition5k is optional and large.

## Suggested model experiments
- CNN: transfer-learn MobileNetV3 on Food-101; report accuracy, precision, recall, macro F1 and confusion matrix.
- OCR: evaluate text/nutrient extraction on a manually annotated label set using character/word error rates and field-level exact match.
- NLP: evaluate ingredient/allergen entity extraction with precision, recall and F1.
- Recommendation: evaluate ranking relevance (Precision@K / Recall@K) only after collecting valid feedback data.

## Hardware and environment
Use Python 3.11 or 3.12 for the project starter. Install PyTorch using the official selector for the laptop OS and hardware: https://pytorch.org/get-started/locally/
Do not assume CUDA is available. CPU training is possible for small experiments but may be slow.
