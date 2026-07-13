import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./routes/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import DashboardPage from "./pages/DashboardPage";
import WhistleblowerPage from "./features/whistleblower/WhistleblowerPage";
import SeatingPage from "./features/seating/SeatingPage";
import SyllabusPage from "./features/syllabus/SyllabusPage";
import LedgerPage from "./features/ledger/LedgerPage";
import SosPage from "./features/sos/SosPage";
import FactCheckerPage from "./features/factchecker/FactCheckerPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/missions/whistleblower" element={<WhistleblowerPage />} />
          <Route path="/missions/syllabus" element={<SyllabusPage />} />
          <Route path="/missions/ledger" element={<LedgerPage />} />
          <Route path="/missions/sos" element={<SosPage />} />
          <Route path="/missions/factchecker" element={<FactCheckerPage />} />
          <Route path="/missions/seating" element={<SeatingPage />} />
        </Route>

        <Route element={<ProtectedRoute allowedRoles={["second_captain", "third_captain"]} />}>
          <Route path="/missions/seating" element={<SeatingPage />} />
        </Route>

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
