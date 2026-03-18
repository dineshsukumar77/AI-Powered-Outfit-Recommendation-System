import React from 'react'
import './ContextForm.css'

const STYLES = [
  { value: 'casual', label: 'Casual' },
  { value: 'smart casual', label: 'Smart casual' },
  { value: 'formal', label: 'Formal' },
  { value: 'minimal', label: 'Minimal' },
  { value: 'bohemian', label: 'Bohemian' },
  { value: 'sporty', label: 'Sporty' },
]

function ContextForm({
  occasion,
  setOccasion,
  weather,
  setWeather,
  weatherCity,
  setWeatherCity,
  weatherFetched,
  onFetchWeather,
  stylePreference,
  setStylePreference,
  loading,
}) {
  return (
    <div className="context-form">
      <label className="label">
        Occasion
        <input
          type="text"
          placeholder="e.g. Job interview, Weekend brunch"
          value={occasion}
          onChange={(e) => setOccasion(e.target.value)}
          className="input full"
        />
      </label>

      <div className="weather-block">
        <label className="label">
          Weather (or fetch by city)
          <div className="weather-row">
            <input
              type="text"
              placeholder="e.g. Sunny, 72°F"
              value={weather}
              onChange={(e) => setWeather(e.target.value)}
              className="input full"
            />
          </div>
        </label>
        <div className="weather-fetch">
          <input
            type="text"
            placeholder="City for live weather"
            value={weatherCity}
            onChange={(e) => setWeatherCity(e.target.value)}
            className="input"
          />
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={onFetchWeather}
            disabled={loading || !weatherCity.trim()}
          >
            {loading ? '…' : 'Get weather'}
          </button>
        </div>
        {weatherFetched && (
          <p className={`weather-result ${weatherFetched.toLowerCase().includes('error') || weatherFetched.toLowerCase().includes('unknown') ? 'weather-error' : ''}`}>
            {weatherFetched.toLowerCase().includes('error') || weatherFetched.toLowerCase().includes('unknown') ? weatherFetched : `Fetched: ${weatherFetched}`}
          </p>
        )}
      </div>

      <label className="label">
        Style preference
        <select
          value={stylePreference}
          onChange={(e) => setStylePreference(e.target.value)}
          className="input full"
        >
          {STYLES.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
      </label>
    </div>
  )
}

export default ContextForm
