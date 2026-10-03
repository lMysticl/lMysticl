"""Build compact images from the retained background and satellite atlas.

Only web sizing, atlas-cell extraction and lossless WebP encoding happen here.
The source artwork is never recolored or repainted.
"""

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets' / 'business'
WEB = ROOT / 'assets' / 'web'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_webp(image, name):
    path = WEB / (name + '.webp')
    pending = path.with_suffix('.webp.tmp')
    image.save(pending, format='WEBP', lossless=True, exact=True, method=6)
    with Image.open(pending) as decoded:
        if decoded.convert('RGBA').tobytes() != image.convert('RGBA').tobytes():
            raise ValueError(f'Decoded pixel mismatch: {name}')
    pending.replace(path)
    return {'path': path.relative_to(ROOT).as_posix(), 'dimensions': list(image.size),
            'bytes': path.stat().st_size, 'sha256': digest(path), 'rgba_equal': True}


def build():
    WEB.mkdir(parents=True, exist_ok=True)
    background = SOURCE / 'cover-background.png'
    atlas_path = SOURCE / 'satellite-atlas.png'
    with Image.open(background) as original:
        normalized = original.convert('RGB').resize((1200, 430), Image.Resampling.LANCZOS)
    images = [save_webp(normalized, 'business-background')]
    with Image.open(atlas_path) as original:
        atlas = original.convert('RGBA')
    if atlas.getextrema()[3] == (255, 255):
        raise ValueError('Satellite atlas must have a transparent background')
    for i, name in enumerate(('purple', 'gold', 'teal')):
        cell = atlas.crop((round(i * atlas.width / 3), 0,
                           round((i + 1) * atlas.width / 3), atlas.height))
        alpha = cell.getchannel('A')
        bounds = alpha.getbbox()
        if bounds is None:
            raise ValueError(f'Empty satellite cell: {name}')
        # ImageGen leaves alpha 1-4 dust in otherwise empty gutters. Inspect
        # the actual silhouette without deleting or changing those RGBA pixels.
        silhouette = alpha.point(lambda value: 255 if value > 4 else 0).getbbox()
        if silhouette is None or silhouette[0] < 2 or silhouette[2] > cell.width - 2:
            raise ValueError(f'Clipped satellite cell: {name}')
        cropped = cell.crop(bounds)
        cropped.thumbnail((116, 116), Image.Resampling.LANCZOS)
        sprite = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        sprite.paste(cropped, ((128 - cropped.width) // 2, (128 - cropped.height) // 2))
        images.append(save_webp(sprite, 'satellite-' + name))
    proof = {'schema_version': 1, 'sources': [
        {'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p)}
        for p in (background, atlas_path)], 'images': images,
        'operations': 'One 1200x430 background resize. Three atlas cells, alpha trim, 128x128 web canvases. Derived RGBA pixels checked after lossless encoding.'}
    target = WEB / 'business-encoding-proof.json'
    pending = target.with_suffix('.json.tmp')
    pending.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    pending.replace(target)
    print(json.dumps({'images': images, 'proof': str(target.relative_to(ROOT))}))


if __name__ == '__main__':
    build()
