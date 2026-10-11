import {BrowserRouter, Routes, Route, useLocation} from 'react-router-dom'
import { useState , useEffect, useRef} from 'react'
import './index.css'
import Home from './home.jsx'
import Features from './features.jsx'
import Navbar from './navbar.jsx'
import Login from './login.jsx'
import Protected from './protected.jsx'
import Dashboard from './dashboard.jsx'
import SignUp from './signup.jsx'

//MY BELOVED TOASTER
import {Toaster} from 'react-hot-toast';

//import Navbar from './navbar.jsx'
//ALL PAGES!
function Topset(){
  const path = useLocation();
  const target = useRef(null);
  useEffect(() => {
      if(target.current){
        target.current.scrollIntoView({ //special to start where i want
          behavior: "instant",  //smooth auto
          block: "start" //alligns to the top!
    })
    }
  }, [path])
  return (
    <div ref = {target}>
      <Routes>
        <Route path = "/" element = {<Home/>}/>
        <Route path = "/features" element = {<Features/>}/>
        <Route path = "/login" element = {<Login/>}/>
        <Route path = "/signup" element = {<SignUp/>}/>
        <Route path = "/dashboard" element = {
          <Protected>
            <Dashboard /> 
          </Protected>
        }/>
      </Routes>
    </div>
  ); 
}
export default function App() {
  return(
    <BrowserRouter>
      <Navbar/>
      <Toaster/>
      <Topset/>
    </BrowserRouter>
  );
}