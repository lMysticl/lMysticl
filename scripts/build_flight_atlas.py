"""Pack Blender's inspected 3D views into one shared PNG per spacecraft.

No resampling: tile pixels and projected cannon/engine coordinates stay in the
same producer frame. A 256-color RGBA palette keeps the small profile imagery
compact; the manifest records its measured pixel error and exact source hashes.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


def build(source, assets, stem):
    data=json.loads((source/'render-manifest.json').read_text(encoding='utf-8'))
    assert data['schema_version']==2 and not data['blockout']
    frames=data['frames']
    w,h=data['width'],data['height']
    columns=8
    rows=math.ceil(len(frames)/columns)
    sheet=Image.new('RGBA',(w*columns,h*rows))
    for i,frame in enumerate(frames):
        path=source/frame['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==frame['png_sha256']
        image=Image.open(path).convert('RGBA')
        assert image.size==(w,h) and image.getchannel('A').getbbox()
        assert abs(frame['nose_angle_degrees'])<.001
        assert all(0<=u<=1 and 0<=v<=1 for u,v in frame['muzzle_uv']+frame['engine_uv'])
        x,y=(i%columns)*w,(i//columns)*h
        sheet.paste(image,(x,y))
        frame['tile']=[x,y,w,h]
    packed=sheet.quantize(colors=256,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE)
    error=ImageStat.Stat(ImageChops.difference(sheet,packed.convert('RGBA')))
    output=source/(stem+'-atlas.png')
    packed.save(output,optimize=True)
    data.update({'tile_width':w,'tile_height':h,'width':sheet.width,'height':sheet.height,
        'columns':columns,'rows':rows,'palette_colors':256,
        'palette_rms_rgba':error.rms,'png_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'atlas_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    manifest=source/'atlas-manifest.json'
    manifest.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    assets.mkdir(parents=True,exist_ok=True)
    for src,name in [(output,stem+'.png'),(manifest,stem+'.json')]:
        pending=assets/(name+'.tmp')
        pending.write_bytes(src.read_bytes())
        pending.replace(assets/name)
    print(json.dumps({'model':data['model'],'views':len(frames),'size':sheet.size,
                      'bytes':output.stat().st_size,'palette_rms_rgba':error.rms}))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--assets',type=Path,required=True)
    parser.add_argument('--stem',required=True,choices=['aster-ship','vesper-interceptor'])
    args=parser.parse_args()
    build(args.source,args.assets,args.stem)
