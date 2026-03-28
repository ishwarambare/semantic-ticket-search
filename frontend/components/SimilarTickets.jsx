export default function SimilarTickets({ results }) {
  if (!results || results.total_found === 0) {
    return (
      <div className="no-results">
        <p>✅ No similar tickets found. This appears to be a new issue.</p>
      </div>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 0.9) return "#ff4444";  // Very similar = red warning
    if (score >= 0.75) return "#ff8800"; // Similar = orange
    return "#44aa44";                     // Somewhat similar = green
  };

  return (
    <div className="similar-tickets">
      <h2>
        Similar Tickets Found ({results.total_found})
      </h2>

      {results.similar_tickets.map((item, idx) => (
        <div key={idx} className="ticket-card">
          <div className="ticket-header">
            <span className="ticket-id">
              #{item.ticket.id}
            </span>
            <span 
              className="similarity-score"
              style={{ color: getScoreColor(item.similarity_score) }}
            >
              {Math.round(item.similarity_score * 100)}% similar
            </span>
            <span className={`status ${item.ticket.status}`}>
              {item.ticket.status}
            </span>
          </div>

          <h3>{item.ticket.title}</h3>
          <p>{item.ticket.description}</p>

          {item.ticket.solution && (
            <div className="solution">
              <strong>✅ Solution:</strong>
              <p>{item.ticket.solution}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}