import { useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ReportPage from "./pages/ReportPage";
import ChatPage from "./pages/ChatPage";
import NiroChatPage from "./pages/NiroChatPage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/report/:reportId" element={<ReportPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/niro" element={<NiroChatPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
