



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
       if(req == 'Compiling Completed'){
         document.getElementById('output').style.backgroundColor = '#68CD86'
         document.getElementById('output').style.borderLeft = '5px solid green '
       }
       else {
         document.getElementById('output').style.backgroundColor = '#E54D42'
         document.getElementById('output').style.borderLeft = '5px solid red '
       }
       document.getElementById('output').style.display = 'inline-block'
        document.getElementById('output').innerHTML = "RESULT: \n" + req;
     });
  });
});