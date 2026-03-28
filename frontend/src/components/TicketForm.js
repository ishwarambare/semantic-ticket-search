import { useState } from "react";
import "./TicketForm.css";

const API_BASE = "http://localhost:8000";

function TicketForm({ onSearchResults, setIsSearching, isSearching }) {
  const [mode, setMode] = useState("search"); // "search" | "create"
  const [query, setQuery] = useState("");
  const [form, setForm] = useState({
    title: "",
    description: "",
    priority: "medium",
    category: "",
  });
  const [createStatus, setCreateStatus] = useState(null);
  const [duplicateWarning, setDuplicateWarning] = useState(null);

  // ── Search ──────────────────────────────────────
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setIsSearching(true);
    onSearchResults(null);
    try {
      const res = await fetch(
        `${API_BASE}/search/similar?query=${encodeURIComponent(query)}&top_k=5`
      );
      const data = await res.json();
      onSearchResults(data);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setIsSearching(false);
    }
  };

  // ── Create ──────────────────────────────────────
  const handleCreate = async (e) => {
    e.preventDefault();
    setCreateStatus(null);
    setDuplicateWarning(null);
    setIsSearching(true);

    // Check for duplicates first
    try {
      const dupRes = await fetch(
        `${API_BASE}/search/check-duplicate?title=${encodeURIComponent(
          form.title
        )}&description=${encodeURIComponent(form.description)}`
      );
      const dupData = await dupRes.json();
      if (dupData.is_likely_duplicate) {
        setDuplicateWarning(dupData);
        setIsSearching(false);
        return;
      }
    } catch (err) {
      // Ignore duplicate check failure, proceed to create
    }

    try {
      const res = await fetch(`${API_BASE}/tickets/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (res.ok) {
        const ticket = await res.json();
        setCreateStatus({ success: true, ticket });
        setForm({ title: "", description: "", priority: "medium", category: "" });
      } else {
        setCreateStatus({ success: false });
      }
    } catch (err) {
      setCreateStatus({ success: false });
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="ticket-form-card">
      {/* Mode Toggle */}
      <div className="mode-toggle">
        <button
          className={mode === "search" ? "active" : ""}
          onClick={() => { setMode("search"); onSearchResults(null); setCreateStatus(null); setDuplicateWarning(null); }}
        >
          🔍 Find Similar
        </button>
        <button
          className={mode === "create" ? "active" : ""}
          onClick={() => { setMode("create"); onSearchResults(null); setCreateStatus(null); setDuplicateWarning(null); }}
        >
          ✏️ Create Ticket
        </button>
      </div>

      {/* Search Mode */}
      {mode === "search" && (
        <form onSubmit={handleSearch} className="form-body">
          <label>Describe your issue</label>
          <textarea
            id="search-query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. I can't log into the system after the latest update..."
            rows={4}
            required
          />
          <button type="submit" className="submit-btn" disabled={isSearching}>
            {isSearching ? (
              <span className="spinner-text">⏳ Searching...</span>
            ) : (
              "Find Similar Tickets"
            )}
          </button>
        </form>
      )}

      {/* Create Mode */}
      {mode === "create" && (
        <form onSubmit={handleCreate} className="form-body">
          <label>Title</label>
          <input
            id="ticket-title"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Short summary of the issue"
            required
          />

          <label>Description</label>
          <textarea
            id="ticket-description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="Describe the problem in detail..."
            rows={4}
            required
          />

          <div className="form-row">
            <div className="form-group">
              <label>Priority</label>
              <select
                id="ticket-priority"
                value={form.priority}
                onChange={(e) => setForm({ ...form, priority: e.target.value })}
              >
                <option value="low">🟢 Low</option>
                <option value="medium">🟡 Medium</option>
                <option value="high">🔴 High</option>
                <option value="critical">🚨 Critical</option>
              </select>
            </div>
            <div className="form-group">
              <label>Category</label>
              <input
                id="ticket-category"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                placeholder="e.g. authentication"
              />
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={isSearching}>
            {isSearching ? "⏳ Checking..." : "Submit Ticket"}
          </button>

          {/* Duplicate Warning */}
          {duplicateWarning && (
            <div className="duplicate-warning">
              <h4>⚠️ Similar tickets already exist</h4>
              <p>Your ticket may be a duplicate. Please review before submitting.</p>
              <ul>
                {duplicateWarning.similar_tickets.map((t) => (
                  <li key={t.id}>
                    <strong>#{t.id}</strong> — {t.title}{" "}
                    <span className="score">{Math.round(t.similarity_score * 100)}% match</span>
                    <span className={`status-badge status-${t.status}`}>{t.status}</span>
                  </li>
                ))}
              </ul>
              <button
                className="submit-btn secondary"
                onClick={() => { setDuplicateWarning(null); handleCreate({ preventDefault: () => {} }); }}
              >
                Submit Anyway
              </button>
            </div>
          )}

          {/* Success */}
          {createStatus?.success && (
            <div className="success-banner">
              ✅ Ticket <strong>#{createStatus.ticket.id}</strong> created successfully!
            </div>
          )}
          {createStatus?.success === false && (
            <div className="error-banner">❌ Failed to create ticket. Check the API server.</div>
          )}
        </form>
      )}
    </div>
  );
}

export default TicketForm;
