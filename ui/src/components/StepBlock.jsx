import { useState } from 'react'
import ReactMarkdown from 'react-markdown'

const TYPE_LABEL = {
  planner:    { label: 'Planner',    bg: 'bg-violet-100', text: 'text-violet-700' },
  search:     { label: 'Search',     bg: 'bg-blue-100',   text: 'text-blue-700'   },
  reflection: { label: 'Reflection', bg: 'bg-amber-100',  text: 'text-amber-700'  },
  synthesis:  { label: 'Synthesis',  bg: 'bg-green-100',  text: 'text-green-700'  },
}

function Badge({ type }) {
  const t = TYPE_LABEL[type] || { label: type, bg: 'bg-gray-100', text: 'text-gray-600' }
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${t.bg} ${t.text}`}>
      {t.label}
    </span>
  )
}

function PlannerOutput({ data }) {
  const questions = data?.sub_questions || []
  return (
    <ul className="space-y-1 mt-2">
      {questions.map((q, i) => (
        <li key={i} className="text-sm text-gray-700 flex gap-2">
          <span className="text-gray-400 flex-shrink-0">{i + 1}.</span>
          <span>{q}</span>
        </li>
      ))}
    </ul>
  )
}

function SearchOutput({ data }) {
  const results = data?.results || []
  return (
    <div className="mt-2 space-y-2">
      <p className="text-xs text-gray-400">{results.length} results retrieved</p>
      {results.slice(0, 5).map((r, i) => (
        <div key={i} className="text-sm">
          <a
            href={r.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-600 hover:underline font-medium"
          >
            {r.title || r.url}
          </a>
          {r.content && (
            <p className="text-gray-500 text-xs mt-0.5 line-clamp-2">{r.content}</p>
          )}
        </div>
      ))}
      {results.length > 5 && (
        <p className="text-xs text-gray-400">+{results.length - 5} more</p>
      )}
    </div>
  )
}

function ReflectionOutput({ data, triggeredLoop }) {
  return (
    <div className="mt-2 space-y-2">
      <div className={`inline-flex items-center gap-1.5 text-xs font-medium px-2 py-1 rounded-full ${
        triggeredLoop ? 'bg-amber-50 text-amber-700' : 'bg-green-50 text-green-700'
      }`}>
        {triggeredLoop ? '⚠ Loop triggered — refining search' : '✓ Adequate — proceeding to synthesis'}
      </div>
      {data?.reason && (
        <p className="text-sm text-gray-600 italic">"{data.reason}"</p>
      )}
      {triggeredLoop && data?.refined_queries?.length > 0 && (
        <div>
          <p className="text-xs text-gray-400 mb-1">Refined queries:</p>
          <ul className="space-y-0.5">
            {data.refined_queries.map((q, i) => (
              <li key={i} className="text-sm text-gray-700">• {q}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function SynthesisOutput({ data }) {
  const report = data?.report || ''
  return (
    <div className="mt-3 prose prose-sm max-w-none text-gray-800">
      <ReactMarkdown>{report}</ReactMarkdown>
    </div>
  )
}

function StepContent({ step }) {
  const out = step.output_data
  if (!out) return <p className="text-xs text-gray-400 mt-2">Running...</p>
  if (step.step_type === 'planner')    return <PlannerOutput data={out} />
  if (step.step_type === 'search')     return <SearchOutput data={out} />
  if (step.step_type === 'reflection') return <ReflectionOutput data={out} triggeredLoop={step.triggered_loop} />
  if (step.step_type === 'synthesis')  return <SynthesisOutput data={out} />
  return null
}

export default function StepBlock({ step, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="border border-gray-100 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors text-left"
      >
        <span className="text-xs text-gray-400 w-5 flex-shrink-0 font-mono">
          {step.step_order}
        </span>
        <Badge type={step.step_type} />
        {step.step_type === 'search' && step.input_data?.queries && (
          <span className="text-xs text-gray-400">
            {step.input_data.queries.length} {step.input_data.queries.length === 1 ? 'query' : 'queries'}
          </span>
        )}
        {step.triggered_loop && (
          <span className="text-xs text-amber-600 font-medium">⚠ loop</span>
        )}
        <div className="ml-auto flex items-center gap-3">
          {step.duration_ms != null && (
            <span className="text-xs text-gray-400">{(step.duration_ms / 1000).toFixed(1)}s</span>
          )}
          <span className="text-gray-300 text-xs">{open ? '▲' : '▼'}</span>
        </div>
      </button>

      {open && (
        <div className="px-4 pb-4 border-t border-gray-100">
          <StepContent step={step} />
        </div>
      )}
    </div>
  )
}
