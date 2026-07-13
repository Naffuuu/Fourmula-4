import { useState } from "react";
import { Link } from "react-router-dom";
import { MailCheck } from "lucide-react";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import api from "../lib/apiClient";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post("/auth/forgot-password", { email });
    } finally {
      // Always show the same "sent" state regardless of whether the email
      // exists, so this endpoint can't be used to enumerate accounts.
      setSubmitting(false);
      setSent(true);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <Card>
          {sent ? (
            <div className="text-center py-4">
              <MailCheck className="w-10 h-10 text-success-500 mx-auto mb-3" />
              <h2 className="font-display text-lg font-semibold">Check your inbox</h2>
              <p className="text-sm text-ink-soft mt-1">
                If an account exists for <strong>{email}</strong>, a reset link is on its way. In
                local dev without an email provider configured, the link is printed to the backend
                console instead.
              </p>
            </div>
          ) : (
            <form onSubmit={submit} className="flex flex-col gap-4">
              <div>
                <h1 className="font-display text-xl font-bold mb-1">Reset your password</h1>
                <p className="text-sm text-ink-soft">
                  Enter your email and we'll send a link to reset your password.
                </p>
              </div>
              <Input
                label="Email address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Button type="submit" loading={submitting} className="w-full">
                Send reset link
              </Button>
            </form>
          )}
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
