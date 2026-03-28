import { useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000";

export default function TicketForm({ 
  onSearchResults, 
  setIsSearching,
  isSearching 
}) {
  const [form, setForm] = useState({
    title: "",
    description: "",
    priority: "medium",
  });
  const [duplicateWarning, setDuplicateWarning] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const checkDuplicate = async () => {
    if (form.title.length < 5) return;
    
    try {
      const res = await axios.get(
        `${API_URL}/search/check-duplicate`,
        { params: { 
            title: form.title, 
            description: form.description 
          } 
        }
      );
      if (res.data.is_likely_duplicate) {
        setDuplicateWarning(res.data);
      } else {
        setDuplicateWarning(null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSearch = async () => {
    if (!form.description) return;
    setIsSearching(true);
    
    try {
      const res = await axios.get(
        `${API_URL}/search/similar`,
        { params: { 
            query: `${form.title} ${form.description}`,
            top_k: 5
          } 
        }
      );
      onSearchResults(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleCreate = async () => {
    try {
      await axios.post(`${API_URL}/tickets/`, form);
      alert("Ticket created successfully!");
      setForm({ title: "", description: "", priority: "medium" });
      onSearchResults(null);
      setDuplicateWarning(null);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="ticket-form">
      <h2>New Ticket</h2>

      {duplicateWarning && (
        <div className="warning">
          ⚠️ Similar tickets already exist! 
          Check results below before creating.
        </div>
      )}

      <input
        name="title"
        placeholder="Ticket title"
        value={form.title}
        onChange={handleChange}
        onBlur={checkDuplicate}
      />

      <textarea
        name="description"
        placeholder="Describe the issue in detail..."
        value={form.description}
        onChange={handleChange}
        rows={4}
      />

      <select 
        name="priority" 
        value={form.priority}
        onChange={handleChange}
      >
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
        <option value="critical">Critical</option>
      </select>

      <div className="buttons">
        <button 
          onClick={handleSearch}
          disabled={isSearching || !form.description}
          className="btn-search"
        >
          {isSearching ? "Searching..." : "🔍 Find Similar"}
        </button>

        <button 
          onClick={handleCreate}
          disabled={!form.title || !form.description}
          className="btn-create"
        >
          ➕ Create Ticket
        </button>
      </div>
    </div>
  );
}