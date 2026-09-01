# Prompt templates

Use short labeled prompts. Preserve the PPT's specificity; do not add story content.

## Bottom layer

```text
Use case: illustration-story
Asset type: primary-school textbook bottom-layer background
Primary request: <PPT description>
Input images: Image 1: background style reference
Scene/backdrop: <environment, weather, time of day>
Style/medium: polished flat 2D Chinese children's textbook illustration; rounded geometry; bright colors; soft restrained gradients
Composition/framing: exact 16:9; stable wide view; clear foreground, midground, background; reserve open usable placement space
Constraints: environment only unless explicitly requested; fully opaque; no people; no text; no speech bubbles; no watermark; no border
Avoid: photorealism; 3D render; anime; heavy outlines; gritty texture; dramatic lens distortion
```

## Plot image

```text
Use case: illustration-story
Asset type: primary-school textbook narrative scene
Primary request: <complete blue-box description>
Input images: Image 1..N: named character anchors; final image: story style reference
Scene/backdrop: <location, weather, time>
Subject: <characters, actions, required props, object counts, spatial relations>
Style/medium: same polished flat 2D children's textbook illustration style as the references
Composition/framing: exact 4:3; one immediately readable story beat; all required characters and key objects clearly visible
Constraints: preserve every named character's face, silhouette, outfit, colors, age, and proportions; obey requested object and dice-pip counts; no extra characters or props; fully opaque; no text; no speech bubbles; no watermark; no border
Avoid: identity drift; costume changes; merged characters; malformed hands; cropped key action; photorealism; 3D render; anime
```

## Atmosphere asset

```text
Use case: background-extraction
Asset type: isolated primary-school textbook atmosphere asset
Primary request: <single object>
Input images: Image 1: transparent atmosphere style reference
Subject: one complete <object or explicitly requested foreground cluster>, isolated
Style/medium: polished flat 2D children's textbook asset; rounded shape; bright friendly color; soft restrained shading
Composition/framing: unrestricted aspect ratio; centered; full silhouette; generous padding
Scene/backdrop: perfectly flat solid <key color> chroma-key background for local removal
Constraints: only the requested asset or cluster; uniform key background; no floor plane; no cast shadow; no extra decoration; no text; no watermark; do not use <key color> in the subject
```

## Element asset

```text
Use case: background-extraction
Asset type: isolated primary-school textbook reusable element
Primary request: <single object or named character pose>
Input images: Image 1: character anchor when applicable; Image 2: matching element style reference
Subject: one complete <object/character and pose>
Style/medium: polished flat 2D children's textbook asset; rounded geometry; bright colors; soft restrained gradients
Composition/framing: unrestricted aspect ratio; centered; full body/object visible; generous padding
Scene/backdrop: perfectly flat solid <key color> chroma-key background for local removal
Constraints: preserve character identity and outfit when applicable; change only pose/expression; one isolated subject; no floor plane; no cast shadow; no text; no watermark; do not use <key color> in the subject
```

## Revision prompt

```text
Change only: <one targeted correction>.
Keep unchanged: character identity, outfit, proportions, composition, camera, palette, background, all correct object counts and spatial relationships.
Still required: exact target aspect ratio; no text; no speech bubbles; no watermark; no extra objects.
```
