# Water Preparedness Bundle — Design

## Information Architecture
- **Hub:** `water-preparedness-ladder` — defines the ladder stages, TL;DR, Why, How, Related, FAQ.
- **Spokes:** three pages aligned to the hub:
  - `water-storage-containers-review`
  - `sanitize-water-bricks-guide`
  - `emergency-filtration-roundup`

## Templates
- hub → `hub.md.j2`
- guide/review/roundup → corresponding Jinja templates in `praeparium/templates/`

## Narrative Flow
1. TL;DR
2. Why it matters
3. How to do it (stepwise)
4. Common pitfalls
5. Related links (interlinks)
6. FAQs

## Notes
- Use consistent callouts for safety, time, cost.
- Include quick-reference tables where helpful.
