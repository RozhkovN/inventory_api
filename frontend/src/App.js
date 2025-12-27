import React, { useState } from 'react';
import './App.css';
import Warehouse from './Warehouse';
import Sales from './Sales';
import History from './History';

function App() {
  const [activeTab, setActiveTab] = useState('warehouse');

  return (
    <div className="App">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>📊 Inventory Manager</h1>
        </div>
        <div className="navbar-menu">
          <button 
            className={`nav-button ${activeTab === 'warehouse' ? 'active' : ''}`}
            onClick={() => setActiveTab('warehouse')}
          >
            📦 Склад
          </button>
          <button 
            className={`nav-button ${activeTab === 'sales' ? 'active' : ''}`}
            onClick={() => setActiveTab('sales')}
          >
            💰 Продажи
          </button>
          <button 
            className={`nav-button ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            📊 История
          </button>
        </div>
      </nav>

      <main className="main-content">
        {activeTab === 'warehouse' && <Warehouse />}
        {activeTab === 'sales' && <Sales />}
        {activeTab === 'history' && <History />}
      </main>

      <footer className="app-footer">
        <p>© 2025 Inventory Manager | FastAPI + React</p>
      </footer>
    </div>
  );
}

export default App;
