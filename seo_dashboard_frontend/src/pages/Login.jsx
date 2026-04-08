import { useEffect, useRef, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";
import loginImg from "../assets/login.png";

function Login() {
  const [form, setForm] = useState({
    username: "",
    password: "",
  });
  const [googleError, setGoogleError] = useState("");

  const googleBtnRef = useRef(null);
  const navigate = useNavigate();
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  const handleGoogleResponse = async (response) => {
    try {
      const res = await api.post("/auth/google/", {
        credential: response.credential,
      });

      localStorage.setItem("access", res.data.access);
      localStorage.setItem("refresh", res.data.refresh);
      localStorage.setItem("user", JSON.stringify(res.data.user));

      alert("Connexion Google reussie");
      navigate("/dashboard");
    } catch (error) {
      console.error(error);
      alert(
        error.response?.data?.error ||
          error.response?.data?.detail ||
          "Erreur Google login"
      );
    }
  };

  useEffect(() => {
    if (!googleClientId) {
      setGoogleError("Configuration Google manquante.");
      return;
    }

    let cancelled = false;

    const renderGoogleButton = () => {
      if (cancelled || !window.google || !googleBtnRef.current) {
        return false;
      }

      googleBtnRef.current.innerHTML = "";

      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: handleGoogleResponse,
      });

      window.google.accounts.id.renderButton(googleBtnRef.current, {
        theme: "outline",
        size: "large",
        width: 320,
        text: "continue_with",
        shape: "rectangular",
      });

      setGoogleError("");
      return true;
    };

    if (renderGoogleButton()) {
      return () => {
        cancelled = true;
      };
    }

    const existingScript = document.querySelector(
      'script[src="https://accounts.google.com/gsi/client"]'
    );

    const handleScriptLoad = () => {
      if (!renderGoogleButton()) {
        setGoogleError("Impossible de charger Google Sign-In.");
      }
    };

    if (existingScript) {
      existingScript.addEventListener("load", handleScriptLoad);
    }

    const timeoutId = window.setTimeout(() => {
      if (!renderGoogleButton()) {
        setGoogleError("Impossible de charger Google Sign-In.");
      }
    }, 1500);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
      existingScript?.removeEventListener("load", handleScriptLoad);
    };
  }, [googleClientId]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await api.post("/auth/login/", form);

      localStorage.setItem("access", response.data.access);
      localStorage.setItem("refresh", response.data.refresh);
      localStorage.setItem("user", JSON.stringify(response.data.user));

      navigate("/dashboard");
    } catch (error) {
      console.error(error);
      alert(
        error.response?.data?.detail ||
          error.response?.data?.error ||
          "Erreur de connexion"
      );
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.wrapper}>
        <div style={styles.right}>
          <img src={loginImg} alt="SEOmind login visual" style={styles.image} />
        </div>
        <div style={styles.left}>
          <div style={styles.formBox}>
            <h2 style={styles.title}>Connexion</h2>
            <p style={styles.subtitle}>Accede a ton dashboard SEOmind.</p>

            <form onSubmit={handleSubmit}>
              <input
                style={styles.input}
                type="text"
                name="username"
                placeholder="Nom d'utilisateur"
                value={form.username}
                onChange={handleChange}
              />

              <input
                style={styles.input}
                type="password"
                name="password"
                placeholder="Mot de passe"
                value={form.password}
                onChange={handleChange}
              />

              <button style={styles.button} type="submit">
                Se connecter
              </button>
            </form>

            <div style={styles.separator}>Ou</div>

            <div
              ref={googleBtnRef}
              style={{ display: "flex", justifyContent: "center" }}
            />
            {googleError && <p style={styles.googleError}>{googleError}</p>}

            <p style={styles.linkText}>
              <Link to="/forgot-password">Mot de passe oublie ?</Link>
            </p>

            <p style={styles.linkText}>
              Pas de compte ? <Link to="/register">S'inscrire</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;

const styles = {
  page: {
    minHeight: "100vh",
    background: "#f5f7fb",
    padding: "110px 30px 30px",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    boxSizing: "border-box",
  },
  wrapper: {
    width: "100%",
    maxWidth: "1200px",
    minHeight: "650px",
    background: "#ffffff",
    borderRadius: "24px",
    overflow: "hidden",
    boxShadow: "0 15px 40px rgba(0,0,0,0.10)",
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
  },
  left: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "40px",
  },
  formBox: {
    width: "100%",
    maxWidth: "380px",
  },
  right: {
    background: "linear-gradient(#ffffff)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "30px",
  },
  image: {
    width: "100%",
    maxWidth: "500px",
    objectFit: "contain",
  },
  title: {
    fontSize: "32px",
    fontWeight: "bold",
    marginBottom: "10px",
    color: "#111827",
    textAlign: "center",
  },
  subtitle: {
    color: "#6b7280",
    marginBottom: "24px",
    textAlign: "center",
    fontSize: "16px",
  },
  input: {
    width: "100%",
    padding: "14px 16px",
    borderRadius: "12px",
    border: "1px solid #d1d5db",
    marginBottom: "14px",
    fontSize: "15px",
    outline: "none",
    boxSizing: "border-box",
  },
  button: {
    width: "100%",
    background: "#0f172a",
    color: "#fff",
    border: "none",
    padding: "14px 16px",
    borderRadius: "12px",
    fontWeight: "bold",
    cursor: "pointer",
    fontSize: "15px",
  },
  separator: {
    margin: "22px 0",
    textAlign: "center",
    color: "#6b7280",
    fontSize: "16px",
  },
  linkText: {
    marginTop: "16px",
    textAlign: "center",
  },
  googleError: {
    marginTop: "12px",
    color: "#b91c1c",
    fontSize: "14px",
    textAlign: "center",
  },
};
