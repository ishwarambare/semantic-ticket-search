import { useState } from "react";
import TicketForm from "./components/TicketForm";
import SimilarTickets from "./components/SimilarTickets";
import "./App.css";

function App() {
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  return (
    <div className="app">
      <header>
        <h1>🔍 Smart Ticket Search</h1>
        <p>AI-powered similar ticket detection</p>
      </header>

      <main>
        <TicketForm
          onSearchResults={setSearchResults}
          setIsSearching={setIsSearching}
          isSearching={isSearching}
        />
        {searchResults && (
          <SimilarTickets results={searchResults} />
        )}
      </main>
    </div>
  );
}

export default App;