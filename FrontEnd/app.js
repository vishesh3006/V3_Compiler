//jshint esversion:6
import express from 'express'
import ejs from 'ejs'
import bodyParser from 'body-parser'


const app = express()

app.set('view engine', 'ejs')
app.use(express.static("public"));
app.use(express.json())
app.use(express.urlencoded({extended: true}))

app.get("/", (req, res) => {
    res.render("editor");
})

app.listen("3000", () => {
    console.log("Server running at 3000")
})