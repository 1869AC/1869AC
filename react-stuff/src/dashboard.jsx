import { useState , useEffect, useRef} from 'react'
import wall from "./assets/wall.PNG"
import plus from "./assets/cover.PNG"
import {supabase} from './main.jsx'
import { useNavigate} from 'react-router-dom'
import toast from 'react-hot-toast';
const MREOW = import.meta.env.VITE_API_URL

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
    const new_array = ifSlice? playlist_array.slice(0,8):playlist_array 
    {/* PLS ADD PLAYLIST EXTRACTION LOGIC!*/}
    pythongetterofsongs()
        return(
        <>
            {new_array.map((song_name, index)=> {
            return(
                <div key = {index}>
                    <img className = "small" src = {url(song_name[2])}/>
                    <p>{song_name[0]}</p>
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
    useEffect(() => {
        //GUEST
        async function guestFetcher(){
            try{
                const response = await Promise(
                    [fetch("/GIMMETHOSESONGS/0")]
                );
                const data = response[0]
                if (!data.ok){
                    throw new Error("COULD NOT LOAD PLAYLIST UNO")
                }
                const first = await data.json()
                setPlaylists(first)
            }catch(e){
                toast.error(e.message)
            }
        }
        // AUTH
        async function fetcher() { 
            try{
                const {response, error} = await supabase.auth.getUser()
                if (!response.user.data || !response.user ){
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
                toast.error(error)
            }
            else if (response2.data && response2.data.songs){
                const formattedSongs = response2.data.map(song => [
                    song.name || "Untitled",
                    song.dir || "missing path",
                    plus
                ])
                setPlaylists(formattedSongs)
        }}
        fetcher()
        guestFetcher()
    }, []);
    return(
        <div className = "container">
            <h1> THIS SITE IS EXPERIMENTAL. INFERFACE ON THIS PAGE DOES NOT WORK AT THE MOMENT!</h1>
            <div className = "menu_row">
                <p> Playlists </p>
                <button style ={{color: "white", backgroundColor: "MediumSeaGreen", transform: "scale(1.5)", marginBottom: "3em"}} onClick = {toggle}> {!all? "Show all": "Condense"}</button>
            </div>
           <div className = "playlists">
                <Playlists ifSlice = {!all}/>
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