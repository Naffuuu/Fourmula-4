import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, ShieldAlert } from "lucide-react";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import GoogleOAuthButton from "../features/auth/GoogleOAuthButton";
import FacebookOAuthButton from "../features/auth/FacebookOAuthButton";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../context/ToastContext";

export default function LoginPage() {
  const { login } = useAuth();
  const { push } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname || "/dashboard";

  const goBack = () => {
    if (window.history.state?.idx > 0) {
      navigate(-1);
    } else {
      navigate("/", { replace: true });
    }
  };

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login({ email, password });
      navigate(redirectTo, { replace: true });
    } catch (err) {
      if (err.response?.status === 401) {
        setError("Incorrect email or password.");
      } else if (!err.response) {
        setError("Network error — check your connection and try again.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-between mb-6">
          <button
            type="button"
            onClick={goBack}
            className="inline-flex items-center gap-2 text-sm font-semibold text-primary-600 hover:text-primary-700 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>
          <div className="text-right text-xs text-ink-soft">
            Already have an account?
          </div>
        </div>

        <div className="flex flex-col items-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-primary-500 flex items-center justify-center shadow-soft mb-3 rotate-[4deg]">
            <ShieldAlert className="w-7 h-7 text-white" />
          </div>
          <h1 className="font-display text-2xl font-extrabold text-center">Welcome back</h1>
          <p className="text-ink-soft text-sm text-center mt-1">Log in to your Protocol account.</p>
        </div>

        <Card>
          <form onSubmit={submit} className="flex flex-col gap-4" noValidate>
            <Input
              label="Email address"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <div>
              <Input
                label="Password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={error || undefined}
              />
              <div className="text-right mt-1.5">
                <Link to="/forgot-password" className="text-xs font-semibold text-primary-600 hover:underline">
                  Forgot password?
                </Link>
              </div>
            </div>

            <Button type="submit" loading={submitting} className="w-full">
              Log in
            </Button>
          </form>

          <div className="flex items-center gap-3 my-5">
            <div className="h-px bg-primary-100 flex-1" />
            <span className="text-xs text-ink-faint uppercase tracking-wide">or</span>
            <div className="h-px bg-primary-100 flex-1" />
          </div>

          <div className="flex flex-col gap-2">
            <GoogleOAuthButton />
            <FacebookOAuthButton />
          </div>
        </Card>

        <p className="text-center text-sm text-ink-soft mt-5">
          New to the Protocol?{" "}
          <Link to="/signup" className="font-semibold text-primary-600 hover:underline">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
