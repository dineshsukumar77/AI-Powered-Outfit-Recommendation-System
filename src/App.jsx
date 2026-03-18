import React, { useEffect, useState } from 'react'
import { getWardrobes, getWardrobe, getRecommendations, getWeather, login as apiLogin, register as apiRegister } from './api'
import WardrobeEntry from './WardrobeEntry'
import ContextForm from './ContextForm'
import OutfitResults from './OutfitResults'
import SavedWardrobes from './SavedWardrobes'
import './App.css'

const CATEGORIES = [
  { value: 'top', label: 'Top' },
  { value: 'bottom', label: 'Bottom' },
  { value: 'outerwear', label: 'Outerwear' },
  { value: 'shoes', label: 'Shoes' },
  { value: 'accessory', label: 'Accessory' },
  { value: 'dress', label: 'Dress' },
  { value: 'other', label: 'Other' },
]

const LOOKBOOKS = {
  authLeft: [
    {
      title: 'Dress Edit',
      subtitle: 'Soft silhouettes for date nights and events',
      image:
        'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80',
    },
    {
      title: 'Accessories',
      subtitle: 'Bags, jewelry, and heels to finish the look',
      image:
        'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=900&q=80',
    },
  ],
  authRight: [
    {
      title: 'Evening Dress',
      subtitle: 'Elegant textures for special plans and dinner dates',
      image:
        'https://images.unsplash.com/photo-1492707892479-7bc8d5a4ee93?auto=format&fit=crop&w=900&q=80',
    },
    {
      title: 'Jewelry Edit',
      subtitle: 'Statement details that complete the whole look',
      image:
        'https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?auto=format&fit=crop&w=900&q=80',
    },
  ],
  dashboardLeft: [
    {
      title: 'Statement Layers',
      subtitle: 'Polished pieces for work, brunch, and travel',
      image:
        'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80',
    },
    {
      title: 'Finishing Touches',
      subtitle: 'Accessories that lift simple outfits instantly',
      image:
        'https://images.unsplash.com/photo-1576053139778-7e32f2ae3cfd?auto=format&fit=crop&w=900&q=80',
    },
  ],
  dashboardRight: [
    {
      title: 'Dress Studio',
      subtitle: 'Modern occasionwear with sharp, editorial silhouettes',
      image:
        'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=900&q=80',
    },
    {
      title: 'Luxury Details',
      subtitle: 'Bags and finishing pieces for a styled wardrobe',
      image:
        'https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=900&q=80',
    },
  ],
}

const defaultItem = () => ({ name: '', category: 'top', description: '', color: '' })

function SideLookbook({ items, position }) {
  return (
    <aside className={`side-lookbook side-lookbook-${position}`} aria-hidden="true">
      {items.map((item) => (
        <article
          key={`${position}-${item.title}`}
          className="lookbook-card"
          style={{
            backgroundImage: `linear-gradient(180deg, rgba(17, 24, 39, 0.08), rgba(17, 24, 39, 0.72)), url(${item.image})`,
          }}
        >
          <div className="lookbook-copy">
            <span className="lookbook-kicker">{position === 'left' ? 'Style inspo' : 'Closet mood'}</span>
            <h3>{item.title}</h3>
            <p>{item.subtitle}</p>
          </div>
        </article>
      ))}
    </aside>
  )
}

function App() {
  const [user, setUser] = useState(null)
  const [showRegister, setShowRegister] = useState(false)
  const [loginName, setLoginName] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [loginError, setLoginError] = useState('')
  const [registerUsername, setRegisterUsername] = useState('')
  const [registerPassword, setRegisterPassword] = useState('')
  const [registerConfirm, setRegisterConfirm] = useState('')
  const [registerError, setRegisterError] = useState('')
  const [authLoading, setAuthLoading] = useState(false)
  const [items, setItems] = useState([defaultItem()])
  const [occasion, setOccasion] = useState('')
  const [weather, setWeather] = useState('')
  const [weatherCity, setWeatherCity] = useState('')
  const [weatherFetched, setWeatherFetched] = useState('')
  const [stylePreference, setStylePreference] = useState('casual')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [savedWardrobes, setSavedWardrobes] = useState([])
  const [selectedWardrobeId, setSelectedWardrobeId] = useState(null)
  const [loadedWardrobe, setLoadedWardrobe] = useState(null)

  useEffect(() => {
    if (!user?.name) {
      setSavedWardrobes([])
      setSelectedWardrobeId(null)
      return
    }
    getWardrobes(user.name)
      .then((ws) => {
        setSavedWardrobes(ws)
        const sample = ws.find((w) => w.name === 'Sample Wardrobe')
        if (sample) setSelectedWardrobeId(sample.id)
        else if (ws.length) setSelectedWardrobeId(ws[0].id)
        else setSelectedWardrobeId(null)
      })
      .catch(() => setSavedWardrobes([]))
  }, [user])

  useEffect(() => {
    if (!selectedWardrobeId || !user?.name) {
      setLoadedWardrobe(null)
      if (!selectedWardrobeId) return
    }
    if (!user?.name) return
    getWardrobe(selectedWardrobeId, user.name)
      .then((w) => {
        setLoadedWardrobe(w)
        setItems(
          w.items.length
            ? w.items.map((i) => ({
                name: i.name,
                category: i.category,
                description: i.description || '',
                color: i.color || '',
              }))
            : [defaultItem()]
        )
      })
      .catch(() => setSelectedWardrobeId(null))
  }, [selectedWardrobeId, user])

  const handleFetchWeather = () => {
    if (!weatherCity.trim()) return
    setLoading(true)
    setError(null)
    getWeather(weatherCity.trim())
      .then((w) => {
        setWeatherFetched(w)
        setWeather(w)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  const wardrobePayload = items
    .filter((i) => i.name.trim())
    .map((i) => ({
      name: i.name.trim(),
      category: i.category,
      description: (i.description || '').trim(),
      color: (i.color || '').trim(),
    }))

  const handleRecommend = () => {
    if (!wardrobePayload.length) {
      setError('Add at least one wardrobe item.')
      return
    }
    setError(null)
    setResult(null)
    setLoading(true)
    const body = {
      wardrobe_items: wardrobePayload,
      occasion: occasion.trim() || 'casual day',
      style_preference: stylePreference,
      user_name: user?.name || '',
    }
    if (weather.trim()) body.weather = weather
    if (weatherCity.trim()) body.weather_city = weatherCity.trim()

    getRecommendations(body)
      .then(setResult)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  const onWardrobeSaved = (newWardrobeId) => {
    if (!user?.name) return
    getWardrobes(user.name).then((ws) => {
      setSavedWardrobes(ws)
      if (!newWardrobeId) return
      setSelectedWardrobeId(newWardrobeId)
      return getWardrobe(newWardrobeId, user.name).then((w) => {
        setLoadedWardrobe(w)
        setItems(
          w.items.length
            ? w.items.map((i) => ({
                name: i.name,
                category: i.category,
                description: i.description || '',
                color: i.color || '',
              }))
            : [defaultItem()]
        )
      })
    })
  }

  const handleLogin = (e) => {
    e.preventDefault()
    setLoginError('')
    const username = loginName.trim()
    const password = loginPassword
    if (!username || !password) {
      setLoginError('Please enter username and password.')
      return
    }
    setAuthLoading(true)
    apiLogin(username, password)
      .then((data) => setUser({ name: data.username }))
      .catch((err) => setLoginError(err.message))
      .finally(() => setAuthLoading(false))
  }

  const handleRegister = (e) => {
    e.preventDefault()
    setRegisterError('')
    const username = registerUsername.trim()
    const password = registerPassword
    if (!username || !password) {
      setRegisterError('Please enter username and password.')
      return
    }
    if (password !== registerConfirm) {
      setRegisterError('Passwords do not match.')
      return
    }
    if (password.length < 4) {
      setRegisterError('Password must be at least 4 characters.')
      return
    }
    setAuthLoading(true)
    apiRegister(username, password)
      .then(() => {
        setShowRegister(false)
        setLoginName(username)
        setLoginPassword('')
        setRegisterUsername('')
        setRegisterPassword('')
        setRegisterConfirm('')
        setRegisterError('')
      })
      .catch((err) => setRegisterError(err.message))
      .finally(() => setAuthLoading(false))
  }

  const handleLogout = () => {
    setUser(null)
    setResult(null)
    setError(null)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-top">
          <div>
            <h1>AI Outfit Stylist</h1>
            <p className="tagline">Log in to your style studio, then mix, match, and get AI-powered outfit ideas.</p>
          </div>
          {user && (
            <div className="user-pill">
              <span className="user-name">Hi, {user.name}</span>
              <button type="button" className="btn btn-secondary btn-sm" onClick={handleLogout}>
                Logout
              </button>
            </div>
          )}
        </div>
      </header>

      {!user && (
        <div className="page-shell auth-page-shell">
          <SideLookbook items={LOOKBOOKS.authLeft} position="left" />
          <main className="main main-column auth-main">
            <section className="card section-wardrobe auth-card">
              <h2>{showRegister ? 'Create account' : 'Welcome'}</h2>
              <p className="tagline">
                {showRegister
                  ? 'Register to save your wardrobes and outfit recommendations in your account.'
                  : 'Sign in to view your wardrobe and get AI outfit recommendations.'}
              </p>
              {!showRegister ? (
                <form className="login-form" onSubmit={handleLogin}>
                  <label className="login-label">
                    Username
                    <input
                      type="text"
                      placeholder="Enter username"
                      value={loginName}
                      onChange={(e) => setLoginName(e.target.value)}
                      className="input"
                    />
                  </label>
                  <label className="login-label">
                    Password
                    <input
                      type="password"
                      placeholder="Enter password"
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      className="input"
                    />
                  </label>
                  {loginError && <p className="login-error">{loginError}</p>}
                  <button type="submit" className="btn btn-primary login-btn" disabled={authLoading}>
                    {authLoading ? 'Signing in...' : 'Sign in'}
                  </button>
                  <p className="auth-switch">
                    No account?{' '}
                    <button
                      type="button"
                      className="link-btn"
                      onClick={() => {
                        setShowRegister(true)
                        setLoginError('')
                        setRegisterError('')
                      }}
                    >
                      Register
                    </button>
                  </p>
                </form>
              ) : (
                <form className="login-form" onSubmit={handleRegister}>
                  <label className="login-label">
                    Username
                    <input
                      type="text"
                      placeholder="Choose a username (min 2 characters)"
                      value={registerUsername}
                      onChange={(e) => setRegisterUsername(e.target.value)}
                      className="input"
                    />
                  </label>
                  <label className="login-label">
                    Password
                    <input
                      type="password"
                      placeholder="Password (min 4 characters)"
                      value={registerPassword}
                      onChange={(e) => setRegisterPassword(e.target.value)}
                      className="input"
                    />
                  </label>
                  <label className="login-label">
                    Confirm password
                    <input
                      type="password"
                      placeholder="Confirm password"
                      value={registerConfirm}
                      onChange={(e) => setRegisterConfirm(e.target.value)}
                      className="input"
                    />
                  </label>
                  {registerError && <p className="login-error">{registerError}</p>}
                  <button type="submit" className="btn btn-primary login-btn" disabled={authLoading}>
                    {authLoading ? 'Creating account...' : 'Register'}
                  </button>
                  <p className="auth-switch">
                    Already have an account?{' '}
                    <button
                      type="button"
                      className="link-btn"
                      onClick={() => {
                        setShowRegister(false)
                        setLoginError('')
                        setRegisterError('')
                      }}
                    >
                      Sign in
                    </button>
                  </p>
                </form>
              )}
            </section>
          </main>
          <SideLookbook items={LOOKBOOKS.authRight} position="right" />
        </div>
      )}

      {user && (
        <div className="page-shell">
          <SideLookbook items={LOOKBOOKS.dashboardLeft} position="left" />
          <main className="main main-column">
            <section className="card section-wardrobe">
              <h2>Your wardrobe</h2>
              {loadedWardrobe && (
                <p className="wardrobe-summary">
                  Viewing: <strong>{loadedWardrobe.name}</strong> - {loadedWardrobe.items.length} items
                </p>
              )}
              {savedWardrobes.length === 0 && (
                <p className="wardrobe-empty">You have no saved wardrobes yet. Add items below and click Save wardrobe.</p>
              )}
              <SavedWardrobes
                saved={savedWardrobes}
                selectedId={selectedWardrobeId}
                onSelect={setSelectedWardrobeId}
                onRefresh={() => user?.name && getWardrobes(user.name).then(setSavedWardrobes)}
                personName={user?.name}
              />
              <WardrobeEntry
                items={items}
                setItems={setItems}
                categories={CATEGORIES}
                defaultItem={defaultItem}
                loadedWardrobe={loadedWardrobe}
                onSave={onWardrobeSaved}
                personName={user?.name}
              />
            </section>

            <section className="card section-context">
              <h2>Context</h2>
              <ContextForm
                occasion={occasion}
                setOccasion={setOccasion}
                weather={weather}
                setWeather={setWeather}
                weatherCity={weatherCity}
                setWeatherCity={setWeatherCity}
                weatherFetched={weatherFetched}
                onFetchWeather={handleFetchWeather}
                stylePreference={stylePreference}
                setStylePreference={setStylePreference}
                loading={loading}
              />
            </section>

            <div className="actions">
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleRecommend}
                disabled={loading || !wardrobePayload.length}
              >
                {loading ? 'Getting recommendations...' : 'Get outfit recommendations'}
              </button>
            </div>

            {error && <div className="message message-error">{error}</div>}

            {result && (
              <OutfitResults
                outfits={result.outfits}
                suggestedPurchase={result.suggested_purchase}
              />
            )}
          </main>
          <SideLookbook items={LOOKBOOKS.dashboardRight} position="right" />
        </div>
      )}
    </div>
  )
}

export default App
