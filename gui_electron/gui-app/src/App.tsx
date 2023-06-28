import logo from './logo.svg';
import React from "react";
import { BrowserRouter, Route } from "react-router-dom";
import './App.css';
import Sidebar from './components/sidebar.tsx';
import Tab from './components/tab1.tsx';
// import Sidebar from './components/sidebar2.tsx';


function App() {
  return (
    <div className="App">
      <Tab></Tab>
      <header className="App-header">
      </header>
      {/* <Sidebar>
        <p>여기에</p>
        <p>result를 띄우면 될 것 같아요</p>
      </Sidebar> */}
    </div>
  );
}

export default App;
