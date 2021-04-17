// jshint esversion:6

var express = require('express')
var ejs = require('ejs')
var bodyParser = require('body-parser')

const app = express()
const fs = require('fs')
const {PythonShell} =require('python-shell');

app.set('view engine', 'ejs')
app.use(express.static("public"));
app.use(express.json())
app.use(express.urlencoded({extended: true}))

app.get("/", (req, res) => {
    res.render("editor");
})



app.post('/compile', callName);
  
function callName(req, res) {
    
    fs.writeFileSync('hello.tiny', req.body.data )

   
    let options = {
        mode: 'text',
        pythonOptions: ['-u'], // get print results in real-time
          scriptPath: '', //If you are having python_test.py script in same folder, then it's optional.
        args: [req.body.lang] //An argument which can be accessed in the script using sys.argv[1]
    };
      
    
    let options2 = {
        mode: 'text',
        pythonOptions: ['-u'], // get print results in real-time
          scriptPath: '', //If you are having python_test.py script in same folder, then it's optional.
        args: [req.body.data] //An argument which can be accessed in the script using sys.argv[1]
    };

    PythonShell.run('lex.py', options2, function (err, result){
        if(result == null){
            var file = ""
            var ext = ""
            if(req.body.lang == 'C'){
                ext = '.c';
            }
            else if(req.body.lang == 'C++'){
                ext = '.cpp';
            }
            else if(req.body.lang == 'Java'){
                ext = '.java';
            }
            else ext = '.py';

            if(req.body.lang == 'C' || req.body.lang == 'C++')
                file = 'parser_check.py';
            else file = 'parser_check_java.py';
            PythonShell.run(file, options2, function (err, result){
                if(result == null){
                    PythonShell.run('teenytiny.py', options, function (err, result){
                        if(result == null){
                            res.send("Compilation Error");
                        }
                        else{
                            var output = "";
                            fs.readFile('out' + ext, function read(err, data) {
                                if (err) {
                                    throw err;
                                }
                                output = data.toString();
                            
                                // Invoke the next step here however you like
                                // Put all of the code here (not the best solution)
                                // processFile(content);   // Or put the next step in a function and invoke it
                                console.log(output)
                                console.log('/compile/' + result.toString());
                                res.send({result: result.toString(),
                                    output: output
                                });
                            })
                            
                        }
                    });
                    
                }
                else{
                    res.send({result: result.toString()});
                }
            })
        }
        else{
            
            res.send({result: result.toString()});
        }
    })

    
}

app.get('/compile/:result', (req, res) => {
    res.render('compile', {output: req.params.result})
})

app.listen("3000", () => {
    console.log("Server running at 3000")
})