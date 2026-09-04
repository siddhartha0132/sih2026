/**
 * A simple, pure-CSS step-by-step flowchart - deliberately used instead of a
 * data chart with axes, since a sequence of boxes with arrows is far easier
 * for a first-time, low-financial-literacy rural audience to follow than a
 * line/bar graph.
 */
export default function FlowchartView({ steps }) {
  if (!steps || steps.length === 0) return null

  return (
    <div className="panel" style={{ marginBottom: 24 }}>
      <h2>Your journey, step by step</h2>
      <div className="flowchart">
        {steps.map((step, idx) => (
          <div className="flowchart-item" key={step.step_number}>
            <div className="flowchart-box">
              <div className="flowchart-number">{step.step_number}</div>
              <div className="flowchart-title">{step.title}</div>
              <div className="flowchart-desc">{step.description}</div>
            </div>
            {idx < steps.length - 1 && <div className="flowchart-arrow">→</div>}
          </div>
        ))}
      </div>
    </div>
  )
}

