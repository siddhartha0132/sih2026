import { useRef, useState } from 'react'
import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'
import FeasibilityCard from './FeasibilityCard.jsx'
import FinancialPlanCard from './FinancialPlanCard.jsx'
import RevenueProjectionCard from './RevenueProjectionCard.jsx'
import FlowchartView from './FlowchartView.jsx'

/**
 * Shared renderer for one AdvisoryResponse — used by the live Advisor flow
 * (open or personal use) and by the History detail view when replaying a
 * saved report, so both stay visually identical.
 */
export default function ReportView({ response, fileLabel = 'GramVyapaar_Report' }) {
  const reportRef = useRef(null)
  const [isDownloading, setIsDownloading] = useState(false)

  async function downloadPDF() {
    if (!reportRef.current) return
    setIsDownloading(true)
    try {
      const canvas = await html2canvas(reportRef.current, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
      })
      const imgData = canvas.toDataURL('image/jpeg', 1.0)
      const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
      const pdfWidth = pdf.internal.pageSize.getWidth()
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width
      pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, pdfHeight)
      pdf.save(`${fileLabel}.pdf`)
    } catch (err) {
      console.error('Failed to generate PDF', err)
      alert('Failed to download PDF. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  if (!response) return null

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <button className="btn btn-primary" onClick={downloadPDF} disabled={isDownloading}>
          {isDownloading ? 'Generating PDF...' : '📄 Download PDF Report'}
        </button>
      </div>

      <div ref={reportRef} style={{ background: 'var(--color-bg)', padding: '20px', borderRadius: '16px' }}>
        <FeasibilityCard report={response.feasibility_report} />
        <RevenueProjectionCard projection={response.feasibility_report.revenue_projection} />
        <FlowchartView steps={response.feasibility_report.journey_flowchart} />
        <FinancialPlanCard plan={response.financial_plan} />
        <div className="disclaimer" style={{ marginTop: 24 }}>
          {response.disclaimer}
        </div>
      </div>
    </div>
  )
}
