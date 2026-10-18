import { useState , useEffect, useRef} from 'react'
import wall from "./assets/wall.PNG"
import plus from "./assets/cover.PNG"
import {supabase} from './main.jsx'
import { useNavigate} from 'react-router-dom'
import toast from 'react-hot-toast';
const MREOW = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "")
const mode =  localStorage.getItem("mode") || "guest"
function Playlists({ifSlice, playlists}){//obj
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
    const [selected, setSelected] = useState(null);
    const [song, setSong] = useState(null);
    useEffect(() => { 
        //GUEST
        async function guestFetcher(){
            try{
                const response = await fetch(
                    `${MREOW}/GIMMETHOSESONGS/0`
                );
                if (!response.ok){
                    throw new Error("COULD NOT LOAD PLAYLIST UNO")
                }
                //ERROR
                const data = await response.json()
                if (!Array.isArray(data)){
                    //ERROR HOW IS THIS HAPPENING?
                    throw new Error("yeah this ones never happening?")
                }
                setPlaylists(data);
            }catch(e){
                toast.error(e.message) //ERROR HERE DOC TYPE THINGY.
            }
        }
        // AUTH
        async function fetcher() { 
            let user 
            try{
                const {data, error} = await supabase.auth.getUser()
                if (error){
                    toast.error(error.message)
                    return;
                } 
                if (!data.user || !data ){
                    // well dang how did you get here??
                    Navigate('/signup')
                    toast.error("HOW DID YOU GET HERE?!")
                    return
                }
                user = data.user
            }catch(e){
                toast.error(e)
            }
            const {data, error2} = await supabase.from("users").select("songs").eq("id", user.id).maybeSingle(); 
            if(error2){
                toast.error(error.message)
                return;
            }
            if (data && data.songs){
                const songs = data.songs;
                if (Array.isArray(songs)){
                    setPlaylists(songs)
                }else{
                    setPlaylists([]);
                    toast.error("will also nv happen")
                }
            }
        }
        //CALL MY BS
        fetcher()
    }, []);
    const [text, setText] = useState(true)
    return(
        <div className = "container">
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
           <div>
            <button onClick = {playsong}> {text? "Play Songs" : "Turn Off Songs"} </button>
            <p> (By default it tries to play what you were last listening on the terminal! Since that's not always possible sometimes it plays nothing!)</p>
            <audio
                key = {song}
                controls //turns on
                src = {
                    song != null? `${MREOW}/PLAYSONG/${song.playlist_index}/${song.song_index}` : undefined
                }
            />
           </div>
        </div>
    );
    async function playsong(){
        console.log("CLCK")
            if(text == true){
                console.log("OFFLINE")
                //online make it offline
                setText(false)
                setSong(null)
                return
            }
            try{
                console.log("ONLINE")
                setText(true)
                console.log("HI?")
                const response = await fetch(`${MREOW}/NAMEOFSTUPIDSONG/`);
                if (!response.ok){
                    throw new Error(`HTTPS ERROR:${response.status}`)
                    console.log("BAD HTTPS")
                }
                const curSong = await response.json()
                console.log(curSong)
                    setSong({
                        playlist_index: curSong[1],
                        song_index: curSong[0]
                    });
                    console.log("SET SONG")
                }catch(e){
                    console.log("ERROR")
                    console.log(e)
                    toast.error(e.message)
                }
            }

    }
    function toggle(){ 
        setAll(prev=> !prev)
    }
    function newplaylist(){ 
        //NEW PLAYLIST ADDING 
    }