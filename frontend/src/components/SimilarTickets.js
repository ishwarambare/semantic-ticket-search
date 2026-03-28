function SimilarTickets({ results }) {
  if (!results) return null;

  const { query, similar_tickets, total_found } = results;

  const priorityColor = (score) => {
    if (score >= 0.85) return "#22c55e";
    if (score >= 0.7) return "#f59e0b";
    return "#94a3b8";
  };

  return (
    <div className="results-section">
      <div className="results-header">
        <h2>Search Results</h2>
        <p className="results-meta">
          Found <strong>{total_found}</strong> similar ticket{total_found !== 1 ? "s" : ""} for:{" "}
          <em>"{query}"</em>
        </p>
      </div>

      {total_found === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">🎉</span>
          <p>No similar tickets found — this looks like a new issue!</p>
        </div>
      ) : (
        <div className="tickets-list">
          {similar_tickets.map((item, idx) => {
            const { ticket, similarity_score, has_solution } = item;
            const pct = Math.round(similarity_score * 100);

            return (
              <div key={ticket.id} className="ticket-card">
                {/* Rank + Score */}
                <div className="ticket-rank">
                  <span className="rank-number">#{idx + 1}</span>
                  <div className="score-circle" style={{ borderColor: priorityColor(similarity_score) }}>
                    <span style={{ color: priorityColor(similarity_score) }}>{pct}%</span>
                    <small>match</small>
                  </div>
                </div>

                {/* Content */}
                <div className="ticket-content">
                  <div className="ticket-top-row">
                    <h3>
                      <span className="ticket-id">#{ticket.id}</span> {ticket.title}
                    </h3>
                    <div className="ticket-badges">
                      <span className={`status-badge status-${ticket.status}`}>
                        {ticket.status}
                      </span>
                      <span className={`priority-badge priority-${ticket.priority}`}>
                        {ticket.priority}
                      </span>
                      {has_solution && (
                        <span className="solution-badge">✅ Has Solution</span>
                      )}
                    </div>
                  </div>

                  <p className="ticket-description">{ticket.description}</p>

                  {ticket.solution && (
                    <div className="solution-box">
                      <strong>💡 Solution:</strong>
                      <p>{ticket.solution}</p>
                    </div>
                  )}

                  <div className="ticket-footer">
                    {ticket.category && (
                      <span className="category-tag">📁 {ticket.category}</span>
                    )}
                    <span className="ticket-date">
                      🕒 {new Date(ticket.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default SimilarTickets;
