"""
LLM-powered outfit recommendation logic.
Uses OpenAI API; response is parsed for structured outfit suggestions.
"""
import json
import re
from django.conf import settings

def get_outfit_recommendations(wardrobe_items: list[dict], occasion: str, weather: str, style: str) -> dict:
    """
    Call LLM to generate 2-3 outfit combinations with reasoning and one suggested purchase.
    wardrobe_items: list of {"name", "category", "description", "color"}
    Returns: {"outfits": [...], "suggested_purchase": str}
    """
    api_key = getattr(settings, 'OPENAI_API_KEY', None) or ''
    if not api_key:
        return _fallback_recommendations(wardrobe_items, occasion, weather, style)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
    except Exception:
        return _fallback_recommendations(wardrobe_items, occasion, weather, style)

    items_text = "\n".join(
        f"- {item.get('name', '')} ({item.get('category', '')}): {item.get('description', '') or item.get('color', '')}"
        for item in wardrobe_items
    )

    system = """You are a fashion stylist. Given a list of wardrobe items, occasion, weather, and style preference,
output exactly a valid JSON object with this structure (no markdown, no extra text):
{
  "outfits": [
    {
      "name": "short title for this outfit",
      "items": ["item name 1", "item name 2", ...],
      "reasoning": "1-2 sentences why this works for the occasion, weather, and style."
    }
  ],
  "suggested_purchase": "One specific item to buy that would complement the wardrobe and context (1 sentence)."
}
Give exactly 2 or 3 outfits. Use only item names that appear in the user's wardrobe. Be concise."""

    user = f"""Wardrobe items:
{items_text}

Occasion: {occasion}
Weather: {weather}
Style preference: {style}

Respond with only the JSON object."""

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user},
            ],
            temperature=0.7,
        )
        text = response.choices[0].message.content.strip()
        # Strip markdown code block if present
        if text.startswith('```'):
            text = re.sub(r'^```\w*\n?', '', text).rstrip('`')
        data = json.loads(text)
        if 'outfits' not in data:
            data['outfits'] = []
        if 'suggested_purchase' not in data:
            data['suggested_purchase'] = 'Consider adding a versatile piece that matches your style.'
        return data
    except Exception:
        return _fallback_recommendations(wardrobe_items, occasion, weather, style)


def _fallback_recommendations(wardrobe_items: list[dict], occasion: str, weather: str, style: str) -> dict:
    """When LLM is unavailable, return simple rule-based suggestions."""
    tops = [i for i in wardrobe_items if i.get('category') in ('top', 'dress')]
    bottoms = [i for i in wardrobe_items if i.get('category') == 'bottom']
    shoes = [i for i in wardrobe_items if i.get('category') == 'shoes']
    outer = [i for i in wardrobe_items if i.get('category') == 'outerwear']
    accessories = [i for i in wardrobe_items if i.get('category') == 'accessory']

    outfits = []
    if tops and bottoms and shoes:
        t, b, s = tops[0], bottoms[0], shoes[0]
        outfits.append({
            'name': 'Classic combo',
            'items': [t.get('name'), b.get('name'), s.get('name')],
            'reasoning': f'Pairs your {t.get("name")} with {b.get("name")} and {s.get("name")} — suitable for {occasion} in {weather}, matching a {style} style.',
        })
    if len(tops) > 1 and bottoms and shoes:
        t, b, s = tops[1], bottoms[0], shoes[0]
        outfits.append({
            'name': 'Alternative look',
            'items': [t.get('name'), b.get('name'), s.get('name')],
            'reasoning': f'Alternative pairing for {occasion} with a {style} vibe, appropriate for {weather}.',
        })
    if not outfits and wardrobe_items:
        names = [i.get('name') for i in wardrobe_items[:4]]
        outfits.append({
            'name': 'Mix from wardrobe',
            'items': names,
            'reasoning': f'Combining items from your wardrobe for {occasion}, {weather}, {style}.',
        })

    return {
        'outfits': outfits[:3],
        'suggested_purchase': 'A versatile neutral belt or a quality white sneaker would complement many outfits.',
    }
