document.getElementById("content").innerHTML =
  localStorage["text"] || "This text is automatically saved every second :) "; // default text

setInterval(function() {
  // fuction that is saving the innerHTML of the div
  localStorage["text"] = document.getElementById("content").innerHTML; // content div
  console.log(document.getElementById("content").innerText)
}, 1000);



