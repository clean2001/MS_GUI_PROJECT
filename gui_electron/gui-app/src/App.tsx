import logo from './logo.svg';
import './App.css';
import Sidebar from './components/sidebar.tsx';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        {/* <img src={logo} className="App-logo" alt="logo" /> */}
        <div id="toolbar">toolbar</div>
      </header>
      <Sidebar>
        <p>여기에</p>
        <p>result를 띄우면 될 것 같아요</p>
      </Sidebar>

    </div>
  );
}

export default App;
