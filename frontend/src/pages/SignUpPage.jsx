import { Link } from "react-router-dom";
import { ShieldAlert } from "lucide-react";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import PasswordStrengthMeter from "../components/ui/PasswordStrengthMeter";
import GoogleOAuthButton from "../features/auth/GoogleOAuthButton";
import FacebookOAuthButton from "../features/auth/FacebookOAuthButton";
import { useSignupForm } from "../features/auth/useSignupForm";

const ROLES = [
  { value: "student", label: "Student" },
  { value: "second_captain", label: "2nd Captain" },
  { value: "third_captain", label: "3rd Captain" },
  { value: "teacher", label: "Teacher" },
];

export default function SignUpPage() {
  const { form, setField, errors, submitting, submit } = useSignupForm();

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-coral-500 flex items-center justify-center shadow-soft mb-3 rotate-[-4deg]">
            <ShieldAlert className="w-7 h-7 text-white" />
          </div>
          <h1 className="font-display text-2xl font-extrabold text-center">Join the Protocol</h1>
          <p className="text-ink-soft text-sm text-center mt-1">
            Sign up to report abuses, dodge blind spots, and beat the syllabus.
          </p>
        </div>

        <Card>
          <form onSubmit={submit} className="flex flex-col gap-4" noValidate>
            <Input
              label="Full name"
              autoComplete="name"
              value={form.name}
              onChange={(e) => setField("name", e.target.value)}
              error={errors.name}
            />
            <Input
              label="Email address"
              type="email"
              autoComplete="email"
              value={form.email}
              onChange={(e) => setField("email", e.target.value)}
              error={errors.email}
            />
            <div>
              <Input
                label="Password"
                type="password"
                autoComplete="new-password"
                value={form.password}
                onChange={(e) => setField("password", e.target.value)}
                error={errors.password}
              />
              <PasswordStrengthMeter password={form.password} />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-ink-soft">I am a...</label>
              <div className="grid grid-cols-2 gap-2">
                {ROLES.map((r) => (
                  <button
                    type="button"
                    key={r.value}
                    onClick={() => setField("role", r.value)}
                    className={`rounded-xl border-2 px-3 py-2 text-sm font-semibold transition-colors ${
                      form.role === r.value
                        ? "border-primary-500 bg-primary-50 text-primary-700"
                        : "border-primary-100 text-ink-soft hover:border-primary-200"
                    }`}
                  >
                    {r.label}
                  </button>
                ))}
              </div>
            </div>

            {form.role === "student" && (
              <Input
                label="Roll number"
                value={form.roll_number}
                onChange={(e) => setField("roll_number", e.target.value)}
                error={errors.roll_number}
                hint="Hashed with a server-side pepper — never stored in plaintext, never shown to anyone."
              />
            )}

            <Button type="submit" loading={submitting} className="w-full mt-1">
              Create account
            </Button>
          </form>

          <div className="flex items-center gap-3 my-5">
            <div className="h-px bg-primary-100 flex-1" />
            <span className="text-xs text-ink-faint uppercase tracking-wide">or</span>
            <div className="h-px bg-primary-100 flex-1" />
          </div>

          <div className="flex flex-col gap-2">
            <GoogleOAuthButton label="Sign up with Google" />
            <FacebookOAuthButton label="Sign up with Facebook" />
          </div>
        </Card>

        <p className="text-center text-sm text-ink-soft mt-5">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-primary-600 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
