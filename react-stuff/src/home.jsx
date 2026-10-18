import { useEffect, useRef } from 'react'
import './index.css'
import Animation from './animation.jsx'
import { motion } from 'framer-motion'

// static image assets for sections and decorative grid 34-7 = 27 imgs
import left from "./assets/left.PNG"
import right from "./assets/right.PNG"
import chest from "./assets/chest.PNG"
import couch from "./assets/couch.PNG"
import cover from "./assets/cover.PNG"
import fish3 from "./assets/fish-3.PNG"
import fish from "./assets/fish.PNG"
import floor1 from "./assets/floor-1.PNG"
import floor2 from "./assets/floor-2.PNG"
import floor3 from "./assets/floor-3.PNG"
import floor4 from "./assets/floor-4.PNG"
import grate1 from "./assets/grate-1.PNG"
import grate2 from "./assets/grate-2.PNG"
import grate3 from "./assets/grate-3.PNG"
import grate4 from "./assets/grate-4.PNG"
import greyfloor1 from "./assets/grey-floor-1.PNG"
import greyfloor3 from "./assets/grey-floor-3.PNG"
import greywall2 from "./assets/grey-wall-2.PNG"
import human2 from "./assets/human-2.PNG"
import human from "./assets/human.PNG"
import locker from "./assets/locker.PNG"
import tank from "./assets/tank.PNG"
import wall2 from "./assets/wall-2.PNG"
import wall3 from "./assets/wall-3.PNG"
import wallblank from "./assets/wall-blank.PNG"
import wallclosed from "./assets/wall-closed.PNG"
import wallcloser from "./assets/wall-closer.PNG"
import wall from "./assets/wall.PNG"

// characters for the main title animation
var letters = ["1", "8", "6", "9", "A", "C"]

// asset list for the bottom randomized deco gallery
var all = [wall, wallcloser, wallclosed, wallblank, wall3, wall2, greywall2, greyfloor3, greyfloor1, floor4, floor3, floor2, floor1, grate4, grate3, grate2, grate1, tank, locker, human, human2, fish, fish3, cover, couch, chest]

export default function Home() {
  // DOM references for instant scroll and section navigation
  const topRef = useRef(null)
  const nextSection = useRef(null)

  // reset window position to top on initial page mount
  useEffect(function() {
    if (topRef.current) {
      topRef.current.scrollIntoView({ behavior: "instant", block: "start" })
    }
  }, [])

  // smooth scroll handler triggered by the CTA button
  function scrollPage() {
    if (nextSection.current) {
      nextSection.current.scrollIntoView({ behavior: "smooth" })
    }
  }

  return (
    <div ref={topRef}>
      {/* primary viewport hero section */}
      <motion.div
        className="column"
        initial={{ opacity: 1, y: 150 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.1 }}
        transition={{ duration: 0.7 }}
      >
        <div className="content">
          <div className="row">
            {/* render title characters with staggered entrance delay */}
            {letters.map(function(char, idx) {
              return (
                <motion.span
                  key={idx}
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: false }}
                  transition={{ duration: 0.2, delay: 0.3 + (idx * 0.1) }}
                  style={{ display: "inline-block" }}
                >
                  {char}
                </motion.span>
              )
            })}
          </div>

          <div className="mini">
            <p> The offline and online music player! </p>
            <div className="flex_row">
              {/* navigate down to info */}
              <button onClick={scrollPage}>
                Let's go!
              </button>
            </div>
          </div>
        </div>

        {/* background animation component */}
        <Animation />
      </motion.div>

      {/* project info, requirements, and setup guide */}
      <div ref={nextSection}>
                {/* install guide for the terminal app */}
        <motion.div
          className="biggie install"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: false, amount: 0.2 }}
          transition={{ duration: 0.6 }}
        >
          <h1> Install the player! </h1>

          <h2> Mac / Linux </h2>
          <pre className="code">{`brew install --cask vlc
          brew trust mrpeng4/tap
          brew tap mrpeng4/tap
          brew install ac1869
          1869ac`}</pre>

          <h2> Windows </h2>
          <p> 1. Install Python 3.12 or newer (tick "Add Python to PATH") </p>
          <p> 2. Install the 64-bit VLC media player from videolan.org </p>
          <p> 3. Open a terminal in the project folder and run: </p>
          <pre className="code">{`pip install -r requirements.txt
          python main.py`}</pre>
        </motion.div>
        <motion.div
          className="biggie"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: false, amount: 0.2 }}
          transition={{ duration: 0.6 }}
        >
          <div className="row reverse">
            <div>
              <h2 className="stack"> Currently a work in progress! </h2>
            </div>
            <img className="ugh" src={left} />
          </div>
        </motion.div>

        <motion.div
          className="biggie"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: false, amount: 0.2 }}
          transition={{ duration: 0.6 }}
        >
          <div className="row">
            <div>
              <h2 className="stack"> Right now the app is only avaiable offline on your terminal! It's compatible with Mac, Linux, and Windows! </h2>
            </div>
            <img className="ugh" src={right} />
          </div>
        </motion.div>

        <motion.div
          className="biggie"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: false, amount: 0.2 }}
          transition={{ duration: 0.6 }}
        >
          <div className="row reverse">
            <div>
              <h2 className="stack"> You can install the application by going to this <a href="https://github.com/mrpeng4/1869AC">repository</a> and cloning it! </h2>
            </div>
            <img className="ugh" src={left} />
          </div>
        </motion.div>

        <motion.div
          className="biggie"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: false, amount: 0.2 }}
          transition={{ duration: 0.6 }}
        >
          <div className="row">
            <div>
              <h2 className="stack"> You also need to have python and VLC media player installed! </h2>
            </div>
            <img className="ugh" src={right} />
          </div>
        </motion.div>
      </div>

      {/* randomized decorative sprite footer */}
      <div>
        {[...all].sort(() => Math.random() - 0.5)
        .map((img,index) => (
          <img
            className = "icon"
            key = {index}
            src = {img}
          />
        ))}
      </div>
    </div>
  )
}