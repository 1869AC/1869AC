import {Link} from 'react-router-dom'
import './index.css'
import cover from "./assets/cover.PNG"
import {get_login_status} from './data.jsx'
import {useLocation} from 'react-router-dom'

export default function NavBar () {
    return(
    <nav className = "nav">
        <div className = "logo">
            <img className = "small" src = {cover} />
            <p> 1869AC </p>
        </div>

        {/* THE ACTUAL LIST! */}
        <List/>
    </nav>
    );
}

function List(){ 
    const location = useLocation()
    if (get_login_status() && location.pathname == "/dashboard"){
        //LOGGED IN 
        return(
            <ul className = "list">
                <li> <Link to = "/"><img className = "small" src = {cover}/></Link> </li> 
                <li> <Link to = "/"><img className = "small" src = {cover}/></Link> </li>
                <li> <Link to = "/"><img className = "small" src = {cover}/></Link> </li>
                <li> <Link to = "/"><img className = "small" src = {cover}/></Link> </li>
             </ul>
        );
    }else{
        return(
            <ul className = "list">
                <li> <Link to = "/"> Home </Link> </li>
                <li> <Link to = "/features"> Features </Link> </li>
                <li> <Link to = "/login"> Login </Link></li>
                <li> <Link to = "/signup"> Signup </Link></li>
                <li> <Link to="/about"> About </Link> </li>
            </ul>
        );
    }
}