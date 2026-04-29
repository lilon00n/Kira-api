import os
import tempfile
import io
from base64 import b64encode
from typing import Dict, List, Optional, Tuple

import pikepdf
from pikepdf import Array, Name, Pdf, Stream
from pikepdf.models import PdfImage
from PIL import Image, ImageCms

PROCESS_KEYS = {
    'C': 'cyan',
    'CYAN': 'cyan',
    'PROCESSCYAN': 'cyan',
    'M': 'magenta',
    'MAGENTA': 'magenta',
    'PROCESSMAGENTA': 'magenta',
    'Y': 'yellow',
    'YELLOW': 'yellow',
    'PROCESSYELLOW': 'yellow',
    'K': 'black',
    'BLACK': 'black',
    'PROCESSBLACK': 'black',
}

def _normalize_name(raw_name: str) -> str:
    name = str(raw_name).strip()
    if name.startswith('/'):
        name = name[1:]
    return name.strip()


def _key_for_process(name: str):
    n = _normalize_name(name).upper().replace(' ', '').replace('-', '')
    if 'PANTONE' in n:
        return None
    return PROCESS_KEYS.get(n)


def _is_reserved_spot(name: str) -> bool:
    upper = _normalize_name(name).upper()
    return upper in {'ALL', 'NONE', 'REGISTRATION'}


def _make_zero_tint_transform(pdf: Pdf):
    """Return a FunctionType4 tint transform that outputs CMYK 0,0,0,0."""
    parse_num = lambda s: pikepdf.Object.parse(s.encode() if isinstance(s, str) else s)
    fn_stream = Stream(pdf, b'{ pop 0 0 0 0 }')
    fn_stream['/FunctionType'] = parse_num('4')
    fn_stream['/Domain'] = Array([parse_num('0'), parse_num('1')])
    fn_stream['/Range'] = Array([parse_num('0'), parse_num('1')] * 4)
    return pdf.make_indirect(fn_stream)


def _make_constant_tint_transform(pdf: Pdf, cmyk: tuple):
    """Return a FunctionType4 tint transform that outputs a fixed CMYK color."""
    c, m, y, k = cmyk
    fn_code = f'{{ pop {c:.4f} {m:.4f} {y:.4f} {k:.4f} }}'.encode()
    fn_stream = Stream(pdf, fn_code)
    fn_stream['/FunctionType'] = pikepdf.Object.parse(b'4')
    fn_stream['/Domain'] = Array([pikepdf.Object.parse(b'0'), pikepdf.Object.parse(b'1')])
    fn_stream['/Range'] = Array([pikepdf.Object.parse(b'0'), pikepdf.Object.parse(b'1')] * 4)
    return pdf.make_indirect(fn_stream)


def _spot_name_to_cmyk(name: str) -> tuple:
    """Approximate CMYK display color derived from a spot color name."""
    import re as _re
    n = name.upper().replace(' ', '').replace('-', '').replace('_', '').replace('.', '')

    # Die / cut / crease → thin magenta line
    if any(kw in n for kw in ['DIE', 'CUT', 'TROQUEL', 'CREASE', 'KISS', 'PERF']):
        return (0.0, 1.0, 0.0, 0.0)

    # Varnish / coating → near-transparent
    if any(kw in n for kw in ['VARNISH', 'BARNIZ', 'GLOSS', 'MATTE', 'COATING', 'LACA']):
        return (0.0, 0.0, 0.0, 0.08)

    # White → transparent (invisible on white paper)
    if any(kw in n for kw in ['WHITE', 'BLANCO', 'BLANC', 'WEISS']):
        return (0.0, 0.0, 0.0, 0.0)

    # Metallics
    if any(kw in n for kw in ['SILVER', 'PLATA', 'CHROME']):
        return (0.0, 0.0, 0.0, 0.25)
    if any(kw in n for kw in ['GOLD', 'ORO', 'DORADO']):
        return (0.0, 0.15, 0.70, 0.05)

    # Blues
    if any(kw in n for kw in ['BLUE', 'AZUL', 'AZULINO', 'REFLEX', 'NAVY', 'CELESTE']):
        return (1.0, 0.5, 0.0, 0.0)

    # Greens
    if any(kw in n for kw in ['GREEN', 'VERDE']):
        return (0.7, 0.0, 1.0, 0.0)

    # Reds
    if any(kw in n for kw in ['RED', 'ROJO', 'WARM']):
        return (0.0, 0.9, 0.9, 0.0)

    # Magenta / pink
    if any(kw in n for kw in ['MAGENTA', 'PINK', 'ROSA', 'FUCHSIA']):
        return (0.0, 0.8, 0.1, 0.0)

    # Orange
    if any(kw in n for kw in ['ORANGE', 'NARANJA']):
        return (0.0, 0.45, 0.9, 0.0)

    # Yellow
    if any(kw in n for kw in ['YELLOW', 'AMARILLO', 'GELB']):
        return (0.0, 0.05, 0.95, 0.0)

    # Purple / violet
    if any(kw in n for kw in ['PURPLE', 'VIOLET', 'MORADO', 'PURPURA', 'LILA']):
        return (0.5, 0.9, 0.0, 0.0)

    # Pantone specific overrides, then number range
    _PANTONE_OVERRIDES = {
        386: (0.25, 0.0, 1.0, 0.0),   # chartreuse green
        375: (0.35, 0.0, 1.0, 0.0),
        368: (0.65, 0.0, 1.0, 0.0),
        347: (0.90, 0.0, 0.8, 0.0),
        354: (0.75, 0.0, 1.0, 0.0),
        485: (0.0, 0.90, 0.9, 0.0),   # warm red
        21:  (0.0, 0.45, 0.9, 0.0),   # orange
    }
    m = _re.search(r'(\d{3,4})', n)
    if m:
        num = int(m.group(1))
        if num in _PANTONE_OVERRIDES:
            return _PANTONE_OVERRIDES[num]
        if 100 <= num <= 150:
            return (0.0, 0.05, 0.90, 0.0)    # yellow family
        elif 151 <= num <= 199:
            return (0.0, 0.35, 0.90, 0.0)    # orange-yellow
        elif 200 <= num <= 259:
            return (0.0, 0.80, 0.30, 0.0)    # red-magenta
        elif 260 <= num <= 299:
            return (0.30, 0.90, 0.0, 0.0)    # purple
        elif 300 <= num <= 399:
            return (1.00, 0.40, 0.0, 0.0)    # blue family
        elif 400 <= num <= 499:
            return (0.10, 0.10, 0.20, 0.50)  # gray-brown
        elif 500 <= num <= 599:
            return (0.0, 0.50, 0.10, 0.20)   # dusty pink
        elif 600 <= num <= 699:
            return (0.0, 0.05, 0.50, 0.05)   # light yellow
        elif 700 <= num <= 799:
            return (0.0, 0.60, 0.60, 0.10)   # salmon-red
        elif 800 <= num <= 899:
            return (0.0, 0.60, 0.90, 0.0)    # neon/fluorescent

    # Default: dark neutral (not pure black to be distinguishable from K)
    return (0.0, 0.0, 0.0, 0.75)


def _is_iccbased_rgb(colorspace) -> bool:
    cs = _as_array(colorspace)
    if not cs or len(cs) < 2 or cs[0] != Name.ICCBased:
        return False
    try:
        profile = cs[1]
        n_obj = profile.get('/N')
        n = int(n_obj) if n_obj is not None else 0
        return n == 3
    except Exception:
        return False


def _detect_rgb_content(pdf: Pdf) -> dict:
    """Scan PDF for RGB color content (images and vectors)."""
    rgb_images = 0
    icc_rgb_images = 0
    rgb_vectors = 0
    visited_images: set = set()

    for objid in range(1, len(pdf.objects) + 1):
        try:
            obj = pdf.get_object((objid, 0))
            if not isinstance(obj, Stream):
                continue
            subtype = obj.get('/Subtype', None)
            if subtype != Name.Image:
                continue
            key = (objid, 0)
            if key in visited_images:
                continue
            visited_images.add(key)
            try:
                if bool(obj.get('/ImageMask')) or obj.get('/SMask') is not None:
                    continue
            except Exception:
                pass
            cs = obj.get('/ColorSpace', None)
            if cs == Name.DeviceRGB or cs == Name.DeviceGray:
                rgb_images += 1
            elif _is_iccbased_rgb(cs):
                icc_rgb_images += 1
        except Exception:
            pass

    for page in pdf.pages:
        try:
            for ins in pikepdf.parse_content_stream(page):
                op = str(ins.operator)
                if op in {'rg', 'RG', 'g', 'G'}:
                    rgb_vectors += 1
                    break
        except Exception:
            pass

    return {
        'rgbImages': rgb_images,
        'iccBasedRgb': icc_rgb_images,
        'rgbVectors': rgb_vectors,
    }


def _to_float(value, default=0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _is_pure_black_fill(state) -> bool:
    if not state:
        return False
    kind = state.get('kind')
    if kind == 'gray':
        return _to_float(state.get('g', 1.0), 1.0) <= 0.0001
    if kind == 'cmyk':
        c = _to_float(state.get('c', 0.0), 0.0)
        m = _to_float(state.get('m', 0.0), 0.0)
        y = _to_float(state.get('y', 0.0), 0.0)
        k = _to_float(state.get('k', 0.0), 0.0)
        return c <= 0.0001 and m <= 0.0001 and y <= 0.0001 and k >= 0.999
    return False


def _detect_pure_black_text(pdf: Pdf) -> dict:
    pure_black_text_ops = 0

    for page in pdf.pages:
        fill_state = None
        try:
            for ins in pikepdf.parse_content_stream(page):
                op = str(ins.operator)
                operands = list(ins.operands)

                if op == 'k' and len(operands) >= 4:
                    fill_state = {
                        'kind': 'cmyk',
                        'c': operands[0],
                        'm': operands[1],
                        'y': operands[2],
                        'k': operands[3],
                    }
                elif op == 'g' and len(operands) >= 1:
                    fill_state = {'kind': 'gray', 'g': operands[0]}
                elif op == 'rg' and len(operands) >= 3:
                    fill_state = {
                        'kind': 'rgb',
                        'r': operands[0],
                        'g': operands[1],
                        'b': operands[2],
                    }

                if op in {'Tj', 'TJ', "'", '"'} and _is_pure_black_fill(fill_state):
                    pure_black_text_ops += 1
        except Exception:
            pass

    return {
        'hasPureBlackText': pure_black_text_ops > 0,
        'pureBlackTextOps': pure_black_text_ops,
    }


def _detect_transparency(pdf: Pdf) -> dict:
    image_soft_masks = 0
    image_masks = 0
    alpha_states = 0
    softmask_groups = 0

    for objid in range(1, len(pdf.objects) + 1):
        try:
            obj = pdf.get_object((objid, 0))
            if isinstance(obj, Stream):
                if obj.get('/Subtype', None) == Name.Image:
                    if obj.get('/SMask') is not None:
                        image_soft_masks += 1
                    if obj.get('/Mask') is not None:
                        image_masks += 1
            if isinstance(obj, dict):
                if '/ca' in obj and _to_float(obj.get('/ca'), 1.0) < 0.999:
                    alpha_states += 1
                if '/CA' in obj and _to_float(obj.get('/CA'), 1.0) < 0.999:
                    alpha_states += 1
                smask = obj.get('/SMask', None)
                if smask is not None and str(smask) != '/None':
                    softmask_groups += 1
        except Exception:
            pass

    total = image_soft_masks + image_masks + alpha_states + softmask_groups
    return {
        'hasTransparency': total > 0,
        'imageSoftMasks': image_soft_masks,
        'imageMasks': image_masks,
        'alphaStates': alpha_states,
        'softMaskGroups': softmask_groups,
    }


def _find_separations(pdf: Pdf) -> List[Tuple[str, Array]]:
    found = []
    seen = set()
    for objid in range(1, len(pdf.objects) + 1):
        try:
            obj = pdf.get_object((objid, 0))
            if isinstance(obj, Array) and len(obj) >= 4 and obj[0] == Name.Separation:
                name = _normalize_name(str(obj[1]))
                key = (name, objid)
                if key not in seen:
                    found.append((name, obj))
                    seen.add(key)
        except Exception:
            pass
    return found


def _normalize_cs_name(value) -> str:
    if value is None:
        return ''
    name = str(value)
    if name.startswith('/'):
        name = name[1:]
    return name.strip().upper()


def _as_array(value):
    if isinstance(value, Array):
        return value
    return None


def _is_iccbased_cmyk(colorspace) -> bool:
    cs = _as_array(colorspace)
    if not cs or len(cs) < 2 or cs[0] != Name.ICCBased:
        return False
    try:
        profile = cs[1]
        n_obj = profile.get('/N')
        n = int(n_obj) if n_obj is not None else 0
        return n == 4
    except Exception:
        return False


def _device_n_info(colorspace):
    cs = _as_array(colorspace)
    if not cs or len(cs) < 4 or cs[0] != Name.DeviceN:
        return None
    names = []
    try:
        comp_array = cs[1]
        for i in range(len(comp_array)):
            comp = comp_array[i]
            names.append(_normalize_name(str(comp)))
        alt = cs[2]
        alt_name = _normalize_cs_name(alt)
        is_alt_cmyk = alt == Name.DeviceCMYK or alt_name == 'DEVICECMYK'
        if isinstance(alt, Array):
            is_alt_cmyk = _normalize_cs_name(alt[0]) == 'DEVICECMYK'
        return {
            'names': names,
            'is_alt_cmyk': is_alt_cmyk,
        }
    except Exception:
        return None


def _resolve_cs_ref(resources, token):
    for res in resources:
        try:
            if not res or '/ColorSpace' not in res:
                continue
            color_spaces = res['/ColorSpace']
            if token in color_spaces:
                return color_spaces[token]
        except Exception:
            pass
    return None


def _is_numeric_operand(value) -> bool:
    try:
        float(value)
        return True
    except Exception:
        return False


def _is_cmyk_color_space(cs_obj) -> bool:
    if cs_obj is None:
        return False
    if cs_obj == Name.DeviceCMYK:
        return True
    if _is_iccbased_cmyk(cs_obj):
        return True
    return False


def _classify_color_space(resources, operand):
    if operand == Name.DeviceCMYK:
        return {'kind': 'devicecmyk'}
    if operand == Name.DeviceRGB:
        return {'kind': 'devicergb'}
    if operand == Name.DeviceGray:
        return {'kind': 'devicegray'}

    resolved = _resolve_cs_ref(resources, operand)
    if resolved is None:
        resolved = operand

    if _is_cmyk_color_space(resolved):
        return {'kind': 'devicecmyk'}
    if resolved == Name.DeviceRGB:
        return {'kind': 'devicergb'}
    if resolved == Name.DeviceGray:
        return {'kind': 'devicegray'}
    if _is_iccbased_rgb(resolved):
        return {'kind': 'iccbasedrgb'}

    dn = _device_n_info(resolved)
    if dn and dn['is_alt_cmyk']:
        return {'kind': 'devicen', 'names': dn['names']}

    return {'kind': 'unknown'}


def _object_key(obj):
    try:
        og = obj.objgen
        if og and og[0] is not None:
            return ('obj', int(og[0]), int(og[1]))
    except Exception:
        pass
    return ('id', id(obj))


def _prepend_resources(resources_chain, obj):
    try:
        local = obj.get('/Resources', None)
        if local is None:
            return resources_chain
        return [local] + resources_chain
    except Exception:
        return resources_chain


def _iter_resource_entries(resources, key_name):
    if not resources:
        return []
    try:
        section = resources.get(key_name, None)
        if not section:
            return []
        out = []
        for k in section:
            try:
                out.append((k, section[k]))
            except Exception:
                pass
        return out
    except Exception:
        return []


def _resolve_image_colorspace(cs, resources_chain):
    if cs is None:
        return None
    if cs == Name.DeviceCMYK:
        return cs
    if isinstance(cs, Array):
        return cs
    if isinstance(cs, Name):
        ref = _resolve_cs_ref(resources_chain, cs)
        return ref if ref is not None else cs
    return cs


def _patch_operands_cmyk(operands, channels: Dict[str, bool]) -> bool:
    if len(operands) < 4:
        return False
    if not all(_is_numeric_operand(v) for v in operands[:4]):
        return False

    changed = False
    if not channels.get('cyan', True):
        operands[0] = 0
        changed = True
    if not channels.get('magenta', True):
        operands[1] = 0
        changed = True
    if not channels.get('yellow', True):
        operands[2] = 0
        changed = True
    if not channels.get('black', True):
        operands[3] = 0
        changed = True
    return changed


def _patch_operands_devicen(operands, comp_names: List[str], channels: Dict[str, bool]) -> bool:
    if len(operands) < len(comp_names):
        return False
    values = operands[:len(comp_names)]
    if not all(_is_numeric_operand(v) for v in values):
        return False

    changed = False
    for idx, cname in enumerate(comp_names):
        pkey = _key_for_process(cname)
        if pkey and not channels.get(pkey, True):
            operands[idx] = 0
            changed = True
    return changed


def _rgb_to_cmyk_components(r: float, g: float, b: float) -> Tuple[float, float, float, float]:
    r = max(0.0, min(1.0, r))
    g = max(0.0, min(1.0, g))
    b = max(0.0, min(1.0, b))
    k = 1.0 - max(r, g, b)
    if k >= 0.999999:
        return 0.0, 0.0, 0.0, 1.0
    den = 1.0 - k
    c = (1.0 - r - k) / den
    m = (1.0 - g - k) / den
    y = (1.0 - b - k) / den
    return (
        max(0.0, min(1.0, c)),
        max(0.0, min(1.0, m)),
        max(0.0, min(1.0, y)),
        max(0.0, min(1.0, k)),
    )


def _convert_rgb_operands_to_cmyk(operands) -> Optional[List[float]]:
    if len(operands) < 3:
        return None
    if not all(_is_numeric_operand(v) for v in operands[:3]):
        return None
    r = _to_float(operands[0], 0.0)
    g = _to_float(operands[1], 0.0)
    b = _to_float(operands[2], 0.0)
    c, m, y, k = _rgb_to_cmyk_components(r, g, b)
    return [c, m, y, k]


def _is_resolved_rgb_colorspace(cs_obj) -> bool:
    return cs_obj == Name.DeviceRGB or _is_iccbased_rgb(cs_obj)


def _convert_rgb_image_to_cmyk(image_stream: Stream, resources_chain, icc_profile_path: Optional[str]):
    cs = image_stream.get('/ColorSpace', None)
    resolved_cs = _resolve_image_colorspace(cs, resources_chain)
    if not _is_resolved_rgb_colorspace(resolved_cs):
        return {'converted': False, 'reason': 'not-rgb'}

    bpc_obj = image_stream.get('/BitsPerComponent')
    bpc = int(bpc_obj) if bpc_obj is not None else 8
    if bpc != 8:
        return {'converted': False, 'reason': 'unsupported-bpc'}

    try:
        if bool(image_stream.get('/ImageMask')):
            return {'converted': False, 'reason': 'mask-image'}
    except Exception:
        pass

    try:
        if image_stream.get('/SMask') is not None or image_stream.get('/Mask') is not None:
            return {'converted': False, 'reason': 'image-mask'}
    except Exception:
        pass

    width_obj = image_stream.get('/Width')
    height_obj = image_stream.get('/Height')
    if width_obj is None or height_obj is None:
        return {'converted': False, 'reason': 'missing-size'}

    width = int(width_obj)
    height = int(height_obj)
    if width <= 0 or height <= 0:
        return {'converted': False, 'reason': 'invalid-size'}

    try:
        pil_img = PdfImage(image_stream).as_pil_image()
        if pil_img.mode not in ('RGB',):
            pil_img = pil_img.convert('RGB')
        width, height = pil_img.size
        raw = pil_img.tobytes()
    except Exception:
        return {'converted': False, 'reason': 'unfilterable-stream'}

    rgb = Image.frombytes('RGB', (width, height), raw)
    cmyk = None

    if icc_profile_path and os.path.isfile(icc_profile_path):
        try:
            srgb = ImageCms.createProfile('sRGB')
            dst = ImageCms.getOpenProfile(icc_profile_path)
            transform = ImageCms.buildTransformFromOpenProfiles(srgb, dst, 'RGB', 'CMYK')
            cmyk = ImageCms.applyTransform(rgb, transform)
        except Exception:
            cmyk = None

    if cmyk is None:
        cmyk = rgb.convert('CMYK')

    out_bytes = cmyk.tobytes()
    image_stream.write(out_bytes, filter=Name.FlateDecode)
    image_stream['/ColorSpace'] = Name.DeviceCMYK
    image_stream['/BitsPerComponent'] = 8
    if '/DecodeParms' in image_stream:
        del image_stream['/DecodeParms']
    if '/SMask' in image_stream:
        del image_stream['/SMask']

    return {
        'converted': True,
        'width': width,
        'height': height,
        'bytes': len(out_bytes),
    }


def _convert_rgb_vectors_in_container(pdf: Pdf, container, resources_chain) -> int:
    converted = 0
    patched_any = False
    patched_instructions = []

    nonstroke_cs = {'kind': 'unknown'}
    stroke_cs = {'kind': 'unknown'}

    try:
        instructions = list(pikepdf.parse_content_stream(container))
    except Exception:
        return 0

    for ins in instructions:
        op = str(ins.operator)
        operands = list(ins.operands)

        if op == 'cs' and operands:
            nonstroke_cs = _classify_color_space(resources_chain, operands[0])
        elif op == 'CS' and operands:
            stroke_cs = _classify_color_space(resources_chain, operands[0])
        elif op == 'rg':
            cmyk = _convert_rgb_operands_to_cmyk(operands)
            if cmyk is not None:
                operands = cmyk
                op = 'k'
                patched_any = True
                converted += 1
        elif op == 'RG':
            cmyk = _convert_rgb_operands_to_cmyk(operands)
            if cmyk is not None:
                operands = cmyk
                op = 'K'
                patched_any = True
                converted += 1
        elif op in {'sc', 'SC', 'scn', 'SCN'}:
            cs_state = nonstroke_cs if op in {'sc', 'scn'} else stroke_cs
            if cs_state.get('kind') in {'devicergb', 'iccbasedrgb'}:
                cmyk = _convert_rgb_operands_to_cmyk(operands)
                if cmyk is not None:
                    operands = cmyk
                    op = 'sc' if op in {'sc', 'scn'} else 'SC'
                    patched_any = True
                    converted += 1

        patched_instructions.append(
            pikepdf.ContentStreamInstruction(operands, pikepdf.Operator(op))
        )

    if patched_any:
        raw = pikepdf.unparse_content_stream(patched_instructions)
        if isinstance(container, Stream):
            container.write(raw)
        else:
            container.Contents = Stream(pdf, raw)

    return converted


def _convert_rgb_recursively(pdf: Pdf, root_container, icc_profile_path: Optional[str]) -> Dict[str, int]:
    debug = {
        'rgbVectorsConverted': 0,
        'rgbImagesConverted': 0,
        'rgbImagesSkipped': 0,
    }

    visited_containers = set()
    visited_images = set()

    def walk(container, resources_chain):
        ckey = _object_key(container if isinstance(container, Stream) else container.obj)
        if ckey in visited_containers:
            return
        visited_containers.add(ckey)

        chain = _prepend_resources(resources_chain, container)
        debug['rgbVectorsConverted'] += _convert_rgb_vectors_in_container(pdf, container, chain)

        head = chain[0] if chain else None
        for _, xobj in _iter_resource_entries(head, '/XObject'):
            if not isinstance(xobj, Stream):
                continue
            subtype = xobj.get('/Subtype', None)
            if subtype == Name.Form:
                walk(xobj, chain)
            elif subtype == Name.Image:
                ikey = _object_key(xobj)
                if ikey in visited_images:
                    continue
                visited_images.add(ikey)
                info = _convert_rgb_image_to_cmyk(xobj, chain, icc_profile_path)
                if info.get('converted'):
                    debug['rgbImagesConverted'] += 1
                else:
                    debug['rgbImagesSkipped'] += 1

        for _, patt in _iter_resource_entries(head, '/Pattern'):
            if isinstance(patt, Stream):
                walk(patt, chain)

        for _, gs in _iter_resource_entries(head, '/ExtGState'):
            try:
                smask = gs.get('/SMask', None)
                if smask and isinstance(smask, dict):
                    g = smask.get('/G', None)
                    if isinstance(g, Stream):
                        walk(g, chain)
            except Exception:
                pass

    walk(root_container, [])
    return debug


def _patch_page_vectors(pdf: Pdf, page, channels: Dict[str, bool]):
    vectors_cmyk = 0
    patched_any = False
    patched_instructions = []

    resources = _prepend_resources([], page)
    nonstroke_cs = {'kind': 'unknown'}
    stroke_cs = {'kind': 'unknown'}

    for ins in pikepdf.parse_content_stream(page):
        op = str(ins.operator)
        operands = list(ins.operands)
        patched_here = False

        if op == 'cs' and operands:
            nonstroke_cs = _classify_color_space(resources, operands[0])
        elif op == 'CS' and operands:
            stroke_cs = _classify_color_space(resources, operands[0])
        elif op in {'k', 'K'}:
            if _patch_operands_cmyk(operands, channels):
                patched_here = True
            vectors_cmyk += 1
        elif op in {'sc', 'SC'}:
            cs_state = nonstroke_cs if op == 'sc' else stroke_cs
            if cs_state.get('kind') == 'devicecmyk' and len(operands) >= 4:
                if _patch_operands_cmyk(operands, channels):
                    patched_here = True
                vectors_cmyk += 1
        elif op in {'scn', 'SCN'}:
            cs_state = nonstroke_cs if op == 'scn' else stroke_cs
            if cs_state.get('kind') == 'devicecmyk' and len(operands) >= 4:
                if _patch_operands_cmyk(operands, channels):
                    patched_here = True
                vectors_cmyk += 1
            elif cs_state.get('kind') == 'devicen':
                comp_names = cs_state.get('names', [])
                if not isinstance(comp_names, list):
                    comp_names = []
                if comp_names and len(operands) >= len(comp_names):
                    if _patch_operands_devicen(operands, comp_names, channels):
                        patched_here = True
                    vectors_cmyk += 1

        if patched_here:
            patched_any = True

        patched_instructions.append(pikepdf.ContentStreamInstruction(operands, ins.operator))

    if patched_any:
        page.Contents = Stream(pdf, pikepdf.unparse_content_stream(patched_instructions))

    return vectors_cmyk


def _patch_container_vectors(pdf: Pdf, container, resources_chain, channels: Dict[str, bool]):
    vectors_cmyk = 0
    patched_any = False
    patched_instructions = []

    nonstroke_cs = {'kind': 'unknown'}
    stroke_cs = {'kind': 'unknown'}

    try:
        instructions = list(pikepdf.parse_content_stream(container))
    except Exception:
        return 0

    for ins in instructions:
        op = str(ins.operator)
        operands = list(ins.operands)
        patched_here = False

        if op == 'cs' and operands:
            nonstroke_cs = _classify_color_space(resources_chain, operands[0])
        elif op == 'CS' and operands:
            stroke_cs = _classify_color_space(resources_chain, operands[0])
        elif op in {'k', 'K'}:
            if _patch_operands_cmyk(operands, channels):
                patched_here = True
            vectors_cmyk += 1
        elif op in {'sc', 'SC'}:
            cs_state = nonstroke_cs if op == 'sc' else stroke_cs
            if cs_state.get('kind') == 'devicecmyk' and len(operands) >= 4:
                if _patch_operands_cmyk(operands, channels):
                    patched_here = True
                vectors_cmyk += 1
        elif op in {'scn', 'SCN'}:
            cs_state = nonstroke_cs if op == 'scn' else stroke_cs
            if cs_state.get('kind') == 'devicecmyk' and len(operands) >= 4:
                if _patch_operands_cmyk(operands, channels):
                    patched_here = True
                vectors_cmyk += 1
            elif cs_state.get('kind') == 'devicen':
                comp_names = cs_state.get('names', [])
                if not isinstance(comp_names, list):
                    comp_names = []
                if comp_names and len(operands) >= len(comp_names):
                    if _patch_operands_devicen(operands, comp_names, channels):
                        patched_here = True
                    vectors_cmyk += 1

        if patched_here:
            patched_any = True

        patched_instructions.append(pikepdf.ContentStreamInstruction(operands, ins.operator))

    if patched_any:
        raw = pikepdf.unparse_content_stream(patched_instructions)
        if isinstance(container, Stream):
            container.write(raw)
        else:
            container.Contents = Stream(pdf, raw)

    return vectors_cmyk


def _inspect_or_patch_image(image_stream: Stream, resources_chain, channels: Dict[str, bool], apply_patch: bool):
    def _to_xref(stream_obj):
        try:
            og = stream_obj.objgen
            if og and og[0] is not None:
                return int(og[0])
        except Exception:
            pass
        return None

    def _colorspace_debug_label(cs_obj) -> str:
        try:
            if cs_obj is None:
                return 'Unknown'
            if cs_obj == Name.DeviceCMYK:
                return 'DeviceCMYK'
            if _is_iccbased_cmyk(cs_obj):
                return 'ICCBased(CMYK)'
            dn_info = _device_n_info(cs_obj)
            if dn_info and dn_info.get('is_alt_cmyk'):
                comps = ','.join(dn_info.get('names', []))
                return f'DeviceN[{comps}]'
            return str(cs_obj)
        except Exception:
            return 'Unknown'

    debug = {
        'deviceCmykImages': 0,
        'iccBasedCmyk': 0,
        'rgbImages': 0,
        'iccBasedRgb': 0,
        'imagePatchedByBytes': 0,
        'imagePatchedByDecodeFallback': 0,
        'imageUnfilterable': 0,
        'images': [],
    }

    image_debug = {
        'xref': _to_xref(image_stream),
        'colorspace': 'Unknown',
        'mask': False,
        'decoded': False,
        'patched': False,
        'fallbackUsed': False,
    }

    # Image masks and stencil-like masks are binary alpha data; touching channel bytes breaks rendering.
    try:
        image_mask = image_stream.get('/ImageMask')
        if bool(image_mask):
            image_debug['mask'] = True
            debug['images'].append(image_debug)
            return debug
    except Exception:
        pass
    try:
        if image_stream.get('/SMask') is not None or image_stream.get('/Mask') is not None:
            image_debug['mask'] = True
            debug['images'].append(image_debug)
            return debug
    except Exception:
        pass

    cs = image_stream.get('/ColorSpace', None)
    resolved_cs = _resolve_image_colorspace(cs, resources_chain)
    image_debug['colorspace'] = _colorspace_debug_label(resolved_cs)

    bpc_obj = image_stream.get('/BitsPerComponent')
    bpc = int(bpc_obj) if bpc_obj is not None else 8
    if bpc != 8:
        debug['images'].append(image_debug)
        return debug

    def _as_float(v, default):
        try:
            return float(v)
        except Exception:
            return default

    def _build_decode_pairs(component_names: List[str], decode_obj):
        n = len(component_names)
        base = []
        if isinstance(decode_obj, Array) and len(decode_obj) >= 2 * n:
            for i in range(2 * n):
                base.append(_as_float(decode_obj[i], 0.0 if i % 2 == 0 else 1.0))
        else:
            base = [0.0, 1.0] * n

        for idx, cname in enumerate(component_names):
            pkey = _key_for_process(cname)
            if pkey and not channels.get(pkey, True):
                # Force component to constant 0 (no process ink), independently of stream filter.
                base[2 * idx] = 0.0
                base[2 * idx + 1] = 0.0
        return Array(base)

    def _has_codestream_filter() -> bool:
        try:
            filt = image_stream.get('/Filter', None)
        except Exception:
            return False

        if filt is None:
            return False

        if isinstance(filt, Name):
            filters = [filt]
        elif isinstance(filt, Array):
            filters = []
            for i in range(len(filt)):
                f = filt[i]
                if isinstance(f, Name):
                    filters.append(f)
        else:
            return False

        codestream_filters = {
            Name.DCTDecode,
            Name.JPXDecode,
            Name.JBIG2Decode,
        }
        return any(f in codestream_filters for f in filters)

    def _patch_stream_bytes(patch_fn):
        try:
            raw = PdfImage(image_stream).read_bytes()
            patched = patch_fn(raw)
            if patched != raw:
                image_stream.write(patched, filter=Name.FlateDecode)
                if '/DecodeParms' in image_stream:
                    del image_stream['/DecodeParms']
                return True, True
            return True, False
        except Exception:
            return False, False

    if resolved_cs == Name.DeviceCMYK:
        debug['deviceCmykImages'] += 1
        if apply_patch:
            decoded, patched = _patch_stream_bytes(lambda raw: _patch_image_cmyk(raw, channels))
            image_debug['decoded'] = decoded
            if patched:
                debug['imagePatchedByBytes'] += 1
                image_debug['patched'] = True
            elif not decoded and not _has_codestream_filter():
                debug['imageUnfilterable'] += 1
                image_stream['/Decode'] = _build_decode_pairs(
                    ['C', 'M', 'Y', 'K'],
                    image_stream.get('/Decode', None),
                )
                debug['imagePatchedByDecodeFallback'] += 1
                image_debug['patched'] = True
                image_debug['fallbackUsed'] = True
            elif not decoded:
                debug['imageUnfilterable'] += 1
    elif _is_iccbased_cmyk(resolved_cs):
        debug['iccBasedCmyk'] += 1
        if apply_patch:
            decoded, patched = _patch_stream_bytes(lambda raw: _patch_image_cmyk(raw, channels))
            image_debug['decoded'] = decoded
            if patched:
                debug['imagePatchedByBytes'] += 1
                image_debug['patched'] = True
            elif not decoded and not _has_codestream_filter():
                debug['imageUnfilterable'] += 1
                image_stream['/Decode'] = _build_decode_pairs(
                    ['C', 'M', 'Y', 'K'],
                    image_stream.get('/Decode', None),
                )
                debug['imagePatchedByDecodeFallback'] += 1
                image_debug['patched'] = True
                image_debug['fallbackUsed'] = True
            elif not decoded:
                debug['imageUnfilterable'] += 1
    else:
        dn = _device_n_info(resolved_cs)
        if dn and dn['is_alt_cmyk'] and apply_patch:
            decoded, patched = _patch_stream_bytes(lambda raw: _patch_image_devicen(raw, dn['names'], channels))
            image_debug['decoded'] = decoded
            if patched:
                debug['imagePatchedByBytes'] += 1
                image_debug['patched'] = True
            elif not decoded and not _has_codestream_filter():
                debug['imageUnfilterable'] += 1
                image_stream['/Decode'] = _build_decode_pairs(
                    dn['names'],
                    image_stream.get('/Decode', None),
                )
                debug['imagePatchedByDecodeFallback'] += 1
                image_debug['patched'] = True
                image_debug['fallbackUsed'] = True
            elif not decoded:
                debug['imageUnfilterable'] += 1
        elif resolved_cs == Name.DeviceRGB or resolved_cs == Name.DeviceGray:
            debug['rgbImages'] += 1
        elif _is_iccbased_rgb(resolved_cs):
            debug['iccBasedRgb'] += 1

    debug['images'].append(image_debug)

    return debug


def _walk_nested_resources(pdf: Pdf, root_container, channels: Dict[str, bool], apply_patch: bool):
    debug = {
        'vectorsCmyk': 0,
        'deviceCmykImages': 0,
        'iccBasedCmyk': 0,
        'rgbImages': 0,
        'iccBasedRgb': 0,
        'imagePatchedByBytes': 0,
        'imagePatchedByDecodeFallback': 0,
        'imageUnfilterable': 0,
        'images': [],
    }

    visited_containers = set()
    visited_images = set()

    def walk(container, resources_chain):
        ckey = _object_key(container if isinstance(container, Stream) else container.obj)
        if ckey in visited_containers:
            return
        visited_containers.add(ckey)

        chain = _prepend_resources(resources_chain, container)
        debug['vectorsCmyk'] += _patch_container_vectors(pdf, container, chain, channels)

        head = chain[0] if chain else None

        # XObjects: recurse into Form streams and inspect nested Image streams.
        for _, xobj in _iter_resource_entries(head, '/XObject'):
            if not isinstance(xobj, Stream):
                continue
            subtype = xobj.get('/Subtype', None)
            if subtype == Name.Form:
                walk(xobj, chain)
            elif subtype == Name.Image:
                ikey = _object_key(xobj)
                if ikey in visited_images:
                    continue
                visited_images.add(ikey)
                im_debug = _inspect_or_patch_image(xobj, chain, channels, apply_patch)
                debug['deviceCmykImages'] += im_debug['deviceCmykImages']
                debug['iccBasedCmyk'] += im_debug['iccBasedCmyk']
                debug['rgbImages'] += im_debug.get('rgbImages', 0)
                debug['iccBasedRgb'] += im_debug.get('iccBasedRgb', 0)
                debug['imagePatchedByBytes'] += im_debug['imagePatchedByBytes']
                debug['imagePatchedByDecodeFallback'] += im_debug['imagePatchedByDecodeFallback']
                debug['imageUnfilterable'] += im_debug['imageUnfilterable']
                debug['images'].extend(im_debug.get('images', []))

        # Pattern resources can embed paint streams.
        for _, patt in _iter_resource_entries(head, '/Pattern'):
            if isinstance(patt, Stream):
                walk(patt, chain)

        # Transparency / soft masks via ExtGState -> /SMask -> /G Form.
        for _, gs in _iter_resource_entries(head, '/ExtGState'):
            try:
                smask = gs.get('/SMask', None)
                if smask and isinstance(smask, dict):
                    g = smask.get('/G', None)
                    if isinstance(g, Stream):
                        walk(g, chain)
            except Exception:
                pass

    walk(root_container, [])
    return debug


def _has_device_cmyk(pdf: Pdf) -> bool:
    for objid in range(1, len(pdf.objects) + 1):
        try:
            obj = pdf.get_object((objid, 0))
            if isinstance(obj, Stream):
                cs = obj.get('/ColorSpace', None)
                if cs == Name.DeviceCMYK:
                    return True
                if _is_iccbased_cmyk(cs):
                    return True
                if isinstance(cs, Array) and len(cs) and cs[0] == Name.DeviceN:
                    dn = _device_n_info(cs)
                    if dn and dn['is_alt_cmyk']:
                        return True
        except Exception:
            pass
    return False


def _collect_debug_info(pdf: Pdf):
    vectors_cmyk = 0
    device_cmyk_images = 0
    iccbased_cmyk = 0
    rgb_images = 0
    icc_rgb_images = 0
    image_patched_bytes = 0
    image_patched_decode = 0
    image_unfilterable = 0
    images = []

    for page in pdf.pages:
        page_debug = _walk_nested_resources(
            pdf,
            page,
            {'cyan': True, 'magenta': True, 'yellow': True, 'black': True},
            apply_patch=False,
        )
        vectors_cmyk += page_debug['vectorsCmyk']
        device_cmyk_images += page_debug['deviceCmykImages']
        iccbased_cmyk += page_debug['iccBasedCmyk']
        rgb_images += page_debug.get('rgbImages', 0)
        icc_rgb_images += page_debug.get('iccBasedRgb', 0)
        image_patched_bytes += page_debug['imagePatchedByBytes']
        image_patched_decode += page_debug['imagePatchedByDecodeFallback']
        image_unfilterable += page_debug['imageUnfilterable']
        images.extend(page_debug.get('images', []))

    return {
        'vectorsCmyk': vectors_cmyk,
        'deviceCmykImages': device_cmyk_images,
        'iccBasedCmyk': iccbased_cmyk,
        'rgbImages': rgb_images,
        'iccBasedRgb': icc_rgb_images,
        'imagePatchedByBytes': image_patched_bytes,
        'imagePatchedByDecodeFallback': image_patched_decode,
        'imageUnfilterable': image_unfilterable,
        'images': images,
    }


def extract_inks(pdf_path: str) -> Dict[str, object]:
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f'File not found: {pdf_path}')

    spots = []
    spots_set = set()

    with Pdf.open(pdf_path) as pdf:
        has_cmyk = _has_device_cmyk(pdf)
        debug = _collect_debug_info(pdf)
        separations = _find_separations(pdf)
        rgb_content = _detect_rgb_content(pdf)
        pure_black_text = _detect_pure_black_text(pdf)
        transparency = _detect_transparency(pdf)

        for sep_name, sep_array in separations:
            process_key = _key_for_process(sep_name)
            if process_key:
                has_cmyk = True
                continue
            if _is_reserved_spot(sep_name):
                continue
            if sep_name not in spots_set:
                spots.append(sep_name)
                spots_set.add(sep_name)

    has_spots = len(spots) > 0
    has_rgb = (
        rgb_content['rgbImages']
        + rgb_content['iccBasedRgb']
        + rgb_content['rgbVectors']
    ) > 0

    if has_spots and not has_cmyk and not has_rgb:
        color_mode = 'SPOT ONLY'
    elif has_rgb and not has_cmyk:
        color_mode = 'RGB'
    elif has_cmyk and not has_rgb:
        color_mode = 'CMYK'
    else:
        color_mode = 'MIXED'

    rgb_warning = (
        'This PDF uses RGB content. CMYK separations are simulated only.'
        if has_rgb else None
    )

    return {
        'process': ['C', 'M', 'Y', 'K'],
        'processDetected': has_cmyk,
        'spots': spots,
        'colorMode': color_mode,
        'rgbContent': rgb_content,
        'pureBlackText': pure_black_text,
        'transparency': transparency,
        'rgbWarning': rgb_warning,
        'preflight': {
            'rgbImages': rgb_content['rgbImages'],
            'iccBasedRgb': rgb_content['iccBasedRgb'],
            'rgbVectors': rgb_content['rgbVectors'],
            'cmykObjects': {
                'vectors': debug.get('vectorsCmyk', 0),
                'deviceCmykImages': debug.get('deviceCmykImages', 0),
                'iccBasedCmyk': debug.get('iccBasedCmyk', 0),
                'total': (
                    debug.get('vectorsCmyk', 0)
                    + debug.get('deviceCmykImages', 0)
                    + debug.get('iccBasedCmyk', 0)
                ),
            },
            'spotColors': spots,
            'pureBlackText': pure_black_text,
            'transparency': transparency,
            'hasRgbContent': has_rgb,
        },
        'debug': {
            **debug,
            'spots': spots,
        },
    }


def _patch_image_cmyk(raw: bytes, channels: Dict[str, bool]) -> bytes:
    c_on = channels.get('cyan', True)
    m_on = channels.get('magenta', True)
    y_on = channels.get('yellow', True)
    k_on = channels.get('black', True)

    buf = bytearray(raw)
    for i in range(0, len(buf) - 3, 4):
        if not c_on:
            buf[i] = 0
        if not m_on:
            buf[i + 1] = 0
        if not y_on:
            buf[i + 2] = 0
        if not k_on:
            buf[i + 3] = 0
    return bytes(buf)


def _patch_image_devicen(raw: bytes, component_names: List[str], channels: Dict[str, bool]) -> bytes:
    n = len(component_names)
    if n <= 0:
        return raw

    process_index = {}
    for idx, cname in enumerate(component_names):
        pkey = _key_for_process(cname)
        if pkey:
            process_index[idx] = pkey

    if not process_index:
        return raw

    buf = bytearray(raw)
    for i in range(0, len(buf) - (n - 1), n):
        for idx, pkey in process_index.items():
            if not channels.get(pkey, True):
                buf[i + idx] = 0
    return bytes(buf)


def render_channels(pdf_path: str, channels: Dict[str, bool], spots: Optional[Dict[str, bool]] = None) -> Dict[str, object]:
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f'File not found: {pdf_path}')

    if spots is None:
        spots = {}

    temp_fd, temp_path = tempfile.mkstemp(prefix='nala_inks_', suffix='.pdf')
    os.close(temp_fd)

    with Pdf.open(pdf_path) as pdf:
        zero_ref = _make_zero_tint_transform(pdf)
        debug = {
            'vectorsCmyk': 0,
            'deviceCmykImages': 0,
            'iccBasedCmyk': 0,
            'imagePatchedByBytes': 0,
            'imagePatchedByDecodeFallback': 0,
            'imageUnfilterable': 0,
            'spots': [],
            'images': [],
        }

        # 1) Separation colorspaces: process + spots
        for sep_name, sep_array in _find_separations(pdf):
            process_key = _key_for_process(sep_name)
            if process_key:
                if not channels.get(process_key, True):
                    sep_array[3] = zero_ref
                continue

            # Spot channel toggles: disabled → zero, enabled → color approximation for preview
            if sep_name in spots and not bool(spots[sep_name]):
                sep_array[3] = zero_ref
            else:
                # Replace tint transform with a color-name-derived CMYK approximation so the
                # spot renders with a recognisable preview color instead of the original
                # (often K=1 black) tint transform.
                cmyk = _spot_name_to_cmyk(sep_name)
                sep_array[3] = _make_constant_tint_transform(pdf, cmyk)

            debug['spots'].append(sep_name)

        # 2) Recursively patch vectors/images from page resources into nested XObjects/patterns/groups.
        for page in pdf.pages:
            page_debug = _walk_nested_resources(pdf, page, channels, apply_patch=True)
            debug['vectorsCmyk'] += page_debug['vectorsCmyk']
            debug['deviceCmykImages'] += page_debug['deviceCmykImages']
            debug['iccBasedCmyk'] += page_debug['iccBasedCmyk']
            debug['imagePatchedByBytes'] += page_debug['imagePatchedByBytes']
            debug['imagePatchedByDecodeFallback'] += page_debug['imagePatchedByDecodeFallback']
            debug['imageUnfilterable'] += page_debug['imageUnfilterable']
            debug['images'].extend(page_debug.get('images', []))

        pdf.save(temp_path)

    with open(temp_path, 'rb') as f:
        payload = f.read()

    os.remove(temp_path)

    return {
        'ok': True,
        'pdfBase64': b64encode(payload).decode('ascii'),
        'debug': debug,
    }


def convert_rgb_to_cmyk_selective(pdf_path: str, outfile: str, icc_profile: Optional[str] = None) -> Dict[str, object]:
    """
    Object-based selective conversion.
    Keep unchanged: DeviceN/spot, CMYK objects, and existing pure black vectors/text.
    Convert only: DeviceRGB and ICCBased RGB vectors/images.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f'File not found: {pdf_path}')

    out_dir = os.path.dirname(outfile)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    conversion_debug = {
        'rgbVectorsConverted': 0,
        'rgbImagesConverted': 0,
        'rgbImagesSkipped': 0,
    }

    with Pdf.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_debug = _convert_rgb_recursively(pdf, page, icc_profile)
            conversion_debug['rgbVectorsConverted'] += page_debug.get('rgbVectorsConverted', 0)
            conversion_debug['rgbImagesConverted'] += page_debug.get('rgbImagesConverted', 0)
            conversion_debug['rgbImagesSkipped'] += page_debug.get('rgbImagesSkipped', 0)

        pdf.save(outfile)

    post = extract_inks(outfile)
    return {
        'outfile': outfile,
        'converted': conversion_debug,
        'postflight': post,
    }
