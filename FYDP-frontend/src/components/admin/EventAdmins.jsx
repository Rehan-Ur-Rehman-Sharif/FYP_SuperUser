import React, { useEffect, useState } from "react";
import axios from "../../utils/axiosInstance";

const EventAdmins = () => {
  const [advisors, setAdvisors] = useState([]);
  const [showModal, setShowModal] = useState(false);

  const [selected, setSelected] = useState(null);
  const [viewModal, setViewModal] = useState(false);
  const [editModal, setEditModal] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    email: "",
  });

  const [editData, setEditData] = useState({
    status: "active",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const normalizeList = (payload) => {
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload?.results)) return payload.results;
    return [];
  };

  const fetchAdvisors = async () => {
    try {
      const { data } = await axios.get("/api/events/event-advisors/");
      setAdvisors(normalizeList(data));
    } catch (error) {
      console.error("Failed to fetch event advisors:", error);
      setAdvisors([]);
    }
  };

  useEffect(() => {
    fetchAdvisors();
  }, []);

  const handleCreate = async () => {
    if (!formData.name || !formData.email) return;

    try {
      const payload = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        status: "active",
      };

      const { data } = await axios.post("/api/events/event-advisors/", payload);
      setAdvisors((prev) => [data, ...prev]);
      setShowModal(false);

      setFormData({
        name: "",
        email: "",
      });
    } catch (error) {
      console.error("Failed to create event advisor:", error);
      alert("Could not create event advisor. Please try again.");
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`/api/events/event-advisors/${id}/`);
      setAdvisors((prev) => prev.filter((a) => a.id !== id));
    } catch (error) {
      console.error("Failed to delete event advisor:", error);
      alert("Could not delete event advisor. Please try again.");
    }
  };

  const handleUpdate = async () => {
    if (!selected) return;

    try {
      const { data } = await axios.patch(`/api/events/event-advisors/${selected.id}/`, {
        status: editData.status,
      });

      setAdvisors((prev) =>
        prev.map((a) => (a.id === selected.id ? data : a))
      );
      setSelected(data);
      setEditModal(false);
    } catch (error) {
      console.error("Failed to update event advisor:", error);
      alert("Could not update event advisor. Please try again.");
    }
  };

  return (
    <div className="table-container">
      <div className="table-header">
        <h3>Event Advisors</h3>
        <button
          className="primary-btn"
          onClick={() => setShowModal(true)}
        >
          + Add Event Advisor
        </button>
      </div>

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Events Managed</th>
            <th>Active Events</th>
            <th>Status</th>
            <th>Join Date</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {advisors.map((row) => (
            <tr key={row.id}>
              <td>{row.name}</td>
              <td>{row.email}</td>
              <td>{row.eventsManaged}</td>
              <td>
                <span className="active">{row.activeEvents}</span>
              </td>
              <td>
                <span
                  className={
                    row.status === "active"
                      ? "status active"
                      : "status inactive"
                  }
                >
                  {row.status}
                </span>
              </td>
              <td>{row.joinDate}</td>
              <td className="actions">
                <button
                  className="btn-view"
                  onClick={() => {
                    setSelected(row);
                    setViewModal(true);
                  }}
                >
                  View
                </button>

                <button
                  className="btn-edit"
                  onClick={() => {
                    setSelected(row);
                    setEditData({ status: row.status });
                    setEditModal(true);
                  }}
                >
                  Edit
                </button>

                <button
                  className="btn-delete"
                  onClick={() => handleDelete(row.id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {viewModal && selected && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h1>Event Advisor</h1>
              <button type="button" onClick={() => setViewModal(false)}>✕</button>
            </div>

            <div className="form-grid">
              <input value={selected.name ?? ""} disabled placeholder="Name" title="Name" />
              <input value={selected.email ?? ""} disabled placeholder="Email" title="Email" />
              <input value={String(selected.eventsManaged ?? "")} disabled placeholder="Events managed" title="Events managed" />
              <input value={String(selected.activeEvents ?? "")} disabled placeholder="Active events" title="Active events" />
              <input value={selected.status ?? ""} disabled placeholder="Status" title="Status" />
              <input value={selected.joinDate ?? ""} disabled placeholder="Join date" title="Join date" />
            </div>

            <div className="modal-actions">
              <button type="button" className="btn-cancel" onClick={() => setViewModal(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {editModal && selected && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Edit status</h2>
              <button type="button" onClick={() => setEditModal(false)}>✕</button>
            </div>

            <div className="form-grid">
              <input value={selected.name ?? ""} disabled placeholder="Name" title="Name" />
              <input value={selected.email ?? ""} disabled placeholder="Email" title="Email" />

              <select
                value={editData.status}
                onChange={(e) =>
                  setEditData({ ...editData, status: e.target.value })
                }
                aria-label="Account status"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>

            <div className="modal-actions">
              <button type="button" className="btn-cancel" onClick={() => setEditModal(false)}>
                Cancel
              </button>
              <button type="button" className="btn-create" onClick={handleUpdate}>
                Update
              </button>
            </div>
          </div>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Add Event Advisor</h2>
              <button type="button" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <div className="form-grid">
              <input
                name="name"
                placeholder="Full name"
                value={formData.name}
                onChange={handleChange}
                autoComplete="name"
              />
              <input
                name="email"
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                autoComplete="email"
              />
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="btn-cancel"
                onClick={() => setShowModal(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn-create"
                onClick={handleCreate}
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EventAdmins;
