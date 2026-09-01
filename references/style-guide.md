# Style guide

## Core look

Use a polished 2D children's-book illustration style for Chinese primary-school extracurricular textbooks:

- bright, high-saturation colors with a friendly warm bias;
- rounded silhouettes, simplified geometry, large readable shapes;
- clean digital painting with soft gradients and restrained highlights;
- minimal surface noise and no photorealistic texture;
- large expressive eyes, soft cheeks, compact childlike proportions;
- clear foreground/midground/background separation;
- cheerful, safe, readable staging even during rain, danger, or conflict;
- no heavy ink outlines, gritty rendering, anime realism, 3D toy rendering, collage, or photographic elements.

Use the images under `assets/style-references/` as visual anchors. Match their visual language without copying a scene.

## Composition by type

### Bottom layer

- Exactly 16:9 and fully opaque.
- Build an environment with open usable space for later placement of characters and teaching elements.
- Keep perspective simple and stable; avoid dramatic lens distortion.
- Exclude foreground characters and movable assets unless the PPT explicitly includes them in the background brief.
- Make the scene readable at textbook size.

### Plot image

- Exactly 4:3 and fully opaque.
- Show one clear story beat from the complete blue-box description.
- Make the main action readable immediately; stage secondary details behind it.
- Preserve requested left/right, front/back, touching/opposite, top/bottom, and visible-face relationships.
- Keep every named character recognizable and visible enough to verify identity and action.
- For mathematical props such as dice, render the requested number of dice and only the specified visible pips. Do not add decorative pips that change the problem.

### Atmosphere asset

- Transparent PNG with a tight but comfortable crop.
- Isolate one supporting prop, decorative object, or explicitly requested foreground cluster.
- Use a front or mild three-quarter view unless the PPT requires another angle.
- No floor plane, scene background, cast shadow outside the cutout, or unrelated decoration.

### Element asset

- Transparent PNG with the full requested object, character pose, or explicitly grouped element visible.
- Preserve clean silhouette, generous padding, and consistent scale.
- For character poses, keep the original outfit and body proportions; change only pose and expression.
- For furniture and teaching objects, use simple rounded geometry and restrained shading consistent with the story scenes.

## Palette and finish

- Sky/water blues: clear cyan-to-royal blue.
- Grass/foliage: fresh yellow-green to medium green.
- Warm props/interiors: honey yellow, orange, light tan, soft brown.
- Structural accents: vivid red, white, navy, and warm gray.
- Shadows: soft colored shadows, never muddy black.
- Avoid dirty beige filters, neon bloom, excessive gloss, hard cinematic contrast, and dense texture.

## Visual QA

Reject and regenerate when any of these occur:

- character face, hair/fur, outfit, or proportions drift from the turnaround;
- hands or feet are malformed or important interactions are unclear;
- object count, dice count, pip count, or spatial relation differs from the PPT;
- a transparent asset retains colored matte fragments, halos, checkerboards, or background scenery;
- the image contains text, speech bubbles, borders, logos, signatures, or watermarks;
- key content is cropped or too small to read at page size;
- the style becomes photorealistic, painterly, 3D, anime, or overly detailed.
