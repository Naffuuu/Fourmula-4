import { useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { KeyRound } from "lucide-react";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import PasswordStrengthMeter from "../components/ui/PasswordStrengthMeter";
import api from "../lib/apiClient";
import { useToast } from "../context/ToastContext";

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const navigate = useNavigate();
  const { push } = useToast();

  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!token) {
      push({ type: "error", message: "This reset link is missing its token." });
      return;
    }
    setSubmitting(true);
    try {
      await api.post("/auth/reset-password", { token, new_password: password });
      push({ type: "success", message: "Password reset. Please log in." });
      navigate("/login");
    } catch (err) {
      push({ type: "error", message: err.response?.data?.detail || "This reset link is invalid or expired." });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-primary-500 flex items-center justify-center shadow-soft mb-3">
            <KeyRound className="w-7 h-7 text-white" />
          </div>
          <h1 className="font-display text-2xl font-extrabold text-center">Choose a new password</h1>
        </div>

        <Card>
          <form onSubmit={submit} className="flex flex-col gap-4">
            <div>
              <Input
                label="New password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <PasswordStrengthMeter password={password} />
            </div>
            <Button type="submit" loading={submitting} className="w-full">
              Reset password
            </Button>
          </form>
        </Card>

        <p className="text-center text-sm text-ink-soft mt-5">
          <Link to="/login" className="font-semibold text-primary-600 hover:underline">
            Back to log in
          </Link>
        </p>
      </div>
    </div>
  );
}
