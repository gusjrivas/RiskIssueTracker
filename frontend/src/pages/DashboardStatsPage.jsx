import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import AppHeader from '../components/AppHeader'
import SeverityMatrixGrid from '../components/SeverityMatrixGrid'
import StatusBarChart from '../components/StatusBarChart'
import { useDashboardStats } from '../hooks/useDashboardStats'
import { useSeverityGroups } from '../hooks/useSeverityGroups'

const RISK_STATUSES = ['open', 'in_progress', 'closed', 'derived']
const ISSUE_STATUSES = ['open', 'in_progress', 'closed']

export default function DashboardStatsPage() {
  const { data, loading, error } = useDashboardStats()
  const { data: severityGroups, loading: groupsLoading, error: groupsError, fetchGroups } = useSeverityGroups()

  return (
    <div className="min-h-screen bg-canvas">
      <AppHeader />

      <main className="max-w-5xl mx-auto px-6 py-10">
        <div className="mb-8">
          <h2 className="font-display text-3xl font-bold">Dashboard</h2>
          <p className="text-muted text-sm mt-1">
            {data ? `${data.risks.total} riesgos · ${data.issues.total} issues` : ' '}
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <Loader2 size={24} className="animate-spin text-muted" />
          </div>
        ) : error ? (
          <div className="text-center py-16 text-muted text-sm">{error}</div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="space-y-6"
          >
            <section className="card">
              <h3 className="font-display font-semibold text-sm mb-4">
                Severidad por proximidad y zona de exposición
              </h3>
              <SeverityMatrixGrid
                risksBySeverity={data.risks.by_severity}
                issuesBySeverity={data.issues.by_severity}
                groups={severityGroups}
                groupsLoading={groupsLoading}
                groupsError={groupsError}
                onOpenDrawer={fetchGroups}
              />
            </section>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <section className="card">
                <StatusBarChart
                  title="Riesgos por estado"
                  byStatus={data.risks.by_status}
                  statuses={RISK_STATUSES}
                />
              </section>
              <section className="card">
                <StatusBarChart
                  title="Issues por estado"
                  byStatus={data.issues.by_status}
                  statuses={ISSUE_STATUSES}
                />
              </section>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  )
}
