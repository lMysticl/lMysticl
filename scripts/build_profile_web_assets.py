"""Derive small, lossless web sprites from the retained full-resolution renders.

Pillow 12.3's WebP encoder supports exact transparent RGB preservation. Verify
every decoded RGBA byte before replacing an asset beside its temporary file.
No Blender master, source render, camera pose or cannon coordinate is changed.
"""
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / 'assets'
OUTPUT = ROOT / 'web'
VIEWS = (6, 10, 14, 18, 22, 26, 30, 34)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_exact(image, path):
    temporary = path.with_suffix('.webp.tmp')
    image = image.convert('RGBA')
    image.save(temporary, format='WEBP', lossless=True, method=6, exact=True)
    with Image.open(temporary) as decoded:
        assert decoded.size == image.size
        assert decoded.convert('RGBA').tobytes() == image.tobytes(), path.name
    # Leave an identical destination alone, including when an image preview
    # holds a read handle on Windows. Changed bytes still replace atomically.
    if path.exists() and temporary.read_bytes() == path.read_bytes():
        temporary.unlink()
    else:
        temporary.replace(path)


def build():
    OUTPUT.mkdir(exist_ok=True)
    proof = {'encoding': 'lossless WebP, exact RGBA', 'planets': {}, 'fighters': {}}
    for name in ('core', 'amber', 'moon', 'ocean'):
        source = ROOT / 'planets-3d' / (name + '.png')
        target = OUTPUT / (name + '.webp')
        with Image.open(source) as image:
            save_exact(image, target)
            proof['planets'][name] = {'source_sha256': sha(source),
                'output_sha256': sha(target), 'size': list(image.size),
                'source_bytes': source.stat().st_size, 'web_bytes': target.stat().st_size}
    for stem in ('aster-ship', 'vesper-interceptor'):
        source = ROOT / 'spacecraft-3d' / (stem + '.png')
        manifest_path = source.with_suffix('.json')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        width, height = manifest['frames'][0]['tile'][2:]
        atlas = Image.new('RGBA', (4 * width, 2 * height))
        frames = []
        with Image.open(source) as full:
            for i, index in enumerate(VIEWS):
                frame = dict(manifest['frames'][index])
                x, y, w, h = frame['tile']
                tile = full.crop((x, y, x + w, y + h)).convert('RGBA')
                ax, ay = (i % 4) * width, (i // 4) * height
                atlas.paste(tile, (ax, ay))
                frame.update(source_index=index, tile=[ax, ay, w, h])
                frames.append(frame)
        target = OUTPUT / (stem + '.webp')
        save_exact(atlas, target)
        compact = {'width': atlas.width, 'height': atlas.height, 'frames': frames,
                   'source_atlas_sha256': sha(source),
                   'source_manifest_sha256': sha(manifest_path)}
        temporary = OUTPUT / (stem + '.json.tmp')
        temporary.write_text(json.dumps(compact, indent=2) + '\n', encoding='utf-8')
        temporary.replace(OUTPUT / (stem + '.json'))
        proof['fighters'][stem] = {'source_bytes': source.stat().st_size,
            'web_bytes': target.stat().st_size, 'source_size': [manifest['width'], manifest['height']],
            'web_size': list(atlas.size), 'selected_source_views': list(VIEWS),
            'source_sha256': sha(source), 'output_sha256': sha(target)}
    temporary = OUTPUT / 'encoding-proof.json.tmp'
    temporary.write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    temporary.replace(OUTPUT / 'encoding-proof.json')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    build()
