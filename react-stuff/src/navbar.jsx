import {Link, useNavigate} from 'react-router-dom'
import './index.css'
import cover from "./assets/cover.PNG"
import {get_login_status} from './data.jsx'
import {useLocation} from 'react-router-dom'
import toast from 'react-hot-toast';
const MREOW = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "")
import {supabase} from './main.jsx'

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
    const Navigate = useNavigate()
    const location = useLocation()
    async function logout(){ 
        try {
            const {data:data1, error:error1} = await supabase.auth.getSession()
            if (error1){
                toast.error(error1.message)
                return
            }
            if (!data1.session){
                toast.error("you shouldn't be here!");
                Navigate('/signup');
                return;
            }
            const token = data1.session.access_token
            //all good!
            const response2 = await fetch(
                `${MREOW}/LOGOUT/${token}`, {method: "POST"}
            );
            if (!response2.ok){
                toast.error("error.")
                return
            }
            //sign out front end 
            const {error:error2} = await supabase.auth.signOut()
            if (error2){
                toast.error(error2.message)
                return
            }
            
            toast.success("logged you out!")
            Navigate('/')
        }catch (e){
            toast.error("SERVER DID NOT SYNC")
            Navigate('/')
        }
    }
    if (get_login_status() && location.pathname == "/dashboard"){
        //LOGGED IN 
        return(
            <ul className = "list">
                <li> <button onClick = {logout}> Log Out </button> </li>
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