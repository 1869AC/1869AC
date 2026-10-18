import { useState , useEffect, useRef} from 'react'
import wall from "./assets/wall.PNG"
import plus from "./assets/cover.PNG"
import {supabase} from './main.jsx'
import { useNavigate} from 'react-router-dom'
import toast from 'react-hot-toast';
const MREOW = import.meta.env.VITE_API_URL
const mode =  localStorage.getItem("mode") || "guest"

const playlist_array = [
    ["song", "path", "./assets/cover.PNG"],
    ["othersong", "path2", "./assets/cover.PNG"], 
    ["how usefless", "path3", "./assets/cover.PNG"], 
    ["beautiful", "path4", "./assets/cover.PNG"],
    ["song", "path", "./assets/cover.PNG"],
    ["othersong", "path2", "./assets/cover.PNG"], 
    ["how usefless", "path3", "./assets/cover.PNG"], 
    ["beautiful", "path4", "./assets/cover.PNG"],
    ["song", "path", "./assets/cover.PNG"],
    ["othersong", "path2", "./assets/cover.PNG"], 
    ["how usefless", "path3", "./assets/cover.PNG"], 
    ["beautiful", "path4", "./assets/cover.PNG"]
];

function Playlists({ifSlice}){//obj
    const new_array = ifSlice? playlists.slice(0,8):playlists 
    {/* PLS ADD PLAYLIST EXTRACTION LOGIC!*/}
    if(new_array.length === 0){
        return (<p> No playlists! Go and make one!</p>)
    }
        return(
        <>
            {new_array.map((playlist, index)=> {
            return(
                <div key = {index}>
                    <p>{playlist.name}</p>
                </div>
            );
            })}
        </>
        );
}
function url(path){ 
    return new URL(path, import.meta.url).href; // turns the path into a web url
}
export default function Dashboard(){
    const [all, setAll] = useState(false)
    const [playlists, setPlaylists] = useState([])
    const Navigate = useNavigate()
    const [loading, setLoading] = useState(true);
    const [selected, setSelected] = useState(null)
    useEffect(() => { 
        //GUEST
        async function guestFetcher(){
            try{
                const response = await fetch(
                    "{MREOW}/GIMMETHOSESONGS/0"
                );
                if (!response.ok){
                    throw new Error("COULD NOT LOAD PLAYLIST UNO")
                }
                const data = await response.json()
                if (!Array.isArray(data)){
                    throw new Error("yeah this ones never happening?")
                }
                setPlaylists(first);
            }catch(e){
                toast.error(e.message)
            }
        }
        // AUTH
        async function fetcher() { 
            try{
                const {response, error} = await supabase.auth.getUser()
                if (!response.data.user || !response.data ){
                    // well dang how did you get here??
                    Navigate('/signup')
                    toast.error("HOW DID YOU GET HERE?!")
                    return
                }   
            }catch(e){
                toast.error(e)
            }
            const {response2, error2} = await supabase.from("users").select("songs").eq("id", user.id).maybeSingle(); 
            if(error){
                toast.error(error.message)
                return;
            }
            else if (response2.data && response2.data.songs){
                const formattedSongs = response2.data.map(song => [
                    song.name || "Untitled",
                    song.dir || "missing path",
                ])
                setPlaylists(formattedSongs)
        }}
        if(get_mode() == "guest"){
            guestFetcher()
        }
        else{
            fetcher()
        }
    }, []);
    return(
        <div className = "container">
            <h1> THIS SITE IS EXPERIMENTAL. INFERFACE ON THIS PAGE DOES NOT WORK AT THE MOMENT!</h1>
            <div className = "menu_row">
                <p> Playlists </p>
                <button style ={{color: "white", backgroundColor: "MediumSeaGreen", transform: "scale(1.5)", marginBottom: "3em"}} onClick = {toggle}> {!all? "Show all": "Condense"}</button>
            </div>
           <div className = "playlists">
                <Playlists 
                ifSlice = {!all}
                playlists = {playlists}
                />
           </div>
           <div className = "custom playlists">
                {/* AUTO GENERATED MINI PLAYLISTS WITH SIMILAR VIBES */}
           </div>
           <div>
                {/* ADD PLAYLIST*/}
                <button onClick = {() => {newplaylist()}}> <img className = "small" src = {plus} /> </button>
           </div>
        </div>
    );
    function toggle(){ 
        setAll(prev=> !prev)
    }
    function newplaylist(){ 
        //NEW PLAYLIST ADDING 
    }
}