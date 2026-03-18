import React from 'react'
import './OutfitResults.css'

function OutfitResults({ outfits = [], suggestedPurchase }) {
  return (
    <section className="card results">
      <h2>Outfit recommendations</h2>
      <div className="outfits-list">
        {outfits.map((outfit, i) => (
          <article key={i} className="outfit-card">
            <h3>{outfit.name}</h3>
            <ul className="outfit-items">
              {(outfit.items || []).map((item, j) => (
                <li key={j}>{item}</li>
              ))}
            </ul>
            <p className="reasoning">{outfit.reasoning}</p>
          </article>
        ))}
      </div>
      {suggestedPurchase && (
        <div className="suggested-purchase">
          <h3>Suggested purchase</h3>
          <p>{suggestedPurchase}</p>
        </div>
      )}
    </section>
  )
}

export default OutfitResults
