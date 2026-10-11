import { useState , useEffect, useRef} from 'react'
import wall from "./assets/wall.PNG"
import plus from "./assets/cover.PNG"
const playlist_array = [["song", "path", "./assets/cover.PNG"],["othersong", "path2", "./assets/cover.PNG"], ["how usefless", "path3", "./assets/cover.PNG"], ["beautiful", "path4", "./assets/cover.PNG"],["song", "path", "./assets/cover.PNG"],["othersong", "path2", "./assets/cover.PNG"], ["how usefless", "path3", "./assets/cover.PNG"], ["beautiful", "path4", "./assets/cover.PNG"],["song", "path", "./assets/cover.PNG"],["othersong", "path2", "./assets/cover.PNG"], ["how usefless", "path3", "./assets/cover.PNG"], ["beautiful", "path4", "./assets/cover.PNG"]]

function Playlists({ifSlice}){//obj
    const new_array = ifSlice? playlist_array.slice(0,8):playlist_array 
    {/* PLS ADD PLAYLIST EXTRACTION LOGIC!*/}
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
    return(
        <div className = "container">
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
                <button onClick = {() => {newplaylist()}}> <img className = "medium" src = {plus} /> </button>
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