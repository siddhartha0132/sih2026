const CATEGORIES = [
  'Dairy', 'Retail', 'Textiles', 'Food Processing', 'Poultry',
  'Handicrafts', 'Agri Input Store', 'Tailoring', 'Other',
]

export default function InputForm({ form, setForm, onSubmit, loading, showBusinessName = false }) {
  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <form
      className="panel"
      onSubmit={(e) => { e.preventDefault(); onSubmit() }}
    >
      {showBusinessName && (
        <div className="field">
          <label htmlFor="business_name">Name this business plan</label>
          <input id="business_name" value={form.business_name}
            onChange={(e) => update('business_name', e.target.value)}
            placeholder="e.g. Meena's Dairy" />
          <span className="field-hint">
            Use the same name each time you check in on this business — your
            saved plans will group together as one timeline.
          </span>
        </div>
      )}

      <h3>1. Where are you starting your business?</h3>
      <div className="field-row">
        <div className="field">
          <label htmlFor="village">Village / Town</label>
          <input id="village" required value={form.village}
            onChange={(e) => update('village', e.target.value)} placeholder="e.g. Bilaspur" />
        </div>
        <div className="field">
          <label htmlFor="block">Block / Tehsil (optional)</label>
          <input id="block" value={form.block}
            onChange={(e) => update('block', e.target.value)} placeholder="e.g. Kota" />
        </div>
      </div>
      <div className="field-row">
        <div className="field">
          <label htmlFor="district">District</label>
          <input id="district" required value={form.district}
            onChange={(e) => update('district', e.target.value)} placeholder="e.g. Kota" />
        </div>
        <div className="field">
          <label htmlFor="state">State</label>
          <input id="state" required value={form.state}
            onChange={(e) => update('state', e.target.value)} placeholder="e.g. Rajasthan" />
        </div>
      </div>
      <div className="field">
        <label htmlFor="pincode">PIN Code (optional, improves accuracy)</label>
        <input id="pincode" value={form.pincode}
          onChange={(e) => update('pincode', e.target.value)} placeholder="6-digit PIN" />
      </div>

      <h3 style={{ marginTop: 28 }}>2. What can you contribute?</h3>
      <div className="field">
        <label htmlFor="margin">Available margin capital (₹)</label>
        <input id="margin" type="number" min="1" required value={form.available_margin_capital}
          onChange={(e) => update('available_margin_capital', e.target.value)}
          placeholder="e.g. 100000" />
        <span className="field-hint">
          This is your own contribution — typically 10% of total project cost.
        </span>
      </div>

      <h3 style={{ marginTop: 28 }}>3. What business are you planning?</h3>
      <div className="field">
        <label htmlFor="category">Business category</label>
        <select id="category" value={form.business_category}
          onChange={(e) => update('business_category', e.target.value)}>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>
      {form.business_category === 'Other' && (
        <div className="field">
          <label htmlFor="category_other">Describe your business</label>
          <input id="category_other" value={form.business_category_other}
            onChange={(e) => update('business_category_other', e.target.value)} />
        </div>
      )}

      <h3 style={{ marginTop: 28 }}>Optional profile details</h3>
      <div className="field-row">
        <div className="field">
          <label htmlFor="age">Age</label>
          <input id="age" type="number" min="18" value={form.applicant_age}
            onChange={(e) => update('applicant_age', e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="gender">Gender</label>
          <select id="gender" value={form.applicant_gender}
            onChange={(e) => update('applicant_gender', e.target.value)}>
            <option value="">Prefer not to say</option>
            <option value="Female">Female</option>
            <option value="Male">Male</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      <button type="submit" className="btn btn-primary" disabled={loading} style={{ marginTop: 12 }}>
        {loading ? 'Generating your report…' : 'Generate feasibility report'}
      </button>
    </form>
  )
}
