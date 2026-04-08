import { useEffect, useState } from "react";
import api from "../services/api";

function Recommendations({ websiteId, token }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (websiteId) {
      fetchRecommendations();
    }
  }, [websiteId]);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/recommendations/${websiteId}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setRecommendations(response.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Impossible de charger les recommandations");
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (recId) => {
    try {
      await api.put(
        `/recommendations/${recId}/read/`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setRecommendations(
        recommendations.map((rec) =>
          rec.id === recId ? { ...rec, is_read: true } : rec
        )
      );
    } catch (err) {
      console.error(err);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 1:
        return { bg: "#fee2e2", color: "#dc2626", border: "#fecaca" };
      case 2:
        return { bg: "#fef3c7", color: "#d97706", border: "#fde68a" };
      default:
        return { bg: "#d1fae5", color: "#059669", border: "#a7f3d0" };
    }
  };

  const getTypeIcon = (type) => {
    const icons = {
      ctr: "📊",
      position: "🎯",
      traffic: "🚗",
      bounce: "🔄",
      seo: "🤖",
    };
    return icons[type] || "💡";
  };

  const styles = {
    container: {
      background: "#fff",
      borderRadius: "16px",
      padding: "20px",
      marginTop: "20px",
      boxShadow: "0 6px 18px rgba(0,0,0,0.08)",
    },
    title: {
      fontSize: "20px",
      fontWeight: "bold",
      marginBottom: "15px",
      display: "flex",
      alignItems: "center",
      gap: "10px",
      flexWrap: "wrap",
    },
    card: {
      background: "#f9fafb",
      borderRadius: "12px",
      padding: "16px",
      marginBottom: "12px",
      border: "1px solid #e5e7eb",
      transition: "all 0.3s ease",
    },
    cardHeader: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      marginBottom: "10px",
      gap: "10px",
      flexWrap: "wrap",
    },
    cardTitle: {
      fontSize: "16px",
      fontWeight: "bold",
      display: "flex",
      alignItems: "center",
      gap: "8px",
    },
    priorityBadge: {
      padding: "4px 10px",
      borderRadius: "20px",
      fontSize: "11px",
      fontWeight: "bold",
    },
    description: {
      color: "#4b5563",
      fontSize: "14px",
      lineHeight: "1.5",
      marginBottom: "12px",
    },
    action: {
      background: "#f3f4f6",
      padding: "8px 12px",
      borderRadius: "8px",
      fontSize: "13px",
      color: "#1f2937",
      marginTop: "10px",
    },
    readButton: {
      background: "none",
      border: "none",
      cursor: "pointer",
      fontSize: "20px",
      padding: "5px",
    },
    emptyState: {
      textAlign: "center",
      padding: "40px",
      color: "#6b7280",
    },
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.title}>
          <span>🤖</span> Recommandations SEO IA
        </div>
        <p>Analyse des données en cours...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.title}>
          <span>🤖</span> Recommandations SEO IA
        </div>
        <p style={{ color: "#dc2626" }}>{error}</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.title}>
        <span>🤖</span> Recommandations SEO IA
        <span style={{ fontSize: "12px", color: "#6b7280" }}>
          ({recommendations.length} conseil
          {recommendations.length > 1 ? "s" : ""})
        </span>
      </div>

      {recommendations.length === 0 ? (
        <div style={styles.emptyState}>
          <p>✨ Aucune recommandation pour le moment.</p>
          <p style={{ fontSize: "13px" }}>
            Les données seront analysées automatiquement.
          </p>
        </div>
      ) : (
        recommendations.map((rec) => {
          const priorityStyle = getPriorityColor(rec.priority);
          return (
            <div
              key={rec.id}
              style={{
                ...styles.card,
                opacity: rec.is_read ? 0.6 : 1,
                borderLeft: `4px solid ${priorityStyle.color}`,
              }}
            >
              <div style={styles.cardHeader}>
                <div style={styles.cardTitle}>
                  <span>{getTypeIcon(rec.recommendation_type)}</span>
                  {rec.title}
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span
                    style={{
                      ...styles.priorityBadge,
                      background: priorityStyle.bg,
                      color: priorityStyle.color,
                    }}
                  >
                    {rec.priority_label}
                  </span>
                  {!rec.is_read && (
                    <button
                      style={styles.readButton}
                      onClick={() => markAsRead(rec.id)}
                      title="Marquer comme lu"
                    >
                      ✅
                    </button>
                  )}
                </div>
              </div>
              <p style={styles.description}>{rec.description}</p>
              {rec.action && (
                <div style={styles.action}>
                  <strong>🎯 Action recommandée :</strong> {rec.action}
                </div>
              )}
              <div style={{ fontSize: "11px", color: "#9ca3af", marginTop: "10px" }}>
                {new Date(rec.created_at).toLocaleDateString()}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}

export default Recommendations;
