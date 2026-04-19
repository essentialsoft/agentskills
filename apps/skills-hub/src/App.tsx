import { Outlet } from "react-router-dom";

function App() {
  return (
    <main className="app-shell">
      <header className="app-header">
        <h1>ESI Skills Hub</h1>
        <p>Browse skills, filter quickly, and copy install commands.</p>
      </header>
      <Outlet />
    </main>
  );
}

export default App;
