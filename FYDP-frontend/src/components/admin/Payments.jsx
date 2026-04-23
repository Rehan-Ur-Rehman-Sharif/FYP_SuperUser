import React, { useEffect, useState } from "react";
import axios from "../../utils/axiosInstance";

const Payments = () => {
  const [payments, setPayments] = useState([]);
  const [showModal, setShowModal] = useState(false);

  const [selectedPayment, setSelectedPayment] = useState(null);
  const [viewModal, setViewModal] = useState(false);
  const [editModal, setEditModal] = useState(false);

  const [editData, setEditData] = useState({
    amount: "",
    dueDate: "",
    status: "",
  });
  const [formData, setFormData] = useState({
    organization: "",
    email: "",
    role: "",
    amount: "",
    dueDate: "",
    status: "Pending",
  });

  const fetchPayments = async () => {
    try {
      const { data } = await axios.get("/api/payments/");
      const list = Array.isArray(data) ? data : Array.isArray(data?.results) ? data.results : [];
      setPayments(list);
    } catch (error) {
      console.error("Failed to fetch payments:", error);
      setPayments([]);
    }
  };

  useEffect(() => {
    fetchPayments();
  }, []);

  // ✅ DELETE
  const handleDelete = async (id) => {
    if (!window.confirm("Delete this payment?")) return;

    try {
      await axios.delete(`/api/payments/${id}/`);
      setPayments((prev) => prev.filter((p) => p.id !== id));
    } catch (error) {
      console.error("Failed to delete payment:", error);
      alert("Could not remove payment. Please try again.");
    }
  };

  // ✅ UPDATE
  const handleUpdate = async () => {
    if (!selectedPayment) return;
    try {
      const payload = {
        amount: Number(editData.amount),
        dueDate: editData.dueDate,
        status: editData.status,
      };
      const { data } = await axios.patch(`/api/payments/${selectedPayment.id}/`, payload);
      setPayments((prev) => prev.map((p) => (p.id === selectedPayment.id ? data : p)));
      setSelectedPayment(data);
      setEditModal(false);
    } catch (error) {
      console.error("Failed to update payment:", error);
      alert("Could not update payment. Please verify amount, due date and status.");
    }
  };

  const handleCreatePayment = async () => {
    if (!formData.organization || !formData.email || !formData.role || !formData.amount || !formData.dueDate) {
      return;
    }

    try {
      const payload = {
        organization: formData.organization,
        email: formData.email,
        role: formData.role,
        amount: Number(formData.amount),
        dueDate: formData.dueDate,
        status: formData.status,
      };
      const { data } = await axios.post("/api/payments/", payload);
      setPayments((prev) => [data, ...prev]);
      setShowModal(false);
      setFormData({
        organization: "",
        email: "",
        role: "",
        amount: "",
        dueDate: "",
        status: "Pending",
      });
    } catch (error) {
      console.error("Failed to create payment:", error);
      alert("Could not create payment. Please verify the form.");
    }
  };

  return (
    <div className="table-container">
      <div className="table-header">
        <h3>Pending Payments</h3>
        <button
          className="primary-btn"
          onClick={() => setShowModal(true)}
        >
          + Add Payment
        </button>
      </div>

      <table>
        <thead>
          <tr>
            <th>Organization Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Amount</th>
            <th>Due Date</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {payments.map((payment) => (
            <tr key={payment.id}>
              <td>{payment.organization}</td>
              <td>{payment.email}</td>
              <td>{payment.role}</td>
              <td>₹{payment.amount}</td>
              <td>{payment.dueDate}</td>

              <td>
                <span className={`status ${payment.status.toLowerCase()}`}>
                  {payment.status}
                </span>
              </td>

              {/* ACTIONS */}
              <td>
                <button
                  className="btn-view"
                  onClick={() => {
                    setSelectedPayment(payment);
                    setViewModal(true);
                  }}
                >
                  View
                </button>

                <button
                  className="btn-edit"
                  onClick={() => {
                    setSelectedPayment(payment);
                    setEditData({
                      amount: payment.amount,
                      dueDate: payment.dueDate,
                      status: payment.status,
                    });
                    setEditModal(true);
                  }}
                >
                  Update
                </button>

                <button
                  className="btn-delete"
                  onClick={() => handleDelete(payment.id)}
                >
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* ✅ VIEW MODAL */}
      {viewModal && selectedPayment && (
        <div className="modal-overlay">
          <div className="modal">

            <div className="modal-header">
              <h2>Payment Details</h2>
              <button onClick={() => setViewModal(false)}>✕</button>
            </div>

            <div className="form-grid">
              <input value={selectedPayment.organization} disabled />
              <input value={selectedPayment.email} disabled />
              <input value={selectedPayment.role} disabled />
              <input value={`₹${selectedPayment.amount}`} disabled />
              <input value={selectedPayment.dueDate} disabled />
              <input value={selectedPayment.status} disabled />
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
              <h2>Add New Payment</h2>
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
                type="number"
                placeholder="Amount"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              />
              <input
                type="date"
                value={formData.dueDate}
                onChange={(e) => setFormData({ ...formData, dueDate: e.target.value })}
              />
              <select
                className="full-width"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              >
                <option value="Paid">Paid</option>
                <option value="Pending">Pending</option>
                <option value="Overdue">Overdue</option>
              </select>
            </div>

            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setShowModal(false)}>
                Cancel
              </button>
              <button className="btn-create" onClick={handleCreatePayment}>
                Create Payment
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ✅ EDIT MODAL */}
      {editModal && selectedPayment && (
        <div className="modal-overlay">
          <div className="modal">

            <div className="modal-header">
              <h2>Update Payment</h2>
              <button onClick={() => setEditModal(false)}>✕</button>
            </div>

            <div className="form-grid">
              <input value={selectedPayment.organization} disabled />
              <input value={selectedPayment.email} disabled />

              <input
                type="number"
                placeholder="Amount"
                value={editData.amount}
                onChange={(e) =>
                  setEditData({ ...editData, amount: e.target.value })
                }
              />

              <input
                type="date"
                value={editData.dueDate}
                onChange={(e) =>
                  setEditData({ ...editData, dueDate: e.target.value })
                }
              />

              <select
                value={editData.status}
                onChange={(e) =>
                  setEditData({ ...editData, status: e.target.value })
                }
                className="full-width"
              >
                <option value="Paid">Paid</option>
                <option value="Pending">Pending</option>
                <option value="Overdue">Overdue</option>
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

export default Payments;