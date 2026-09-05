import { useRef, useState } from 'react'
import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'
import FeasibilityCard from './FeasibilityCard.jsx'
import FinancialPlanCard from './FinancialPlanCard.jsx'
import RevenueProjectionCard from './RevenueProjectionCard.jsx'
import FlowchartView from './FlowchartView.jsx'
import LocalContactsCard from './LocalContactsCard.jsx'
import { t } from '../i18n.js'

/**
 * Shared renderer for one AdvisoryResponse — used by the live Advisor flow
 * (open or personal use) and by the History detail view when replaying a
 * saved report, so both stay visually identical.
 */
export default function ReportView({ response, language = 'en', fileLabel = 'GramVyapaar_Report', businessCategory }) {
  const reportRef = useRef(null)
  const [isDownloading, setIsDownloading] = useState(false)

  async function downloadPDF() {
    if (!reportRef.current) return
    setIsDownloading(true)
    try {
      const node = reportRef.current
      const scale = 2
      const canvas = await html2canvas(node, {
        scale,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
      })

      // A single addImage() onto one A4 page silently clips everything past
      // the first page's height — that's why the old PDF got cut off partway
      // through the report. Paginate properly: slice the full canvas into
      // page-sized chunks and add one PDF page per chunk. Prefer cutting at
      // the bottom edge of a top-level report card (FeasibilityCard,
      // RevenueProjectionCard, etc.) over an arbitrary pixel offset, so a
      // card isn't sliced in half across a page break unless it's taller
      // than one full page on its own.
      const breakpoints = []
      for (const child of node.children) {
        breakpoints.push(Math.round((child.offsetTop + child.offsetHeight) * scale))
      }

      const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
      const pdfWidth = pdf.internal.pageSize.getWidth()
      const pdfPageHeightMM = pdf.internal.pageSize.getHeight()
      const pxPerMm = canvas.width / pdfWidth
      const maxPageHeightPx = Math.floor(pdfPageHeightMM * pxPerMm)

      let y = 0
      let firstPage = true
      while (y < canvas.height) {
        const limit = Math.min(y + maxPageHeightPx, canvas.height)
        const candidate = breakpoints.filter((b) => b > y && b <= limit).pop()
        const sliceEnd = candidate || limit
        const sliceHeightPx = sliceEnd - y
        if (sliceHeightPx <= 0) break

        const sliceCanvas = document.createElement('canvas')
        sliceCanvas.width = canvas.width
        sliceCanvas.height = sliceHeightPx
        sliceCanvas.getContext('2d').drawImage(
          canvas, 0, y, canvas.width, sliceHeightPx, 0, 0, canvas.width, sliceHeightPx
        )
        const imgData = sliceCanvas.toDataURL('image/jpeg', 0.95)

        if (!firstPage) pdf.addPage()
        firstPage = false
        pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, sliceHeightPx / pxPerMm)

        y = sliceEnd
      }

      pdf.save(`${fileLabel}.pdf`)
    } catch (err) {
      console.error('Failed to generate PDF', err)
      alert(t(language, 'report.pdfFailed'))
    } finally {
      setIsDownloading(false)
    }
  }

  if (!response) return null

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <button className="btn btn-primary" onClick={downloadPDF} disabled={isDownloading}>
          {isDownloading ? t(language, 'report.generatingPdf') : t(language, 'report.downloadPdf')}
        </button>
      </div>

      <div ref={reportRef} style={{ background: 'var(--color-bg)', padding: '20px', borderRadius: '16px' }}>
        <FeasibilityCard report={response.feasibility_report} language={language} />
        <RevenueProjectionCard projection={response.feasibility_report.revenue_projection} language={language} />
        <FlowchartView steps={response.feasibility_report.journey_flowchart} language={language} />
        <FinancialPlanCard plan={response.financial_plan} language={language} />
        <LocalContactsCard category={businessCategory} language={language} />
        <div className="disclaimer" style={{ marginTop: 24 }}>
          {response.disclaimer}
        </div>
      </div>
    </div>
  )
}
