import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext";
import Layout from "./components/Layout";
import Dashboard from "./modules/dashboard/Dashboard";
import AgentsPage from "./modules/agent/AgentsPage";
import ViolationsPage from "./modules/violation/ViolationsPage";
import RulesPage from "./modules/settings/RulesPage";
import SettingsPage from "./modules/settings/SettingsPage";

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agents" element={<AgentsPage />} />
            <Route path="/violations" element={<ViolationsPage />} />
            <Route path="/rules" element={<RulesPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
