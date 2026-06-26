import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "./hooks/useAuth";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import AuthPage from "./pages/AuthPage";
import DashboardPage from "./pages/DashboardPage";
import UploadPage from "./pages/UploadPage";
import ProcessingPage from "./pages/ProcessingPage";
import ReportPage from "./pages/ReportPage";
import PortfolioPage from "./pages/PortfolioPage";

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />
      <main>{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" toastOptions={{
          style: { background: "#1f2937", color: "#f9fafb", border: "1px solid #374151" }
        }}/>
        <Routes>
          <Route path="/login" element={<AuthPage />} />
          <Route path="/" element={<ProtectedRoute><Layout><DashboardPage /></Layout></ProtectedRoute>} />
          <Route path="/upload" element={<ProtectedRoute><Layout><UploadPage /></Layout></ProtectedRoute>} />
          <Route path="/portfolio" element={<ProtectedRoute><Layout><PortfolioPage /></Layout></ProtectedRoute>} />
          <Route path="/projects/:projectId" element={<ProtectedRoute><Layout><ProcessingPage /></Layout></ProtectedRoute>} />
          <Route path="/projects/:projectId/report" element={<ProtectedRoute><Layout><ReportPage /></Layout></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
