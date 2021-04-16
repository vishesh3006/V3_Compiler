
// alert("ssss");
document.getElementById("content").innerHTML =
  localStorage["text"] || "This text is automatically saved every second :) "; // default text

setInterval(function() {
  // fuction that is saving the innerHTML of the div
  
  localStorage["text"] = document.getElementById("content").innerHTML; // content div
  console.log("sss");
  // console.log(document.getElementById("content").innerText)
}, 1000);



$(document).ready( () => {
  $("button").on("click", () => {
    alert("Clicked")
    var data = $("#content").innerText;
    var lang = $( "#language option:selected" ).text();
     $.ajax({
      url: "/compile",
      type: "POST",
      data: {data: data, lang: lang},
      success: function() {
        console.log("Yes")
      },
     });   
  });
});