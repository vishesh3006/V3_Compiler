$('div[contenteditable=true]').keydown(function(e) {
  // trap the return key being pressed
  if (e.keyCode == 13) {
    // insert 2 br tags (if only one br tag is inserted the cursor won't go to the second line)
    document.execCommand('insertHTML', false, '<br><br>');
    // prevent the default behaviour of return key pressed
    return false;
  }
});

// $(document).on('keyup', '#content', function(e){
//   //detect 'tab' key
//   if(e.keyCode == 9){
//     //add tab
//     document.execCommand('insertHTML', false, '&#009');
//     //prevent focusing on next element
//     e.preventDefault()   
//   }
// });

document.getElementById("content").innerHTML =
  localStorage["text"] || "This text is automatically saved every second :) "; // default text

setInterval(function() {
  // fuction that is saving the innerHTML of the div
  localStorage["text"] = document.getElementById("content").innerHTML; // content div
  console.log(document.getElementById("content").innerText)
}, 1000);

$('div[contenteditable=true]').on('keydown', function(e){
  if(e.keyCode == 9){
      e.preventDefault();
      document.execCommand('insertHTML', false, '&#009');
  }
}).css('white-space', 'pre-wrap');

$(document).ready( () => {
  $("#button").on("click", () => {
    var data = document.getElementById("content").innerText;
    var lang = document.getElementById("language").value
     $.ajax({
      url: "/compile",
      type: "POST",
      data: {data: data, lang: lang},
      success: function() {
        console.log("Yes")
      },
     }).then((req, res) =>{
      //  console.log(req);
       if(req.result == 'Result: Compiling Completed'){
         document.getElementById('output').style.backgroundColor = '#68CD86'
         document.getElementById('output').style.borderLeft = '5px solid green'

        //  document.getElementById('content').style.minHeight = '40vh';
         document.getElementById('content').style.height = '95%';
         document.getElementById('content').style.width = '95%';
         document.getElementById('compiled_output').style.height = '95%';
        //  document.getElementById('content').style.width = '50vw'
         document.getElementById('content').style.overflowY = 'scroll';
        //  document.getElementById('compiled_output').style.display = 'inline';
         document.getElementById('compiled_output').innerText = req.output;
        //  document.getElementById('compiled_output').style.minHeight = '40vh';
        //  document.getElementById('compiled_output').style.width = '50vw';
         document.getElementById('compiled_output').style.overflowY = 'scroll';
         document.getElementById('input_compile_nav').innerText = 'SOURCE CODE';
         document.getElementById('input_nav').style.display = 'block'
         document.getElementById('compile_nav').innerText = 'OUTPUT LANGUAGE: ' + lang;
         document.getElementById('output_nav').style.display = 'block'
         document.getElementById('compile_nav').style.paddingLeft = '10px'
         document.getElementById('INPUT').style.width = '50vw'
         document.getElementById('INPUT').style.height = '79%'
         document.getElementById('INPUT').style.top = '95px'
         document.getElementById('OUTPUT').style.width = '50vw'
         document.getElementById('OUTPUT').style.display = 'block'
       }
       else {
        document.getElementById('INPUT').style.top = '95px'
         document.getElementById('output').style.backgroundColor = '#E54D42'
         document.getElementById('output').style.borderLeft = '5px solid red'
        //  document.getElementById('compiled_output').style.display = 'none';
        //  document.getElementById('output_nav').style.display = 'none';
        //  document.getElementById('content').style.minHeight = '100%';
        //  document.getElementById('content').style.height = 'max-content';
        //  document.getElementById('compiled_output').innerText = '';
        //  document.getElementById('content').style.overflowY = 'visible';
        document.getElementById('OUTPUT').style.display = 'none'
        document.getElementById('input_nav').style.display = 'none'
        document.getElementById('INPUT').style.width = '100vw'
        document.getElementById('content').style.width = '100%';
        document.getElementById('content').style.height = '100%';
        document.getElementById('INPUT').style.height = '84%'
       }
        document.getElementById('output').style.display = 'block'
        document.getElementById('output').innerHTML =  req.result;
     });
  });
});

function copyToClipboard(element) {
  var $temp = $("<textarea>");
  $("body").append($temp);
  $temp.val($(element).text()).select();
  document.execCommand("copy");
  $temp.remove();
}

function copyCode(element) {
  var $temp = $("<textarea>");
  
  var brRegex = /<br\s*[\/]?>/gi;
  $("body").append($temp);
  $temp.val($(element).html().replace(brRegex, "\r\n").replace( /&lt;/g, "<" ).replace( /&gt;/g, ">" ).replace( /&amp;/g, "&" )).select();
  document.execCommand("copy");
  $temp.remove();
}

function ancher(element){
  $(element)[0].click();
}