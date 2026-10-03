# Profile image sources and web assets

The selected cover is the user's dark Fullstack reference with daylight Earth,
the original APIs / Services / Data satellites and five technology groups:
Java 21, Spring Boot, PostgreSQL, Kafka and React / TypeScript. The heading is
exactly **Fullstack Java Developer**, with no personal name. Both GitHub theme
variants deliberately retain that same selected dark design.

The background and three detailed spacecraft models are retained under
assets/business as original ImageGen PNG masters, with source identities in
source.json. The web producer resizes the background once to 1200 x 430,
extracts the three atlas cells, retains alpha pixels, and encodes four lossless
WebP images. Decoded derived RGBA equality and file identities are recorded in
business-encoding-proof.json. Each SVG embeds each image once and reuses it.

Rebuild the current cover with the existing Pillow runtime:

    python -B scripts/build_profile_business_assets.py
    python -B scripts/build_profile_orbits.py

The cover producer recognizes business-dark in existing SVGs. Use --business
when selecting it from a historical cinematic cover. Both producers validate
their output and replace files atomically on the same filesystem.

Eight spacecraft and their upright captions follow perspective orbital paths.
The three service orbits take 64 seconds; the five technology orbits take 96
seconds. The whole composition repeats after 192 seconds. Synchronized
front/back layers and reuse of the Earth region provide occlusion. Rear
captions fade as a whole before Earth could cut their letters, and a small
continuous caption offset protects the upper frame boundary. No runtime
JavaScript, WebGL, external images or GIF decoder is needed.

Desktop is 1200 x 430. Mobile is 640 x 700, with the same copy above the Earth.
The README picture element selects desktop/mobile, dark/light and
animated/static variants. Reduced-motion preferences freeze the composition;
the animated SVG also provides a native CSS fallback.

The earlier planet PNGs, NASA-map provenance, editable Blender scenes,
85-view fighter atlases, camera manifests and cinematic producers remain
available in the repository and Git history. Their original four planet WebP
images and two eight-view fighter WebP atlases are retained for those earlier
covers; the current selected business cover does not embed them.

Historical image encodings can still be rebuilt separately:

    python -B scripts/build_profile_web_assets.py

That producer verifies decoded original RGBA equality before replacement.
Its encoding-proof.json records the historical planet/ship asset identities.
