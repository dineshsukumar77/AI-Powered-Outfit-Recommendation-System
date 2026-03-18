const BASE = '/api';

export async function login(username, password) {
  const r = await fetch(`${BASE}/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(err.detail || 'Login failed');
  }
  return r.json();
}

export async function register(username, password) {
  const r = await fetch(`${BASE}/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(err.detail || 'Registration failed');
  }
  return r.json();
}

export async function getWardrobes(personName) {
  if (!personName) return [];
  const r = await fetch(`${BASE}/wardrobes/?person_name=${encodeURIComponent(personName)}`);
  if (!r.ok) throw new Error('Failed to load wardrobes');
  return r.json();
}

export async function getWardrobe(id, personName) {
  if (!personName) throw new Error('Person name required');
  const r = await fetch(`${BASE}/wardrobes/${id}/?person_name=${encodeURIComponent(personName)}`);
  if (!r.ok) throw new Error('Failed to load wardrobe');
  return r.json();
}

export async function createWardrobe(data) {
  const r = await fetch(`${BASE}/wardrobes/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!r.ok) throw new Error('Failed to create wardrobe');
  return r.json();
}

export async function addWardrobeItem(wardrobeId, item, personName) {
  const url = personName
    ? `${BASE}/wardrobes/${wardrobeId}/items/?person_name=${encodeURIComponent(personName)}`
    : `${BASE}/wardrobes/${wardrobeId}/items/`;
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to add item');
  }
  return r.json();
}

export async function deleteWardrobe(id, personName) {
  const url = personName
    ? `${BASE}/wardrobes/${id}/?person_name=${encodeURIComponent(personName)}`
    : `${BASE}/wardrobes/${id}/`;
  const r = await fetch(url, { method: 'DELETE' });
  if (!r.ok) throw new Error('Failed to delete wardrobe');
}

export async function getWeather(city) {
  const r = await fetch(`${BASE}/weather/?city=${encodeURIComponent(city)}`);
  if (!r.ok) throw new Error('Weather unavailable');
  const data = await r.json();
  return data.weather;
}

export async function getRecommendations(body) {
  const r = await fetch(`${BASE}/recommend/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(err.detail || 'Recommendation failed');
  }
  return r.json();
}

export async function extractWardrobeFromImage(file, options = {}) {
  const form = new FormData();
  form.append('image', file);
  if (options.personName) form.append('person_name', options.personName);
  if (options.wardrobeId) form.append('wardrobe_id', String(options.wardrobeId));
  const r = await fetch(`${BASE}/extract-wardrobe/`, {
    method: 'POST',
    body: form,
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to extract items from image');
  }
  return r.json();
}
