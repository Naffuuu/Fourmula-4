import { useEffect, useState } from "react";
import { Facebook, Loader2 } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../context/ToastContext";
import { useNavigate } from "react-router-dom";
import Button from "../../components/ui/Button";

const FB_APP_ID = import.meta.env.VITE_FACEBOOK_APP_ID;

let sdkLoadPromise = null;

/**
 * Lazily loads the Facebook JS SDK once, then exposes window.FB.login().
 * We only ever send the resulting access token to our backend, which
 * verifies it server-side against the Graph API (see oauth_service.py) —
 * the frontend never decides "this user is authenticated" on its own.
 */
function loadFacebookSdk() {
  if (sdkLoadPromise) return sdkLoadPromise;

  sdkLoadPromise = new Promise((resolve, reject) => {
    if (!FB_APP_ID) {
      reject(new Error("VITE_FACEBOOK_APP_ID is not configured"));
      return;
    }
    window.fbAsyncInit = function () {
      window.FB.init({ appId: FB_APP_ID, cookie: true, xfbml: false, version: "v20.0" });
      resolve(window.FB);
    };
    const script = document.createElement("script");
    script.src = "https://connect.facebook.net/en_US/sdk.js";
    script.async = true;
    script.defer = true;
    script.onerror = () => reject(new Error("Failed to load Facebook SDK"));
    document.body.appendChild(script);
  });

  return sdkLoadPromise;
}

export default function FacebookOAuthButton({ label = "Continue with Facebook" }) {
  const { loginWithOAuth } = useAuth();
  const { push } = useToast();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [sdkError, setSdkError] = useState(false);

  useEffect(() => {
    loadFacebookSdk().catch(() => setSdkError(true));
  }, []);

  const handleClick = async () => {
    setLoading(true);
    try {
      const FB = await loadFacebookSdk();
      const response = await new Promise((resolve) =>
        FB.login(resolve, { scope: "public_profile,email" })
      );

      if (response.status !== "connected") {
        push({ type: "error", message: "Facebook sign-in was cancelled." });
        return;
      }

      await loginWithOAuth("facebook", response.authResponse.accessToken);
      navigate("/dashboard");
    } catch (err) {
      push({
        type: "error",
        message:
          err.response?.data?.detail ||
          (sdkError
            ? "Facebook login isn't configured for this environment."
            : "Facebook sign-in failed. Please try again or use email/password."),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      type="button"
      variant="outline"
      className="w-full !border-[#1877F2] !text-[#1877F2] hover:!bg-[#1877F2]/5"
      icon={loading ? Loader2 : Facebook}
      loading={loading}
      onClick={handleClick}
    >
      {label}
    </Button>
  );
}
