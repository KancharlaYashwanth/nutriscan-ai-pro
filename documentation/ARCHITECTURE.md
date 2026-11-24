# Architecture (planned)

Browser UI -> Flask REST API -> Product API adapter (Open Food Facts)
                                      -> Product normalization / missing-data checks
                                      -> Nutrition display

Later:
Image upload -> OCR -> human-checkable structured extraction
Food photo -> CNN classifier (optional food-category feature)
Ingredient text -> NLP / dictionary -> ingredient & allergen flags
User profile + normalized product facts -> medically reviewed rules engine
Rules output -> explanation layer (LLM optional; cannot override rules)
Recommendation candidates -> dietary filters -> transparent ranking

The rules engine must fail safely when data is missing. It must not issue a medical clearance or guarantee allergy safety.
