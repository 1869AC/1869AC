import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { useEffect, useRef } from 'react'
import './index.css'
import Home from './home.jsx'
import Features from './features.jsx'
import Navbar from './navbar.jsx'

function Topset() {
  const path = useLocation();
  const target = useRef(null);
  useEffect(() => {
      if(target.current){
        target.current.scrollIntoView({ 
          behavior: "instant", 
          block: "start" 
        })
    }
  }, [path])
  return (
    <div ref={target}>
      <Routes>
        <Route path="/" element={<Home/>}/>
        <Route path="/features" element={<Features/>}/>
      </Routes>
    </div>
  ); 
}

export default function App() {
  return(
    <BrowserRouter basename="/1869AC">
      <Navbar/>
      <Topset/>
    </BrowserRouter>
  );
}