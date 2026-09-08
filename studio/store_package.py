"""Build verifiable Google Play listing assets from validated app evidence."""
from __future__ import annotations

import binascii
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import zlib

CATEGORIES = {
    'ART_AND_DESIGN', 'BUSINESS', 'EDUCATION', 'ENTERTAINMENT', 'FINANCE',
    'HEALTH_AND_FITNESS', 'LIFESTYLE', 'MAPS_AND_NAVIGATION', 'MEDICAL',
    'MUSIC_AND_AUDIO', 'NEWS_AND_MAGAZINES', 'PERSONALIZATION', 'PHOTOGRAPHY',
    'PRODUCTIVITY', 'SHOPPING', 'SOCIAL', 'SPORTS', 'TOOLS', 'TRAVEL_AND_LOCAL',
}
SENSITIVE_PERMISSIONS = {
    'android.permission.ACCESS_FINE_LOCATION', 'android.permission.ACCESS_COARSE_LOCATION',
    'android.permission.CAMERA', 'android.permission.RECORD_AUDIO',
    'android.permission.READ_CONTACTS', 'android.permission.WRITE_CONTACTS',
    'android.permission.READ_CALENDAR', 'android.permission.WRITE_CALENDAR',
    'android.permission.READ_SMS', 'android.permission.SEND_SMS',
    'android.permission.READ_PHONE_STATE', 'android.permission.BLUETOOTH_CONNECT',
    'android.permission.POST_NOTIFICATIONS',
}


def validate_store_listing(value: dict) -> dict:
    required = {'title', 'short_description', 'full_description', 'category'}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError('Store listing must contain exactly title, short_description, full_description, category')
    limits = [('title', 1, 30), ('short_description', 10, 80), ('full_description', 80, 4000)]
    for key, low, high in limits:
        text = value.get(key)
        if not isinstance(text, str) or not low <= len(text.strip()) <= high or '\x00' in text:
            raise ValueError(f'Invalid Play listing {key} length')
        value[key] = text.strip()
    if value['category'] not in CATEGORIES:
        raise ValueError('Unsupported Play category')
    return value


def _sentence(text: str, limit: int) -> str:
    clean = re.sub(r'\s+', ' ', text).strip()
    if not clean:
        return ''
    first = re.split(r'(?<=[.!?])\s+', clean)[0]
    if len(first) <= limit:
        return first.rstrip('. ') + '.'
    cut = first[:limit - 1].rsplit(' ', 1)[0].rstrip(' ,;:-')
    return (cut or first[:limit - 1]).rstrip('. ') + '…'


def _category(text: str) -> str:
    lower = text.lower()
    rules = [
        ('HEALTH_AND_FITNESS', ('fitness', 'workout', 'health', 'wellness', 'sleep')),
        ('EDUCATION', ('learn', 'study', 'school', 'quiz', 'education')),
        ('FINANCE', ('budget', 'finance', 'money', 'expense', 'invoice')),
        ('TRAVEL_AND_LOCAL', ('travel', 'trip', 'route', 'itinerary', 'nearby')),
        ('SHOPPING', ('shop', 'shopping', 'cart', 'price', 'product')),
        ('SOCIAL', ('social', 'friends', 'community', 'chat')),
        ('MUSIC_AND_AUDIO', ('music', 'audio', 'podcast', 'sound')),
        ('PHOTOGRAPHY', ('photo', 'camera', 'image', 'gallery')),
        ('SPORTS', ('sport', 'score', 'team', 'match')),
        ('BUSINESS', ('business', 'client', 'crm', 'sales', 'work')),
        ('PRODUCTIVITY', ('task', 'timer', 'focus', 'note', 'habit', 'productivity', 'plan')),
    ]
    for category, words in rules:
        if any(word in lower for word in words):
            return category
    return 'TOOLS'


def listing_from_state(req: dict, state: dict) -> dict:
    title = re.sub(r'[_-]+', ' ', req['app_name']).strip().title()[:30] or 'Mobile App'
    brief = re.sub(r'\s+', ' ', req.get('brief', '')).strip()
    short = _sentence(brief, 80)
    if len(short) < 10:
        short = f'{title} helps you complete the app’s core workflow simply and reliably.'[:80]

    product = state.get('product', {})
    features: list[str] = []
    if isinstance(product, dict):
        for key, value in product.items():
            if key == 'journeys':
                continue
            if isinstance(value, list) and any(token in key.lower() for token in ('accept', 'feature', 'scope', 'goal')):
                for item in value:
                    if isinstance(item, str) and 8 <= len(item.strip()) <= 180:
                        features.append(re.sub(r'\s+', ' ', item).strip())
            if len(features) >= 5:
                break

    intro = _sentence(brief, 360)
    body = [intro or f'{title} is designed around a focused, reliable mobile experience.']
    if features:
        body.append('Key capabilities:\n' + '\n'.join('• ' + item for item in features[:5]))
    journeys = product.get('journeys', []) if isinstance(product, dict) else []
    if isinstance(journeys, list) and journeys:
        body.append(f'Validated around {len(journeys)} critical user journey' + ('s.' if len(journeys) != 1 else '.'))
    body.append('Built for a clear mobile experience with validated interaction, layout, accessibility and runtime checks.')
    full = '\n\n'.join(body)
    if len(full) < 80:
        full += ' The application is designed to keep its primary workflow simple, dependable and easy to understand.'
    full = full[:4000].rstrip()
    return validate_store_listing({
        'title': title,
        'short_description': short,
        'full_description': full,
        'category': _category(brief + ' ' + json.dumps(product, ensure_ascii=False)),
    })


def permissions(root: Path) -> list[str]:
    manifest = root / 'android/app/src/main/AndroidManifest.xml'
    if not manifest.is_file():
        return []
    return sorted(set(re.findall(r'<uses-permission[^>]+android:name=["\']([^"\']+)["\']',
                                 manifest.read_text(errors='replace'))))


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', binascii.crc32(kind + payload) & 0xffffffff)


def encode_rgba(width: int, height: int, pixels: bytes) -> bytes:
    if len(pixels) != width * height * 4:
        raise ValueError('Invalid RGBA payload')
    raw = b''.join(b'\x00' + pixels[y * width * 4:(y + 1) * width * 4] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)) +
            _chunk(b'IDAT', zlib.compress(raw, 9)) + _chunk(b'IEND', b''))


def decode_png(path: Path) -> tuple[int, int, bytes]:
    raw = path.read_bytes()
    if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Screenshot is not PNG')
    pos, width, height, ctype, compressed = 8, 0, 0, None, bytearray()
    while pos + 12 <= len(raw):
        size = struct.unpack('>I', raw[pos:pos + 4])[0]
        kind = raw[pos + 4:pos + 8]
        data = raw[pos + 8:pos + 8 + size]
        pos += 12 + size
        if kind == b'IHDR':
            width, height, depth, ctype, comp, filt, interlace = struct.unpack('>IIBBBBB', data)
            if depth != 8 or ctype not in (2, 6) or comp or filt or interlace:
                raise ValueError('Unsupported PNG format')
        elif kind == b'IDAT':
            compressed.extend(data)
        elif kind == b'IEND':
            break
    channels = 4 if ctype == 6 else 3
    inflated = zlib.decompress(bytes(compressed))
    stride = width * channels
    if len(inflated) != height * (stride + 1):
        raise ValueError('Invalid PNG scanlines')
    previous = bytearray(stride)
    rgba = bytearray()
    index = 0
    for _ in range(height):
        filter_type = inflated[index]
        scan = bytearray(inflated[index + 1:index + 1 + stride])
        index += stride + 1
        for x in range(stride):
            left = scan[x - channels] if x >= channels else 0
            up = previous[x]
            upper_left = previous[x - channels] if x >= channels else 0
            if filter_type == 1:
                scan[x] = (scan[x] + left) & 255
            elif filter_type == 2:
                scan[x] = (scan[x] + up) & 255
            elif filter_type == 3:
                scan[x] = (scan[x] + ((left + up) // 2)) & 255
            elif filter_type == 4:
                p = left + up - upper_left
                pa, pb, pc = abs(p - left), abs(p - up), abs(p - upper_left)
                predictor = left if pa <= pb and pa <= pc else up if pb <= pc else upper_left
                scan[x] = (scan[x] + predictor) & 255
            elif filter_type != 0:
                raise ValueError('Unsupported PNG filter')
        if channels == 4:
            rgba.extend(scan)
        else:
            for x in range(0, len(scan), 3):
                rgba.extend(scan[x:x + 3] + b'\xff')
        previous = scan
    return width, height, bytes(rgba)


def store_screenshot(source: Path, destination: Path) -> dict:
    width, height, pixels = decode_png(source)
    if not 320 <= min(width, height) or max(width, height) > 3840:
        raise ValueError('Screenshot dimensions outside Play limits')
    target_w, target_h = width, height
    if max(width, height) > 2 * min(width, height):
        if height >= width:
            target_w = math.ceil(height / 2)
        else:
            target_h = math.ceil(width / 2)
    if (target_w, target_h) != (width, height):
        bg = pixels[:4]
        canvas = bytearray(bg * (target_w * target_h))
        ox, oy = (target_w - width) // 2, (target_h - height) // 2
        for y in range(height):
            src = y * width * 4
            dst = ((y + oy) * target_w + ox) * 4
            canvas[dst:dst + width * 4] = pixels[src:src + width * 4]
        pixels = bytes(canvas)
    destination.write_bytes(encode_rgba(target_w, target_h, pixels))
    return {'source': source.name, 'file': destination.name, 'width': target_w, 'height': target_h,
            'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()}


def _colors(design: object) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    text = json.dumps(design, ensure_ascii=False)
    found = re.findall(r'#[0-9a-fA-F]{6}\b', text)
    values = []
    for item in found:
        rgb = tuple(int(item[i:i + 2], 16) for i in (1, 3, 5))
        if rgb not in values:
            values.append(rgb)
    return (values + [(24, 32, 48), (90, 100, 246)])[:2]


def _brand_image(width: int, height: int, design: object, feature: bool) -> bytes:
    a, b = _colors(design)
    pixels = bytearray(width * height * 4)
    cx, cy = (width * (0.72 if feature else 0.5), height * 0.5)
    radius = min(width, height) * (0.33 if feature else 0.28)
    for y in range(height):
        t = y / max(1, height - 1)
        base = tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))
        for x in range(width):
            dx, dy = x - cx, y - cy
            dist = (dx * dx + dy * dy) ** 0.5
            glow = max(0.0, 1.0 - dist / radius)
            rgb = tuple(min(255, round(base[i] + glow * (255 - base[i]) * 0.72)) for i in range(3))
            pos = (y * width + x) * 4
            pixels[pos:pos + 4] = bytes((*rgb, 255))
    return encode_rgba(width, height, bytes(pixels))


def build_store_package(root: Path, out: Path, state: dict, listing: dict) -> dict:
    listing = validate_store_listing(dict(listing))
    store = out / 'play-store'
    shots = store / 'screenshots' / 'phone'
    shots.mkdir(parents=True, exist_ok=True)

    candidates = sorted(p for p in out.glob('*--compact-light.png') if p.is_file())
    if (out / 'device-release.png').is_file():
        candidates.insert(0, out / 'device-release.png')
    unique, seen = [], set()
    for source in candidates:
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest not in seen:
            seen.add(digest)
            unique.append(source)
    if len(unique) < 2:
        raise ValueError('At least two distinct validated phone screenshots are required')

    screenshot_evidence = []
    for index, source in enumerate(unique[:8], start=1):
        screenshot_evidence.append(store_screenshot(source, shots / f'{index:02d}.png'))

    icon = store / 'icon-512.png'
    feature = store / 'feature-graphic-1024x500.png'
    icon.write_bytes(_brand_image(512, 512, state.get('design', {}), False))
    feature.write_bytes(_brand_image(1024, 500, state.get('design', {}), True))

    perms = permissions(root)
    manifest = {
        'listing': listing,
        'permissions': perms,
        'sensitive_permissions_requiring_data_safety_review': [p for p in perms if p in SENSITIVE_PERMISSIONS],
        'account_fields_required_at_submission': ['developer_contact_email'],
        'assets': {
            'icon': {'file': icon.name, 'width': 512, 'height': 512,
                     'sha256': hashlib.sha256(icon.read_bytes()).hexdigest()},
            'feature_graphic': {'file': feature.name, 'width': 1024, 'height': 500,
                                'sha256': hashlib.sha256(feature.read_bytes()).hexdigest()},
            'phone_screenshots': screenshot_evidence,
        },
    }
    listing_dir = store / 'listing' / 'en-US'
    listing_dir.mkdir(parents=True, exist_ok=True)
    (listing_dir / 'title.txt').write_text(listing['title'] + '\n')
    (listing_dir / 'short-description.txt').write_text(listing['short_description'] + '\n')
    (listing_dir / 'full-description.txt').write_text(listing['full_description'] + '\n')
    manifest_path = store / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, ensure_ascii=False, indent=2) + '\n')
    return {
        'passed': True,
        'package': 'play-store',
        'listing': listing,
        'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        'screenshot_count': len(screenshot_evidence),
        'permissions': perms,
        'sensitive_permissions': manifest['sensitive_permissions_requiring_data_safety_review'],
        'account_fields_required_at_submission': manifest['account_fields_required_at_submission'],
        'assets': manifest['assets'],
    }
