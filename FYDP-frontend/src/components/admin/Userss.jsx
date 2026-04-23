import React, { useEffect, useState } from "react";
import axios from "../../utils/axiosInstance";

const Users = () => {
  const [users, setUsers] = useState([]);

  const [selectedUser, setSelectedUser] = useState(null);
  const [viewModal, setViewModal] = useState(false);
  const [editModal, setEditModal] = useState(false);

  const [editData, setEditData] = useState({
    role: "",
    status: "",
  });

  const fetchUsers = async () => {
    try {
      const { data } = await axios.get("/api/users/");
      setUsers(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Failed to fetch users:", error);
      setUsers([]);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // ✅ DELETE
  const handleDelete = async (id) => {
    if (!window.confirm("Delete this user?")) return;

    try {
      await axios.delete(`/api/users/${id}/`);
      setUsers((prev) => prev.filter((u) => u.id !== id));
    } catch (error) {
      console.error("Failed to remove user:", error);
      alert("Could not remove user. Please try again.");
    }
  };

  // ✅ UPDATE
  const handleUpdate = async () => {
    if (!selectedUser) return;
    try {
      const payload = {
        role: editData.role,
        status: editData.status,
      };
      const { data } = await axios.patch(`/api/users/${selectedUser.id}/`, payload);
      setUsers((prev) => prev.map((u) => (u.id === selectedUser.id ? data : u)));
      setSelectedUser(data);
      setEditModal(false);
    } catch (error) {
      console.error("Failed to update user:", error);
      alert("Could not update user. Please try again.");
    }
  };

  return (
    <div className="table-container">
      <div className="table-header">
        <h3>Current Users</h3>
      </div>

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Organization</th>
            <th>Department</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.name}</td>
              <td>{user.email}</td>
              <td>{user.role}</td>
              <td>{user.organization}</td>
              <td>{user.department}</td>

              {/* STATUS */}
              <td>
                <span className={`status ${user.status}`}>
                  {user.status}
                </span>
              </td>

              {/* ACTIONS */}
              <td className="actions">
                <button
                  className="btn-view"
                  onClick={() => {
                    setSelectedUser(user);
                    setViewModal(true);
                  }}
                >
                  View
                </button>

                <button
                  className="btn-edit"
                  onClick={() => {
                    setSelectedUser(user);
                    setEditData({
                      role: user.role,
                      status: user.status,
                    });
                    setEditModal(true);
                  }}
                >
                  Update
                </button>

                <button
                  className="btn-delete"
                  onClick={() => handleDelete(user.id)}
                >
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* ✅ VIEW MODAL */}
      {viewModal && selectedUser && (
        <div className="modal-overlay">
          <div className="modal">

            <div className="modal-header">
              <h2>User Details</h2>
              <button onClick={() => setViewModal(false)}>✕</button>
            </div>

            <div className="form-grid">
              <input value={selectedUser.name} disabled />
              <input value={selectedUser.email} disabled />
              <input value={selectedUser.role} disabled />
              <input value={selectedUser.organization} disabled />
              <input value={selectedUser.department} disabled />
              <input value={selectedUser.status} disabled />
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

      {/* ✅ EDIT MODAL */}
      {editModal && selectedUser && (
        <div className="modal-overlay">
          <div className="modal">

            <div className="modal-header">
              <h2>Update User</h2>
              <button onClick={() => setEditModal(false)}>✕</button>
            </div>

            <div className="form-grid">
              <input value={selectedUser.name} disabled />
              <input value={selectedUser.email} disabled />

              {/* ROLE */}
              <select
                value={editData.role}
                onChange={(e) =>
                  setEditData({ ...editData, role: e.target.value })
                }
              >
                <option value="Admin">Admin</option>
                <option value="Student">Student</option>
                <option value="Teacher">Teacher</option>
                <option value="Employee">Employee</option>
              </select>

              {/* STATUS */}
              <select
                value={editData.status}
                onChange={(e) =>
                  setEditData({ ...editData, status: e.target.value })
                }
              >
                <option value="online">online</option>
                <option value="offline">offline</option>
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

export default Users;