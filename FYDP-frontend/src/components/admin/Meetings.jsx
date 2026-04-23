import React, { useEffect, useState } from "react";
import axios from "../../utils/axiosInstance";

const Meetings = () => {
  const [meetings, setMeetings] = useState([]);
  const [showModal, setShowModal] = useState(false);

  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const [viewModal, setViewModal] = useState(false);
  const [editModal, setEditModal] = useState(false);

  const [editData, setEditData] = useState({
    date: "",
    time: "",
    status: "",
  });
  const [formData, setFormData] = useState({
    organization: "",
    email: "",
    role: "",
    purpose: "",
    date: "",
    time: "",
    status: "Pending",
  });

  const fetchMeetings = async () => {
    try {
      const { data } = await axios.get("/api/meetings/");
      const list = Array.isArray(data) ? data : Array.isArray(data?.results) ? data.results : [];
      setMeetings(list);
    } catch (error) {
      console.error("Failed to fetch meetings:", error);
      setMeetings([]);
    }
  };

  useEffect(() => {
    fetchMeetings();
  }, []);

  // ✅ DELETE
  const handleDelete = async (id) => {
    if (!window.confirm("Delete this meeting?")) return;

    try {
      await axios.delete(`/api/meetings/${id}/`);
      setMeetings((prev) => prev.filter((m) => m.id !== id));
    } catch (error) {
      console.error("Failed to delete meeting:", error);
      alert("Could not remove meeting. Please try again.");
    }
  };

  // ✅ UPDATE
  const handleUpdate = async () => {
    if (!selectedMeeting) return;
    try {
      const payload = {
        date: editData.date,
        time: editData.time,
        status: editData.status,
      };
      const { data } = await axios.patch(`/api/meetings/${selectedMeeting.id}/`, payload);
      setMeetings((prev) => prev.map((m) => (m.id === selectedMeeting.id ? data : m)));
      setSelectedMeeting(data);
      setEditModal(false);
    } catch (error) {
      console.error("Failed to update meeting:", error);
      alert("Could not update meeting. Please verify date/time/status.");
    }
  };

  const handleCreateMeeting = async () => {
    if (!formData.organization || !formData.email || !formData.role || !formData.purpose || !formData.date || !formData.time) {
      return;
    }

    try {
      const payload = {
        organization: formData.organization,
        email: formData.email,
        role: formData.role,
        purpose: formData.purpose,
        date: formData.date,
        time: formData.time,
        status: formData.status,
      };
      const { data } = await axios.post("/api/meetings/", payload);
      setMeetings((prev) => [data, ...prev]);
      setShowModal(false);
      setFormData({
        organization: "",
        email: "",
        role: "",
        purpose: "",
        date: "",
        time: "",
        status: "Pending",
      });
    } catch (error) {
      console.error("Failed to create meeting:", error);
      alert("Could not create meeting. Please verify the form.");
    }
  };

  return (
    <div className="table-container">
      <div className="table-header">
        <h3>Meeting Requests</h3>
        <button
          className="primary-btn"
          onClick={() => setShowModal(true)}
        >
          + Add Meeting
        </button>
      </div>

      <table>
        <thead>
          <tr>
            <th>Organization</th>
            <th>Email</th>
            <th>Role</th>
            <th>Purpose</th>
            <th>Preferred Date</th>
            <th>Time</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {meetings.map((meeting) => (
            <tr key={meeting.id}>
              <td>{meeting.organization}</td>
              <td>{meeting.email}</td>
              <td>{meeting.role}</td>
              <td>{meeting.purpose}</td>
              <td>{meeting.date}</td>
              <td>{meeting.time}</td>

              <td>
                <span className={`status ${meeting.status.toLowerCase()}`}>
                  {meeting.status}
                </span>
              </td>

              {/* ACTIONS */}
              <td className="actions">
                <button
                  className="btn-view"
                  onClick={() => {
                    setSelectedMeeting(meeting);
                    setViewModal(true);
                  }}
                >
                  View
                </button>

                <button
                  className="btn-edit"
                  onClick={() => {
                    setSelectedMeeting(meeting);
                    setEditData({
                      date: meeting.date,
                      time: meeting.time,
                      status: meeting.status,
                    });
                    setEditModal(true);
                  }}
                >
                  Update
                </button>

                <button
                  className="btn-delete"
                  onClick={() => handleDelete(meeting.id)}
                >
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* ✅ VIEW MODAL */}
      {viewModal && selectedMeeting && (
        <div className="modal-overlay">
          <div className="modal">

            <div className="modal-header">
              <h2>Meeting Details</h2>
              <button onClick={() => setViewModal(false)}>✕</button>
            </div>

            <div className="form-grid">
              <input value={selectedMeeting.organization} disabled />
              <input value={selectedMeeting.email} disabled />
              <input value={selectedMeeting.role} disabled />
              <input value={selectedMeeting.purpose} disabled />
              <input value={selectedMeeting.date} disabled />
              <input value={selectedMeeting.time} disabled />
              <input value={selectedMeeting.status} disabled />
            </div>

            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setViewModal(false)}
              >
                Close
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ✅ CREATE MODAL */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Add New Meeting</h2>
              <button onClick={() => setShowModal(false)}>✕</button>
            </div>

            <div className="form-grid">
              <input
                name="organization"
                placeholder="Organization"
                value={formData.organization}
                onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
              />
              <input
                name="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
              <input
                name="role"
                placeholder="Role"
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              />
              <input
                name="purpose"
                placeholder="Purpose"
                value={formData.purpose}
                onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
              />
              <input
                type="date"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              />
              <input
                type="time"
                value={formData.time}
                onChange={(e) => setFormData({ ...formData, time: e.target.value })}
              />
              <select
                className="full-width"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              >
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>

            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setShowModal(false)}>
                Cancel
              </button>
              <button className="btn-create" onClick={handleCreateMeeting}>
                Create Meeting
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ✅ EDIT MODAL */}
      {editModal && selectedMeeting && (
        <div className="modal-overlay">
          <div className="modal">

            <div className="modal-header">
              <h2>Update Meeting</h2>
              <button onClick={() => setEditModal(false)}>✕</button>
            </div>

            <div className="form-grid">
              <input value={selectedMeeting.organization} disabled />
              <input value={selectedMeeting.email} disabled />

              {/* Editable Fields */}
              <input
                type="date"
                value={editData.date}
                onChange={(e) =>
                  setEditData({ ...editData, date: e.target.value })
                }
              />

              <input
                type="time"
                value={editData.time}
                onChange={(e) =>
                  setEditData({ ...editData, time: e.target.value })
                }
              />

              <select
                value={editData.status}
                onChange={(e) =>
                  setEditData({ ...editData, status: e.target.value })
                }
                className="full-width"
              >
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>

            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setEditModal(false)}
              >
                Cancel
              </button>

              <button
                className="btn-create"
                onClick={handleUpdate}
              >
                Update
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
};

export default Meetings;