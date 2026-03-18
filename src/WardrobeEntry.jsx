import React from 'react'
import { createWardrobe, addWardrobeItem, extractWardrobeFromImage } from './api'
import './WardrobeEntry.css'

function WardrobeEntry({ items, setItems, categories, defaultItem, loadedWardrobe, onSave, personName }) {
  const addRow = () => setItems((prev) => [...prev, defaultItem()])
  const fileInputRef = React.useRef(null)

  const updateItem = (index, field, value) => {
    setItems((prev) => {
      const next = [...prev]
      next[index] = { ...next[index], [field]: value }
      return next
    })
  }

  const removeRow = (index) => {
    if (items.length <= 1) return
    setItems((prev) => prev.filter((_, i) => i !== index))
  }

  const [saving, setSaving] = React.useState(false)
  const [saveError, setSaveError] = React.useState(null)
  const [extractLoading, setExtractLoading] = React.useState(false)
  const [extractError, setExtractError] = React.useState(null)
  const [extractSuccess, setExtractSuccess] = React.useState(null)

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.type.startsWith('image/')) {
      setExtractError('Please select an image file (JPEG, PNG, GIF, or WebP).')
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      setExtractError('Image must be under 5MB.')
      return
    }
    setExtractError(null)
    setExtractSuccess(null)
    setExtractLoading(true)
    try {
      const response = await extractWardrobeFromImage(file, {
        personName,
        wardrobeId: loadedWardrobe?.id,
      })
      const extracted = response.items || []
      if (extracted.length) {
        setItems(
          extracted.map((i) => ({
            name: i.name,
            category: i.category || 'other',
            description: i.description || '',
            color: i.color || '',
          }))
        )
        if (response.wardrobe?.id) {
          onSave?.(response.wardrobe.id)
          setExtractSuccess(`Extracted and saved ${response.saved_count || extracted.length} item(s) to ${response.wardrobe.name}.`)
        } else {
          setExtractSuccess(`Added ${extracted.length} item(s) from photo.`)
        }
      } else {
        setExtractSuccess('No items detected in the image. Try a clearer photo of your clothes.')
      }
    } catch (err) {
      setExtractError(err.message)
    } finally {
      setExtractLoading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleSaveWardrobe = async () => {
    const valid = items.filter((i) => i.name.trim())
    if (!valid.length || !personName) return
    setSaveError(null)
    setSaving(true)
    try {
      const wardrobe = await createWardrobe({ name: 'My Wardrobe', person_name: personName })
      for (const item of valid) {
        await addWardrobeItem(wardrobe.id, {
          name: item.name.trim(),
          category: item.category,
          description: item.description.trim(),
          color: item.color.trim(),
        }, personName)
      }
      onSave?.(wardrobe.id)
    } catch (e) {
      setSaveError(e.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="wardrobe-entry">
      {items.length > 0 && (
        <div className="wardrobe-row wardrobe-row--header" aria-hidden="true">
          <span className="wardrobe-label">Name</span>
          <span className="wardrobe-label">Category</span>
          <span className="wardrobe-label">Description</span>
          <span className="wardrobe-label">Color</span>
          <span className="wardrobe-label wardrobe-label--action" />
        </div>
      )}
      {items.map((item, index) => (
        <div key={index} className="wardrobe-row">
          <input
            type="text"
            placeholder="Name (e.g. Navy blazer)"
            value={item.name}
            onChange={(e) => updateItem(index, 'name', e.target.value)}
            className="input input-name"
          />
          <select
            value={item.category}
            onChange={(e) => updateItem(index, 'category', e.target.value)}
            className="input input-category"
          >
            {categories.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Description (optional)"
            value={item.description}
            onChange={(e) => updateItem(index, 'description', e.target.value)}
            className="input input-desc"
          />
          <input
            type="text"
            placeholder="Color (optional)"
            value={item.color}
            onChange={(e) => updateItem(index, 'color', e.target.value)}
            className="input input-color"
          />
          <button
            type="button"
            className="btn btn-remove"
            onClick={() => removeRow(index)}
            disabled={items.length <= 1}
            aria-label="Remove item"
          >
            x
          </button>
        </div>
      ))}
      <div className="wardrobe-upload">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/gif,image/webp"
          onChange={handleImageUpload}
          className="wardrobe-upload-input"
          disabled={extractLoading}
        />
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() => fileInputRef.current?.click()}
          disabled={extractLoading}
        >
          {extractLoading ? 'Extracting...' : 'Upload photo to add items'}
        </button>
        {extractError && <p className="save-error">{extractError}</p>}
        {extractSuccess && <p className="extract-success">{extractSuccess}</p>}
      </div>
      <div className="wardrobe-actions">
        <button type="button" className="btn btn-secondary btn-sm" onClick={addRow}>
          + Add item
        </button>
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={handleSaveWardrobe}
          disabled={saving || !personName || !items.some((i) => i.name.trim())}
        >
          {saving ? 'Saving...' : 'Save wardrobe'}
        </button>
      </div>
      {saveError && <p className="save-error">{saveError}</p>}
    </div>
  )
}

export default WardrobeEntry
