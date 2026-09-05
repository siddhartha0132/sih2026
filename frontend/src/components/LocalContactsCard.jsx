import { t } from '../i18n.js'

/**
 * Sample/illustrative supply-chain contacts for a given business category —
 * raw material suppliers, distributors, retailers, and potential bulk
 * clients. These are mock names and phone numbers for demonstration only;
 * the disclaimer in the card makes that explicit to the reader.
 */
const CONTACTS_BY_CATEGORY = {
  Dairy: [
    { role: 'contacts.roleRawMaterial', name: 'Krishna Cattle Feed & Fodder Suppliers', phone: '+91 98230 14567' },
    { role: 'contacts.roleDistributor', name: 'Amul Village Milk Collection Center', phone: '+91 97890 22314' },
    { role: 'contacts.roleRetailer', name: 'Shree Ganesh Kirana & Dairy Booth', phone: '+91 90123 67789' },
    { role: 'contacts.roleClient', name: 'New Priya Sweets & Restaurant', phone: '+91 89012 45321' },
  ],
  Retail: [
    { role: 'contacts.roleRawMaterial', name: 'Bharat Wholesale Traders', phone: '+91 98765 11223' },
    { role: 'contacts.roleDistributor', name: 'Metro Cash & Carry Area Distributor', phone: '+91 97654 33445' },
    { role: 'contacts.roleRetailer', name: 'Gramin Retail Traders Association', phone: '+91 91234 55667' },
    { role: 'contacts.roleClient', name: 'Village Panchayat Ration Depot', phone: '+91 90876 77889' },
  ],
  Textiles: [
    { role: 'contacts.roleRawMaterial', name: 'Suraj Yarn & Fabric Mills', phone: '+91 98123 90876' },
    { role: 'contacts.roleDistributor', name: 'Surat Textile Wholesale Agency', phone: '+91 97012 65432' },
    { role: 'contacts.roleRetailer', name: 'Meena Garments & Cloth Store', phone: '+91 90345 21098' },
    { role: 'contacts.roleClient', name: 'Fashion Point Boutique Chain', phone: '+91 89234 76543' },
  ],
  'Food Processing': [
    { role: 'contacts.roleRawMaterial', name: 'Kisan Produce Aggregators', phone: '+91 98456 32109' },
    { role: 'contacts.roleDistributor', name: 'Annapurna FMCG Distribution', phone: '+91 97345 87654' },
    { role: 'contacts.roleRetailer', name: 'Local Kirana Chain Network', phone: '+91 90567 43210' },
    { role: 'contacts.roleClient', name: 'Highway Dhaba & Catering Services', phone: '+91 89678 90123' },
  ],
  Poultry: [
    { role: 'contacts.roleRawMaterial', name: 'Godrej Poultry Feed & Chick Supply', phone: '+91 98789 01234' },
    { role: 'contacts.roleDistributor', name: 'Egg & Broiler Wholesale Traders', phone: '+91 97890 12345' },
    { role: 'contacts.roleRetailer', name: 'Fresh Farm Meat & Egg Shop', phone: '+91 90901 23456' },
    { role: 'contacts.roleClient', name: 'City Caterers & Banquet Hall', phone: '+91 89012 34567' },
  ],
  Handicrafts: [
    { role: 'contacts.roleRawMaterial', name: 'Village Bamboo & Clay Material Depot', phone: '+91 98012 34567' },
    { role: 'contacts.roleDistributor', name: 'Handicraft Export & Wholesale Aggregators', phone: '+91 97123 45678' },
    { role: 'contacts.roleRetailer', name: 'State Handicraft Emporium', phone: '+91 90234 56789' },
    { role: 'contacts.roleClient', name: 'Craft Mela Exhibition Organizers', phone: '+91 89345 67890' },
  ],
  'Agri Input Store': [
    { role: 'contacts.roleRawMaterial', name: 'National Seeds & Fertilizer Company', phone: '+91 98456 78901' },
    { role: 'contacts.roleDistributor', name: 'Agri Input Wholesale Depot', phone: '+91 97567 89012' },
    { role: 'contacts.roleRetailer', name: 'Neighbouring Agri Input Retailers Group', phone: '+91 90678 90123' },
    { role: 'contacts.roleClient', name: 'Local Farmer Producer Organization (FPO)', phone: '+91 89789 01234' },
  ],
  Tailoring: [
    { role: 'contacts.roleRawMaterial', name: 'Ganpati Fabric & Thread Wholesalers', phone: '+91 98890 12345' },
    { role: 'contacts.roleDistributor', name: 'Garment Accessories Supply Co.', phone: '+91 97901 23456' },
    { role: 'contacts.roleRetailer', name: 'Local Boutique & Cloth Store Tie-up', phone: '+91 90012 34567' },
    { role: 'contacts.roleClient', name: 'Government School Uniform Committee', phone: '+91 89123 45678' },
  ],
  Other: [
    { role: 'contacts.roleRawMaterial', name: 'Local Raw Material Supply Co.', phone: '+91 98234 56789' },
    { role: 'contacts.roleDistributor', name: 'Regional Distribution Agency', phone: '+91 97345 67890' },
    { role: 'contacts.roleRetailer', name: 'Local Retailer Network Association', phone: '+91 90456 78901' },
    { role: 'contacts.roleClient', name: 'Institutional Bulk Buyer Contact', phone: '+91 89567 89012' },
  ],
}

export default function LocalContactsCard({ category, language = 'en' }) {
  const contacts = CONTACTS_BY_CATEGORY[category] || CONTACTS_BY_CATEGORY.Other

  return (
    <div className="panel" style={{ marginBottom: 24 }}>
      <h2>{t(language, 'contacts.title')}</h2>
      <p className="field-hint">{t(language, 'contacts.subtitle')}</p>

      <div className="stat-row" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
        {contacts.map((c) => (
          <div className="stat" key={`${c.role}-${c.name}`} style={{ textAlign: 'left' }}>
            <div className="field-hint" style={{ marginBottom: 4 }}>{t(language, c.role)}</div>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>{c.name}</div>
            <div className="stat-value" style={{ fontSize: '1.1rem' }}>
              {t(language, 'contacts.callLabel')}: {c.phone}
            </div>
          </div>
        ))}
      </div>

      <p className="confidence-note" style={{ marginTop: 16 }}>{t(language, 'contacts.disclaimer')}</p>
    </div>
  )
}
