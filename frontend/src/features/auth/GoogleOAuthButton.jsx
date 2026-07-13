import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../context/ToastContext";
import { useNavigate } from "react-router-dom";

/**
 * Renders Google's real branded button via GIS, gets back an ID token
 * (JWT signed by Google), and hands it to our backend at /oauth/google for
 * server-side verification (see oauth_service.py — we never trust the token
 * on the frontend, only Google's own verification on our server).
 */
export default function GoogleOAuthButton({ label = "Continue with Google" }) {
  const { loginWithOAuth } = useAuth();
  const { push } = useToast();
  const navigate = useNavigate();

  return (
    <GoogleLogin
      width="100%"
      text={label.startsWith("Continue") ? "continue_with" : "signin_with"}
      shape="pill"
      onSuccess={async (credentialResponse) => {
        try {
          await loginWithOAuth("google", credentialResponse.credential);
          navigate("/dashboard");
        } catch (err) {
          push({
            type: "error",
            message:
              err.response?.data?.detail ||
              "Google sign-in failed. Please try again or use email/password.",
          });
        }
      }}
      onError={() => {
        push({ type: "error", message: "Google sign-in was cancelled or failed." });
      }}
      useOneTap={false}
    />
  );
}
