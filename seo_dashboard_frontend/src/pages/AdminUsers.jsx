import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { theme } from "../styles/theme";

function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    is_active: true,
  });

  const token = localStorage.getItem("access");
  const navigate = useNavigate();

  const userStr = localStorage.getItem("user");
  const currentUser = userStr ? JSON.parse(userStr) : null;
  const isSuperUser = currentUser?.is_superuser || false;

  useEffect(() => {
    if (!isSuperUser) {
      navigate("/dashboard");
      return;
    }
    fetchUsers();
  }, [isSuperUser]);

  const fetchUsers = async () => {
    try {
      const response = await api.get("/auth/admin/users/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUsers(response.data);
    } catch (error) {
      console.error(error);
      alert("Erreur lors du chargement des utilisateurs");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await api.post("/auth/admin/users/create/", formData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert("Utilisateur cree avec succes");
      setShowModal(false);
      setEditingUser(null);
      setFormData({
        username: "",
        email: "",
        password: "",
        first_name: "",
        last_name: "",
        is_active: true,
      });
      fetchUsers();
    } catch (error) {
      alert(error.response?.data?.error || "Erreur lors de la creation");
    }
  };

  const handleToggleActive = async (user) => {
    try {
      await api.put(
        `/auth/admin/users/${user.id}/update/`,
        { is_active: !user.is_active },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchUsers();
    } catch (error) {
      alert(error.response?.data?.error || "Erreur lors de la modification");
    }
  };

  const handleDeleteUser = async (user) => {
    if (window.confirm(`Supprimer definitivement ${user.username} ?`)) {
      try {
        await api.delete(`/auth/admin/users/${user.id}/delete/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        alert("Utilisateur supprime");
        fetchUsers();
      } catch (error) {
        alert(error.response?.data?.error || "Erreur lors de la suppression");
      }
    }
  };

  const styles = {
    page: {
      ...theme.page,
      background: "#f5f7fb",
    },
    container: {
      maxWidth: "1400px",
      margin: "0 auto",
    },
    header: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      marginBottom: "30px",
      gap: "16px",
      flexWrap: "wrap",
    },
    title: {
      fontSize: "28px",
      fontWeight: "bold",
      color: "#111827",
      margin: 0,
    },
    addButton: {
      background: "#6366f1",
      color: "#fff",
      border: "none",
      padding: "12px 24px",
      borderRadius: "10px",
      cursor: "pointer",
      fontWeight: "bold",
    },
    tableWrap: {
      overflowX: "auto",
      borderRadius: "16px",
      boxShadow: "0 6px 18px rgba(0,0,0,0.08)",
      background: "#fff",
    },
    table: {
      width: "100%",
      borderCollapse: "collapse",
      minWidth: "900px",
    },
    th: {
      background: "#f3f4f6",
      padding: "15px",
      textAlign: "left",
      fontWeight: "bold",
    },
    td: {
      padding: "15px",
      borderBottom: "1px solid #e5e7eb",
      verticalAlign: "middle",
    },
    activeBadge: {
      background: "#10b981",
      color: "#fff",
      padding: "5px 10px",
      borderRadius: "20px",
      fontSize: "12px",
    },
    inactiveBadge: {
      background: "#ef4444",
      color: "#fff",
      padding: "5px 10px",
      borderRadius: "20px",
      fontSize: "12px",
    },
    adminBadge: {
      background: "#6366f1",
      color: "#fff",
      padding: "5px 10px",
      borderRadius: "20px",
      fontSize: "12px",
    },
    actionButton: {
      background: "none",
      border: "none",
      cursor: "pointer",
      fontSize: "18px",
      margin: "0 5px",
    },
    modalOverlay: {
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: "rgba(0,0,0,0.5)",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      zIndex: 1000,
      padding: "20px",
    },
    modal: {
      background: "#fff",
      borderRadius: "20px",
      padding: "30px",
      width: "500px",
      maxWidth: "90%",
    },
    input: {
      width: "100%",
      padding: "12px",
      marginBottom: "15px",
      borderRadius: "8px",
      border: "1px solid #d1d5db",
      boxSizing: "border-box",
    },
    buttonRow: {
      display: "flex",
      gap: "10px",
      flexWrap: "wrap",
    },
    empty: {
      ...theme.dashboardCard,
      textAlign: "center",
    },
  };

  if (!isSuperUser) return null;

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <div style={styles.header}>
          <h1 style={styles.title}>Administration des utilisateurs</h1>
          <button style={styles.addButton} onClick={() => setShowModal(true)}>
            + Ajouter un utilisateur
          </button>
        </div>

        {loading ? (
          <p>Chargement...</p>
        ) : users.length === 0 ? (
          <div style={styles.empty}>Aucun utilisateur trouve.</div>
        ) : (
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>ID</th>
                  <th style={styles.th}>Nom d'utilisateur</th>
                  <th style={styles.th}>Email</th>
                  <th style={styles.th}>Role</th>
                  <th style={styles.th}>Statut</th>
                  <th style={styles.th}>Date d'inscription</th>
                  <th style={styles.th}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td style={styles.td}>{user.id}</td>
                    <td style={styles.td}>
                      <strong>{user.username}</strong>
                      {user.first_name && (
                        <span style={{ fontSize: "12px", color: "#6b7280" }}>
                          {" "}
                          ({user.first_name})
                        </span>
                      )}
                    </td>
                    <td style={styles.td}>{user.email}</td>
                    <td style={styles.td}>
                      {user.is_superuser ? (
                        <span style={styles.adminBadge}>Super Admin</span>
                      ) : (
                        <span>Utilisateur</span>
                      )}
                    </td>
                    <td style={styles.td}>
                      <span
                        style={
                          user.is_active
                            ? styles.activeBadge
                            : styles.inactiveBadge
                        }
                      >
                        {user.is_active ? "Actif" : "Inactif"}
                      </span>
                    </td>
                    <td style={styles.td}>{user.date_joined}</td>
                    <td style={styles.td}>
                      <button
                        style={styles.actionButton}
                        onClick={() => handleToggleActive(user)}
                        title={user.is_active ? "Desactiver" : "Activer"}
                      >
                        {user.is_active ? "🔴" : "🟢"}
                      </button>
                      <button
                        style={styles.actionButton}
                        onClick={() => handleDeleteUser(user)}
                        title="Supprimer"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div style={styles.modalOverlay} onClick={() => setShowModal(false)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h2 style={{ marginBottom: "20px" }}>Ajouter un utilisateur</h2>
            <form onSubmit={handleCreateUser}>
              <input
                style={styles.input}
                type="text"
                placeholder="Nom d'utilisateur *"
                value={formData.username}
                onChange={(e) =>
                  setFormData({ ...formData, username: e.target.value })
                }
                required
              />
              <input
                style={styles.input}
                type="email"
                placeholder="Email *"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                required
              />
              <input
                style={styles.input}
                type="password"
                placeholder="Mot de passe *"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                required
              />
              <input
                style={styles.input}
                type="text"
                placeholder="Prenom"
                value={formData.first_name}
                onChange={(e) =>
                  setFormData({ ...formData, first_name: e.target.value })
                }
              />
              <input
                style={styles.input}
                type="text"
                placeholder="Nom"
                value={formData.last_name}
                onChange={(e) =>
                  setFormData({ ...formData, last_name: e.target.value })
                }
              />
              <label
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  marginBottom: "20px",
                }}
              >
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) =>
                    setFormData({ ...formData, is_active: e.target.checked })
                  }
                />
                Activer le compte immediatement
              </label>
              <div style={styles.buttonRow}>
                <button
                  type="submit"
                  style={{ ...styles.addButton, background: "#10b981" }}
                >
                  Creer
                </button>
                <button
                  type="button"
                  style={{ ...styles.addButton, background: "#6b7280" }}
                  onClick={() => setShowModal(false)}
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminUsers;
