import { useState } from "react";
import { ShieldCheck, ShieldX, Search } from "lucide-react";
import PageWrapper from "../../components/layout/PageWrapper";
import Card, { CardHeader } from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import ProgressBar from "../../components/ui/ProgressBar";
import api from "../../lib/apiClient";
import { useToast } from "../../context/ToastContext";

export default function FactCheckerPage() {
  const { push } = useToast();
  const [claim, setClaim] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    if (claim.trim().length < 3) {
      push({ type: "error", message: "Type the rule or claim you want checked." });
      return;
    }
    setSubmitting(true);
    setResult(null);
    try {
      const { data } = await api.post("/factcheck", { claim });
      setResult(data);
    } catch (err) {
      if (err.response?.status === 503) {
        push({ type: "error", message: "Rulebook hasn't been seeded on the server yet." });
      } else {
        push({ type: "error", message: "Could not check that claim right now." });
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <PageWrapper maxWidth="max-w-2xl">
      <h1 className="font-display text-2xl font-extrabold mb-1">Kuddus Fact-Checker</h1>
      <p className="text-ink-soft mb-6">
        Check a rule Kuddus claims exists against the actual seeded rulebook.
      </p>

      <Card className="mb-6">
        <CardHeader title="Check a claim" />
        <form onSubmit={submit} className="flex flex-col gap-4">
          <textarea
            rows={3}
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            className="w-full rounded-xl border-2 border-primary-100 bg-paper-soft px-4 py-2.5 text-sm focus:border-primary-500 focus:bg-paper-card focus:outline-none"
            placeholder='e.g. "He says we have to pay for our own seats now"'
          />
          <Button type="submit" icon={Search} loading={submitting} className="w-full">
            Check against rulebook
          </Button>
        </form>
      </Card>

      {result && (
        <Card className="animate-pop-in">
          <div className="flex items-center gap-3 mb-4">
            {result.verdict ? (
              <Badge tone="success" icon={ShieldCheck} className="text-sm px-3 py-1.5">
                TRUE
              </Badge>
            ) : (
              <Badge tone="danger" icon={ShieldX} className="text-sm px-3 py-1.5">
                FALSE / UNCORROBORATED
              </Badge>
            )}
          </div>

          <ProgressBar
            value={Math.round(result.confidence * 100)}
            max={100}
            tone={result.verdict ? "success" : "danger"}
            label="Confidence"
            className="mb-4"
          />

          <blockquote className="border-l-4 border-primary-200 pl-4 py-1 text-sm text-ink-soft italic">
            "{result.matched_rule_text}"
          </blockquote>
          <p className="text-xs text-ink-faint mt-2">— {result.source_section}</p>
        </Card>
      )}
    </PageWrapper>
  );
}
