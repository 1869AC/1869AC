import { useState } from 'react'
import Home from './home.jsx'
import {Routes, Route, useNavigate} from 'react-router-dom'
import './index.css'

export default function Features() {
  const Navigate = useNavigate()
  return (
    <div id = "overall">
        <h1 style = {{paddingTop: "3em", color: "white"}}> Features! </h1>
        <div className = "instructions">
            <div>
                <p><b>Music Importer:</b> Scans any directory on your computer for audio files (`.mp3`, `.wav`, `.flac`, `.m4a`, `.ogg`) </p>
                <p> and saves them as custom named playlists.</p>
            </div>
            <p><b>Startup Menu:</b> Displays available playlists on launch for quick selection. </p>
            <p><b>Track Navigation:</b> Next (m) and previous (n) song controls with history shuffle memory.</p>
            <p><b>Volume & Sound Effects:</b> Real-time 10-level volume adjustments (o/p) complete with audio feedback using `pygame.mixer`.</p>
            <p><b>Playback Modes:</b> Shuffle mode (s) and single-track with live visual status symbols.</p>
            <p><b>Terminal UI Dashboard:</b> Renders a progress timeline bar, current date/clock, elapsed vs. total time, and an animated vinyl indicator.</p>
            <p><b>Clean Console Output:</b> Automatically suppresses low-level VLC stderr logging to preserve terminal clean-ups.</p>
            <p><b>Loop functionality:</b> loop key (e) can switch between single song loop and continue playlist.</p>
            <div>
                <p><b>Playlist importer:</b> by putting the path of the directory where all your songs are stored it automatically reads and save it to a </p>
                <p>.py file and then reads it for you and plays the music live from the folder and saves it as a playlist witch you can switch between.</p>
            </div>
            <p><b>Playlist selector:</b> select and choose between your favorite playlists.</p>
            <p><b>Song selector:</b> select and choose between your favorite Songs.</p>
        </div>
        <button style = {{fontSize: "max(2vw, 16px)"}} onClick = {() => Navigate("/")}> Go back Home </button>
    </div>
  );
}