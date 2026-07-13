import { useState } from "react";
import { Paperclip, Send } from "lucide-react";
import PageWrapper from "../../components/layout/PageWrapper";
import Card, { CardHeader } from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import api from "../../lib/apiClient";
import { useToast } from "../../context/ToastContext";

const CATEGORIES = [
  { value: "tiffin_theft", label: "Tiffin Theft" },
  { value: "bribes", label: "Bribes" },
  { value: "syllabus_bloat", label: "Syllabus Bloat" },
  { value: "sports_abuse", label: "Sports Abuse" },
  { value: "seating_abuse", label: "Seating Abuse" },
];

export default function WhistleblowerPage() {
  const { push } = useToast();
  const [category, setCategory] = useState(CATEGORIES[0].value);
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    if (description.trim().length < 10) {
      push({ type: "error", message: "Please add a bit more detail (10+ characters)." });
      return;
    }
    setSubmitting(true);
    try {
      let evidence_upload_id;
      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        const uploadResp = await api.post("/complaints/evidence", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        evidence_upload_id = uploadResp.data.upload_id;
      }

      const { data } = await api.post("/complaints", { category, description, evidence_upload_id });
      setSubmitted(data);
      setDescription("");
      setFile(null);
      push({ type: "success", message: "Complaint filed anonymously. Your identity is never attached to it." });
    } catch (err) {
      push({ type: "error", message: err.response?.data?.detail || "Could not submit complaint. Try again." });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <PageWrapper maxWidth="max-w-2xl">
      <h1 className="font-display text-2xl font-extrabold mb-1">Anonymous Whistleblower</h1>
      <p className="text-ink-soft mb-6">
        File a complaint with no personally identifying information attached — ever.
      </p>

      <Card>
        <CardHeader title="Report an incident" />
        <form onSubmit={submit} className="flex flex-col gap-4">
          <div>
            <label className="text-sm font-medium text-ink-soft mb-1.5 block">Category</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {CATEGORIES.map((c) => (
                <button
                  type="button"
                  key={c.value}
                  onClick={() => setCategory(c.value)}
                  className={`rounded-xl border-2 px-3 py-2 text-xs font-semibold transition-colors ${
                    category === c.value
                      ? "border-coral-500 bg-coral-50 text-coral-700"
                      : "border-primary-100 text-ink-soft hover:border-primary-200"
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label htmlFor="description" className="text-sm font-medium text-ink-soft mb-1.5 block">
              What happened?
            </label>
            <textarea
              id="description"
              rows={5}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded-xl border-2 border-primary-100 bg-paper-soft px-4 py-2.5 text-sm focus:border-primary-500 focus:bg-paper-card focus:outline-none"
              placeholder="Describe what happened, when, and where — no names needed."
            />
          </div>

          <div className="flex items-center gap-3">
            <label className="inline-flex items-center gap-2 text-sm font-medium text-primary-600 cursor-pointer">
              <Paperclip className="w-4 h-4" />
              {file ? file.name : "Attach photo evidence (optional)"}
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </label>
          </div>
          <p className="text-xs text-ink-faint -mt-2">
            Photos are automatically stripped of GPS/device metadata before storage.
          </p>

          <Button type="submit" icon={Send} loading={submitting} className="w-full">
            Submit anonymously
          </Button>
        </form>
      </Card>

      {submitted && (
        <Card className="mt-6">
          <CardHeader
            title="Filed"
            action={<Badge tone="warning">{submitted.status.replace("_", " ")}</Badge>}
          />
          <p className="text-sm text-ink-soft">{submitted.description}</p>
        </Card>
      )}
    </PageWrapper>
  );
}
