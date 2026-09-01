---
name: generate-ppt-textbook-illustrations
description: Parse a local PPT or PPTX that specifies primary-school extracurricular textbook illustrations, identify bottom-layer backgrounds, transparent atmosphere assets, transparent element assets, and large blue plot-image boxes, then prepare an approval manifest and generate the approved images in a consistent bundled children's-book style. Use when Codex receives a lesson/story presentation and must create all requested textbook illustrations, preserve the named characters 小思、小高、小括狐 from their turnaround references, or validate the resulting PNG asset set.
---

# Generate PPT Textbook Illustrations

Convert a marked-up lesson PPTX into a reviewed image plan, then generate every approved asset with consistent style and character identity.

## Required workflow

1. Locate the user-provided `.pptx`. If several decks exist, use the one the user identifies; otherwise use the only plausible source deck.
2. Create a work directory beside the deck, normally `插图生成/<deck-stem>/`.
3. Run:

   ```bash
   python scripts/analyze_pptx.py <deck.pptx> --output-dir <work-dir>/plan
   ```

4. Read `<work-dir>/plan/illustration-tasks.json` and `<work-dir>/plan/review.txt`.
5. Perform the stage-one review before generating:
   - Confirm every slide with image instructions appears in the manifest.
   - Treat every qualifying large blue box as one separate plot image.
   - Split combined atmosphere/element descriptions into separate tasks when the PPT clearly names multiple standalone assets.
   - Resolve warnings by inspecting the rendered slide or asking one concise question only when the answer materially changes the asset list.
   - Present the task count, filenames, type, page pair, and one-line content summary to the user.
6. Stop for approval. Do not call image generation before the user approves the plan unless the user explicitly asks to skip review.
7. After approval, generate one image per task with the built-in image generation tool. Issue separate calls for distinct assets; do not treat distinct prompts as variants of one call.
8. Save every accepted image to the manifest's `relative_path` under the chosen output root. Never leave project assets only in the image tool's default storage.
9. Run:

   ```bash
   python scripts/validate_outputs.py <work-dir>/plan/illustration-tasks.json --output-root <output-root>
   ```

10. Inspect every final image visually at full size. Fix character drift, incorrect object counts, unreadable dice faces, background-removal halos, unwanted text, watermarks, and composition errors. Re-run validation after replacements.

## Interpretation contract

- `底层图`: one complete opaque background, exactly 16:9. Do not include foreground characters or movable teaching props unless the PPT explicitly requests them as part of the environment.
- `剧情图`: one complete opaque narrative scene per large blue box, exactly 4:3. Use the complete text inside that box as the source of truth.
- `氛围图`: one isolated supporting prop, decoration, or explicitly requested foreground cluster per task, transparent PNG, unrestricted aspect ratio, generous padding.
- `元素图`: one standalone character pose, teaching object, furniture item, or explicitly requested grouped element per task, transparent PNG, unrestricted aspect ratio.
- Preserve page-pair filenames such as `3-4剧情1.png`, `11-12氛围2.png`, and `15-16底层.png`.
- Do not invent additional characters, props, story actions, labels, or written text.
- For ambiguous joined text such as two nouns without punctuation, keep it visible in the review and resolve it before generation.

## References to load

- Read [references/style-guide.md](references/style-guide.md) before writing prompts or judging style.
- Read [references/characters.md](references/characters.md) whenever a task contains 小思、小高, or 小括狐.
- Read [references/prompt-templates.md](references/prompt-templates.md) when constructing generation prompts.
- Read [references/output-contract.md](references/output-contract.md) when revising the manifest, naming outputs, or reporting QA.

## Image generation rules

- Use the built-in image generation tool by default. Treat bundled images as style or character references, not edit targets.
- Label every input image by role in the prompt. Use only the smallest relevant set:
  - character task: the named character anchor(s) plus at most one relevant style sample;
  - plot task: all named character anchors plus one relevant story style sample;
  - bottom-layer task: one background style sample;
  - atmosphere/element task: one matching transparent-asset sample.
- Preserve character identity aggressively: face, hair/fur silhouette, outfit, body proportions, colors, and age impression.
- Generate no speech bubbles, captions, logos, signatures, watermarks, borders, or page furniture.
- For atmosphere and element assets, request a perfectly flat chroma-key background and remove it using the installed image-generation skill's chroma-key helper. Use `#ff00ff` for green subjects; otherwise default to `#00ff00`. Validate alpha and edge quality.
- If chroma-key removal is unsuitable or fails, explain that true native transparency needs the image-generation CLI fallback and user confirmation; do not silently switch models or paths.
- Iterate with one targeted correction at a time and repeat all identity/composition invariants.

## Completion gate

Complete only when:

- the approved manifest and generated file count match;
- all filenames and type directories match the contract;
- every bottom-layer image is 16:9 and every plot image is 4:3;
- every atmosphere/element PNG has useful transparency and clean edges;
- every named character matches the bundled turnaround anchor;
- all required objects, counts, spatial relations, visible dice faces, actions, weather, and mood match the PPT;
- no unrequested text, watermark, or extra object remains;
- `validate_outputs.py` passes and visual inspection passes.
