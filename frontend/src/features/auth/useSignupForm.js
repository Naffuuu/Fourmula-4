import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../context/ToastContext";
import { scorePassword } from "../../components/ui/PasswordStrengthMeter";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function useSignupForm() {
  const { signup } = useAuth();
  const { push } = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "student",
    roll_number: "",
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const setField = (field, value) => {
    setForm((f) => ({ ...f, [field]: value }));
    setErrors((e) => ({ ...e, [field]: undefined }));
  };

  const validate = () => {
    const next = {};
    if (!form.name.trim()) next.name = "Name is required.";
    if (!form.email.trim()) next.email = "Email is required.";
    else if (!EMAIL_RE.test(form.email)) next.email = "Enter a valid email address.";
    if (!form.password) next.password = "Password is required.";
    else if (scorePassword(form.password) < 2) next.password = "Choose a stronger password (8+ chars, mix of cases/numbers).";
    if (form.role === "student" && !form.roll_number.trim()) {
      next.roll_number = "Roll number is required for students.";
    }
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    try {
      await signup(form);
      push({ type: "success", message: `Welcome, ${form.name.split(" ")[0]}! Account created.` });
      navigate("/dashboard");
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (err.response?.status === 409) {
        setErrors((e) => ({ ...e, email: "An account with this email already exists." }));
      } else {
        push({ type: "error", message: detail || "Something went wrong creating your account." });
      }
    } finally {
      setSubmitting(false);
    }
  };

  return { form, setField, errors, submitting, submit };
}
