import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import RisksPage from './pages/RisksPage'
import RiskDetailPage from './pages/RiskDetailPage'
import IssuesPage from './pages/IssuesPage'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/projects/:projectId/risks" element={<ProtectedRoute><RisksPage /></ProtectedRoute>} />
        <Route path="/risks/:riskId" element={<ProtectedRoute><RiskDetailPage /></ProtectedRoute>} />
        <Route path="/issues/:issueId" element={<ProtectedRoute><IssuesPage /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}
