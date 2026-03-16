"""
Extract wardrobe items from an image using Gemini.
Returns a list of { name, category, description, color }.
"""
import base64
import json
import re

import requests
from django.conf import settings

VALID_CATEGORIES = {'top', 'bottom', 'outerwear', 'shoes', 'accessory', 'dress', 'other'}
DEFAULT_GEMINI_MODELS = [
    'gemini-2.0-flash',
    'gemini-2.0-flash-001',
    'gemini-flash-latest',
]


class ImageExtractionError(Exception):
    """Raised when Gemini image extraction fails with a debuggable reason."""


def _extract_json_array(text: str):
    """Try to parse a JSON array from the response, even if wrapped in markdown/extra text."""
    text = (text or "").strip()
    if "```" in text:
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None


def _extract_first_json_object(text: str):
    """Best-effort recovery for truncated responses that contain at least one full object."""
    text = (text or "").strip()
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : index + 1])
                except json.JSONDecodeError:
                    return None
    return None


def extract_wardrobe_from_image(image_bytes: bytes, content_type: str) -> list[dict] | None:
    """
    Use Gemini Vision to list clothing items in the image.
    Returns list of {"name", "category", "description", "color"}.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or ''
    if not api_key:
        raise ImageExtractionError('GEMINI_API_KEY is not configured.')
    configured_models = getattr(settings, 'GEMINI_IMAGE_MODELS', None) or DEFAULT_GEMINI_MODELS

    b64 = base64.standard_b64encode(image_bytes).decode('ascii')
    media_type = content_type or 'image/jpeg'
    prompt = """You are a wardrobe assistant. Your task is to list clothing and accessory items visible in the image.

RULES:
- Reply with ONLY a JSON array. No other text, no explanation, no markdown.
- Each element must be an object with exactly: "name", "category", "description", "color".
- category must be one of: top, bottom, outerwear, shoes, accessory, dress, other.
- Include dresses and accessories whenever they are visible.
- If the image is slightly blurry or partial, still list items you can reasonably identify (guess type/color if needed).
- If you truly see zero clothing items, reply with: []"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": media_type,
                            "data": b64,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json",
        },
    }
    response_json = None
    last_error = None
    for model_name in configured_models:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={api_key}"
        )
        try:
            response = requests.post(url, json=payload, timeout=45)
            if response.status_code == 404:
                snippet = (response.text or '').strip()
                if len(snippet) > 300:
                    snippet = snippet[:300] + '...'
                last_error = f'Model {model_name} not available: {snippet or "No response body."}'
                continue
            if not response.ok:
                snippet = (response.text or '').strip()
                if len(snippet) > 500:
                    snippet = snippet[:500] + '...'
                raise ImageExtractionError(
                    f'Gemini API returned HTTP {response.status_code} for model {model_name}: {snippet or "No response body."}'
                )
            response_json = response.json()
            break
        except ImageExtractionError:
            raise
        except requests.RequestException as exc:
            raise ImageExtractionError(f'Gemini network request failed: {exc}') from exc
        except ValueError as exc:
            raise ImageExtractionError(f'Gemini returned invalid JSON: {exc}') from exc

    if response_json is None:
        raise ImageExtractionError(last_error or 'No configured Gemini image model was available.')

    try:
        candidates = response_json.get("candidates") or []
        if not candidates:
            raise ImageExtractionError(f'Gemini returned no candidates: {json.dumps(response_json)[:500]}')
        parts = ((candidates[0].get("content") or {}).get("parts") or [])
        text = "".join((part.get("text") or "") for part in parts).strip()
        data = _extract_json_array(text)
        if data is None:
            recovered = _extract_first_json_object(text)
            if recovered is not None:
                data = [recovered]
        if data is None or not isinstance(data, list):
            finish_reason = (candidates[0].get("finishReason") or '').strip()
            detail = text[:500] or "Empty response."
            if finish_reason:
                detail = f'{detail} (finishReason={finish_reason})'
            raise ImageExtractionError(f'Gemini response was not a JSON array: {detail}')

        out: list[dict] = []
        for obj in data:
            if not isinstance(obj, dict):
                continue
            name = (obj.get("name") or "").strip()
            if not name:
                continue
            cat = (obj.get("category") or "other").lower().strip()
            if cat not in VALID_CATEGORIES:
                cat = "other"
            out.append({
                "name": name,
                "category": cat,
                "description": (obj.get("description") or "").strip(),
                "color": (obj.get("color") or "").strip(),
            })
        return out
    except ImageExtractionError:
        raise
    except Exception as exc:
        raise ImageExtractionError(f'Failed to parse extracted items: {exc}') from exc
