import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import './index.css'

var team = [
  { name: "Mishika", github: "justmishchief" },
  { name: "pillu", github: "mrpeng4" },
  { name: "tanmay", github: "YOBO-DANCE" },
  { name: "jyoshita nair", github: "jyoshitanair" }
]

export default function About() {
  const Navigate = useNavigate()
  return (
    <div id = "overall">
        <h1 style = {{paddingTop: "3em", color: "white"}}> About! </h1>

        <div className = "instructions">
            <h2> What is 1869AC? </h2>
            <p> A music player that lives in your terminal, with an online site on the way! </p>
            <p> The terminal player is fully working: playlists, virtual playlists, shuffle, repeat, skip, rewind and much more, on Mac, Linux and Windows. </p>
            <p> The whole project is still a work in progress. Soon the website will play music and save your playlists too. </p>

            <h2> Meet the team </h2>
        </div>

        <div className = "team">
            {team.map(function(person, idx) {
              return (
                <motion.a
                  className = "member"
                  key = {idx}
                  href = {"https://github.com/" + person.github}
                  target = "_blank"
                  rel = "noreferrer"
                  initial = {{ opacity: 0, y: 30 }}
                  whileInView = {{ opacity: 1, y: 0 }}
                  whileHover = {{ scale: 1.05 }}
                  viewport = {{ once: true }}
                  transition = {{ duration: 0.5, delay: idx * 0.15 }}
                >
                  {person.name}
                </motion.a>
              )
            })}
        </div>

        <button style = {{fontSize: "max(2vw, 16px)", margin: "3em 0"}} onClick = {() => Navigate("/")}> Go back Home </button>
    </div>
  );
}