import { useEffect, useState } from "react";
import api from "../services/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import Recommendations from "../components/Recommendations";
import { theme } from "../styles/theme";

function Dashboard() {
  const [url, setUrl] = useState("");
  const [nomSite, setNomSite] = useState("");
  const [sites, setSites] = useState([]);
  const [properties, setProperties] = useState([]);
  const [gaData, setGaData] = useState([]);
  const [seoData, setSeoData] = useState([]);
  const [loadingSeo, setLoadingSeo] = useState(false);
  const [selectedWebsiteId, setSelectedWebsiteId] = useState(null);
  const [selectedPropertyId, setSelectedPropertyId] = useState("");
  const [selectedPropertyName, setSelectedPropertyName] = useState("");

  const token = localStorage.getItem("access");

  const formattedChartData = gaData.map((item) => ({
    ...item,
    date: `${item.date.slice(6, 8)}/${item.date.slice(4, 6)}`,
    users: Number(item.users),
    sessions: Number(item.sessions),
    views: Number(item.views),
  }));

  const fetchSites = async () => {
    try {
      const response = await api.get("/sites/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setSites(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const fetchProperties = async () => {
    try {
      const response = await api.get("/google-analytics/properties/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setProperties(response.data);
    } catch (error) {
      console.error(error);
      alert(
        error.response?.data?.error ||
          "Impossible de recuperer les proprietes Google Analytics"
      );
    }
  };

  const fetchGAData = async (propertyId) => {
    try {
      const response = await api.get(`/google-analytics/data/${propertyId}/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setGaData(response.data);
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.error || "Erreur recuperation donnees GA");
    }
  };

  const fetchSearchConsole = async (siteUrl) => {
    if (!siteUrl) {
      alert("URL du site manquante");
      return;
    }

    setLoadingSeo(true);
    try {
      const response = await api.get(
        `/search-console/data/?site_url=${encodeURIComponent(siteUrl)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setSeoData(response.data);

      if (response.data.length === 0) {
        console.log("Aucune donnee Search Console pour ce site");
      }
    } catch (error) {
      console.error("Erreur Search Console:", error);
      alert(
        error.response?.data?.error ||
          "Erreur lors de la recuperation des donnees SEO"
      );
    }
    setLoadingSeo(false);
  };

  useEffect(() => {
    fetchSites();
  }, []);

  const handleAddSite = async (e) => {
    e.preventDefault();

    try {
      const verifyResponse = await api.post(
        "/google-analytics/verify-url/",
        {
          site_url: url,
          property_id: selectedPropertyId,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!verifyResponse.data.match) {
        alert(
          "La propriete Google Analytics choisie ne correspond pas a l'URL du site."
        );
        return;
      }

      await api.post(
        "/add-site/",
        {
          url: url,
          nom_site: nomSite,
          property_id: selectedPropertyId,
          property_name: selectedPropertyName,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setUrl("");
      setNomSite("");
      setSelectedPropertyId("");
      setSelectedPropertyName("");
      fetchSites();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.error || "Erreur lors de l'ajout du site");
    }
  };

  const handleGoogleAnalyticsConnect = async () => {
    try {
      const response = await api.get("/google-analytics/login/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error(error);
      alert(
        error.response?.data?.detail ||
          error.response?.data?.error ||
          "Erreur lors de la connexion a Google Analytics"
      );
    }
  };

  const handlePropertyChange = (e) => {
    const propertyId = e.target.value;
    setSelectedPropertyId(propertyId);

    const selectedProperty = properties.find(
      (prop) => prop.property_id === propertyId
    );

    setSelectedPropertyName(
      selectedProperty ? selectedProperty.display_name : ""
    );
  };

  const seoStyles = {
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
    },
    tableWrap: {
      overflowX: "auto",
    },
    table: {
      width: "100%",
      borderCollapse: "collapse",
      minWidth: "700px",
    },
    th: {
      textAlign: "left",
      padding: "12px",
      background: "#f3f4f6",
      fontWeight: "bold",
    },
    td: {
      padding: "12px",
      borderBottom: "1px solid #e5e7eb",
    },
    badge: {
      background: "#e5e7eb",
      padding: "4px 8px",
      borderRadius: "12px",
      fontSize: "12px",
    },
  };

  return (
    <div style={theme.page}>
      <div style={theme.container}>
        <div style={theme.dashboardCard}>
          <h2 style={{ marginBottom: "10px", fontWeight: "bold" }}>
            Dashboard SEO<span style={{ color: "#6366f1" }}>mind</span>
          </h2>
          <p style={{ color: "#6b7280" }}>
            Analyse intelligente de ton trafic web avec Google Analytics.
          </p>

          <div style={theme.rowButtons}>
            <button
              style={theme.secondaryButton}
              onClick={handleGoogleAnalyticsConnect}
            >
              Connecter Google Analytics
            </button>

            <button style={theme.secondaryButton} onClick={fetchProperties}>
              Charger proprietes GA
            </button>
          </div>
        </div>

        <div style={theme.dashboardCard}>
          <h3 style={theme.sectionTitle}>Ajouter un site</h3>

          <form onSubmit={handleAddSite}>
            <input
              style={theme.input}
              type="text"
              placeholder="URL du site"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />

            <input
              style={theme.input}
              type="text"
              placeholder="Nom du site"
              value={nomSite}
              onChange={(e) => setNomSite(e.target.value)}
            />

            <select
              style={theme.select}
              value={selectedPropertyId}
              onChange={handlePropertyChange}
            >
              <option value="">Choisir une propriete Google Analytics</option>
              {properties.map((prop) => (
                <option key={prop.property_id} value={prop.property_id}>
                  {prop.display_name} - {prop.property_id}
                </option>
              ))}
            </select>

            <button style={theme.button} type="submit">
              Ajouter site
            </button>
          </form>
        </div>

        <div style={theme.dashboardCard}>
          <h3 style={theme.sectionTitle}>Liste des sites</h3>

          {sites.length === 0 ? (
            <p>Aucun site enregistre</p>
          ) : (
            <div>
              {sites.map((site) => (
                <div key={site.id} style={theme.siteItem}>
                  <strong>{site.nom_site}</strong> - {site.url}
                  <br />
                  <span style={{ color: "#6b7280" }}>
                    Propriete GA : {site.property_name} ({site.property_id})
                  </span>
                  <br />
                  <br />
                  <button
                    style={theme.secondaryButton}
                    onClick={() => {
                      fetchGAData(site.property_id);
                      setSelectedWebsiteId(site.id);
                    }}
                  >
                    Voir stats GA
                  </button>
                  <button
                    style={{ ...theme.secondaryButton, marginLeft: "10px" }}
                    onClick={() => {
                      fetchSearchConsole(site.url);
                      setSelectedWebsiteId(site.id);
                    }}
                  >
                    Voir donnees SEO
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={theme.dashboardCard}>
          <h3 style={theme.sectionTitle}>Graphique d'evolution du trafic</h3>

          {formattedChartData.length === 0 ? (
            <p>Aucune donnee a afficher</p>
          ) : (
            <div style={{ width: "100%", height: "420px" }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formattedChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="users" name="Users" />
                  <Line type="monotone" dataKey="sessions" name="Sessions" />
                  <Line type="monotone" dataKey="views" name="Views" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div style={seoStyles.container}>
          <h3 style={seoStyles.title}>Donnees SEO (Google Search Console)</h3>

          {loadingSeo ? (
            <p>Chargement des donnees SEO...</p>
          ) : seoData.length === 0 ? (
            <p style={{ color: "#6b7280" }}>
              Aucune donnee SEO disponible pour ce site sur la periode
              selectionnee. {!loadingSeo &&
                " Verifiez que votre site est bien enregistre dans Google Search Console."}
            </p>
          ) : (
            <div style={seoStyles.tableWrap}>
              <table style={seoStyles.table}>
                <thead>
                  <tr>
                    <th style={seoStyles.th}>Mot-cle</th>
                    <th style={seoStyles.th}>Clics</th>
                    <th style={seoStyles.th}>Impressions</th>
                    <th style={seoStyles.th}>CTR</th>
                    <th style={seoStyles.th}>Position</th>
                  </tr>
                </thead>
                <tbody>
                  {seoData.map((row, index) => (
                    <tr key={index}>
                      <td style={seoStyles.td}>
                        <strong>{row.keyword}</strong>
                      </td>
                      <td style={seoStyles.td}>{row.clicks}</td>
                      <td style={seoStyles.td}>{row.impressions}</td>
                      <td style={seoStyles.td}>
                        <span style={seoStyles.badge}>
                          {(row.ctr * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td style={seoStyles.td}>
                        <span
                          style={{
                            ...seoStyles.badge,
                            background:
                              row.position <= 5 ? "#d1fae5" : "#fef3c7",
                          }}
                        >
                          {row.position.toFixed(1)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {selectedWebsiteId && (
          <Recommendations websiteId={selectedWebsiteId} token={token} />
        )}
      </div>
    </div>
  );
}

export default Dashboard;
