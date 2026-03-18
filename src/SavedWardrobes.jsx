import React from 'react'
import { deleteWardrobe } from './api'
import './SavedWardrobes.css'

function SavedWardrobes({ saved, selectedId, onSelect, onRefresh, personName }) {
  const [deleting, setDeleting] = React.useState(null)

  const handleDelete = async (e, id) => {
    e.stopPropagation()
    if (!id) return
    setDeleting(id)
    try {
      await deleteWardrobe(id, personName)
      if (selectedId === id) onSelect(null)
      onRefresh?.()
    } finally {
      setDeleting(null)
    }
  }

  if (!saved?.length) return null

  return (
    <div className="saved-wardrobes">
      <span className="saved-label">Saved wardrobes:</span>
      <div className="saved-list">
        {saved.map((w) => (
          <div
            key={w.id}
            className={`saved-item ${selectedId === w.id ? 'selected' : ''}`}
            onClick={() => onSelect(selectedId === w.id ? null : w.id)}
          >
            <span>{w.name} ({w.item_count ?? 0} items)</span>
            <button
              type="button"
              className="btn-delete"
              onClick={(e) => handleDelete(e, w.id)}
              disabled={deleting === w.id}
              aria-label="Delete wardrobe"
            >
              {deleting === w.id ? '…' : '×'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SavedWardrobes
