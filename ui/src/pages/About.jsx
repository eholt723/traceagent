import { Link } from 'react-router-dom'

const PIPELINE_STEPS = [
  {
    label: 'Planner',
    desc: 'The agent reads your question and breaks it into 2–4 focused sub-questions to search for separately.',
  },
  {
    label: 'Search',
    desc: 'Each sub-question is sent to a live web search API. Real sources, not cached knowledge.',
  },
  {
    label: 'Reflection',
    desc: 'The agent evaluates whether the results are good enough. If not, it loops back and searches again — up to 3 rounds.',
  },
  {
    label: 'Synthesis',
    desc: 'A final report is written with inline citations, pulled from everything found across all search rounds.',
  },
]

const ACHIEVEMENTS = [
  'Full reasoning trace visible to the user — planner, search, reflection, and synthesis steps logged individually',
  'Reflection loop is explicit: the agent decides when results are insufficient and triggers another search round',
  'Real-time step streaming via WebSocket — watch the pipeline execute live, step by step',
  'Fork any past run with a modified query; compare two runs side by side with a step-level diff',
  'Public activity wall: all runs are visible to all users with attribution',
  'Pipeline stats dashboard: success rate, avg duration, reflection loop rate, step counts',
  'CloudWatch custom metrics and structured log shipping from EC2 to AWS (6 metrics, log group)',
  'Deployed two ways: Docker container on HuggingFace Spaces, and EC2 + RDS + systemd on AWS',
  '20 unit tests with pytest covering all API routes and agent logic; all external calls mocked (SQLite in-memory, patched LLM and search) — no API keys required; 73% coverage enforced and CI runs on every push via GitHub Actions',
]

const STACK = [
  { name: 'FastAPI', role: 'Python backend, async API routes' },
  { name: 'React', role: 'Frontend UI with Vite' },
  { name: 'PostgreSQL', role: 'Run and step storage (AWS RDS)' },
  { name: 'SQLAlchemy', role: 'ORM and query layer' },
  { name: 'Groq', role: 'LLM inference (llama-3.3-70b)' },
  { name: 'Tavily', role: 'Live web search API' },
  { name: 'WebSockets', role: 'Real-time step streaming' },
  { name: 'AWS EC2', role: 'Production server (systemd)' },
  { name: 'AWS RDS', role: 'Managed PostgreSQL database' },
  { name: 'CloudWatch', role: 'Logs and custom metrics' },
  { name: 'Docker', role: 'HuggingFace Spaces deployment' },
  { name: 'Pydantic', role: 'Schema-first data validation' },
]

export default function About() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <header className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 sticky top-0 z-40">
        <div className="max-w-3xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link
            to="/"
            className="font-semibold text-gray-900 dark:text-gray-100 text-lg tracking-tight hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors"
          >
            TraceAgent
          </Link>
          <Link
            to="/"
            className="text-sm font-medium text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            Open App
          </Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-12 space-y-14">

        {/* Hero */}
        <section>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-3">
            TraceAgent
          </h1>
          <p className="text-base text-gray-600 dark:text-gray-400 leading-relaxed">
            TraceAgent is a research assistant that shows its work. Most AI tools give you an
            answer and hide how they got there. TraceAgent exposes the full reasoning
            process — every search query, every decision the model makes, and every time it
            decides the results aren't good enough and tries again.
          </p>
          <p className="text-base text-gray-600 dark:text-gray-400 leading-relaxed mt-3">
            Built to demonstrate how agentic AI systems actually behave internally, with
            real-time observability, a public activity feed, and full AWS production deployment.
          </p>
        </section>

        {/* Pipeline */}
        <section>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
            How It Works
          </h2>
          <div className="space-y-0">
            {PIPELINE_STEPS.map((step, i) => (
              <div key={step.label} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-cyan-600 text-white flex items-center justify-center text-sm font-bold shrink-0">
                    {i + 1}
                  </div>
                  {i < PIPELINE_STEPS.length - 1 && (
                    <div className="w-px flex-1 bg-gray-200 dark:bg-gray-700 my-1" />
                  )}
                </div>
                <div className="pb-6">
                  <p className="text-sm font-semibold text-gray-900 dark:text-gray-100 mt-1">{step.label}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Achievements */}
        <section>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            What Was Built
          </h2>
          <ul className="space-y-2">
            {ACHIEVEMENTS.map((item) => (
              <li key={item} className="flex gap-2 text-sm text-gray-600 dark:text-gray-400">
                <span className="text-cyan-500 shrink-0 mt-0.5">&#10003;</span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* Tech Stack */}
        <section>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Tech Stack
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {STACK.map((tech) => (
              <div
                key={tech.name}
                className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4"
              >
                <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">{tech.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{tech.role}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Links */}
        <section className="flex flex-wrap gap-3">
          <Link
            to="/"
            className="bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-medium px-5 py-2.5 rounded-lg transition-colors"
          >
            Try the App
          </Link>
          <a
            href="https://github.com/eholt723/traceagent"
            target="_blank"
            rel="noopener noreferrer"
            className="border border-gray-300 dark:border-gray-600 text-sm font-medium text-gray-700 dark:text-gray-300 px-5 py-2.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            View on GitHub
          </a>
        </section>

      </main>
    </div>
  )
}
