import { useState , useEffect, useRef} from 'react'
import { useNavigate} from 'react-router-dom'
import {set_login_status} from './data.jsx'
import {supabase} from './main.jsx'
import show from "./assets/showpass.PNG"
import hide from "./assets/hidepass.PNG"

//MY BELOVED TOASTER
import toast from 'react-hot-toast';

export default function login(){
    const Navigate = useNavigate()
    const [name, setName] = useState("")
    const [password, setPassword] = useState("")
    const [passimg, setPassImg] = useState(false)
    async function submit(e) { 
        e.preventDefault(); 
        // DB CODE
        const real_username = name + "@gmail.com"
        try{
            const {data,error} = await supabase.auth.signInWithPassword(
                {
                    "email": real_username, 
                    "password": password
                }
            )
            if (error) throw error
            toast.success("Sucessfully logged in!")
            set_login_status(true)
            console.log("ERM WHAT THE SIGMA")
            setTimeout(()=>{Navigate("/dashboard")},1000)
        }catch(e){
            toast.error(e.message || "Something has gone wrong.")
        }
    }
    return(
        <div className = "container">
            <p className = "los"> Login! </p>
            <form className = "form" onSubmit = {submit}>
                <input 
                placeholder = "name"
                maxLength = "18"
                minLength = "6"
                onChange =  {(e) => {setName(e.target.value)}}
                />
                <div className = "columner">
                    <div style = {{paddingLeft: "50px", gap: "8px"}}className = "row"> 
                        <input 
                        placeholder = "password"
                        maxLength = "18"
                        minLength = "6"
                        type = "password"
                        onChange = {(e) => {setPassword(e.target.value)}}
                        />
                        <button type = "button" className = "special_button" onClick = {() => setPassImg(!passimg)}> <img src = {passimg? show: hide } alt = "show password" /> </button>
                    </div>
                    <p> {passimg?`${password}`:""}</p> 
                </div>
                <button style = {{backgroundColor: "rgb(140, 8, 8)", color: "white"}} type = "submit"> Submit! </button>
            </form>
            <button type = "button" onClick = {() => Navigate('/signup')}> Signup </button>
        </div>
    );
}

