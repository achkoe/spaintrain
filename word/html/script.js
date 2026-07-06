window.addEventListener("load", (event) => {
  console.log("page is fully loaded");
  document.querySelectorAll(".bookmark").forEach((element) => {
    console.log(element);
    element.addEventListener("click", function (event) {
      console.log(event.target.id);
      console.log(element);
      let e = document.getElementById(event.target.id);
      e.classList.add("highlight");
      setTimeout(() => {
        e.classList.remove("highlight");
      }, 2000);
      localStorage.setItem("bookmark", event.target.id);
    });
  });
  document
    .getElementById("gotopage")
    .addEventListener("click", function (event) {
      console.log("goto");
      let bookmark = localStorage.getItem("bookmark");
      console.log(bookmark);
      let e = document.getElementById(bookmark);
      let url = location.href;
      location.href = "#" + bookmark;
      history.replaceState(null,null,url);   //Don't like hashes. Changing it back.
      e.classList.add("highlight");
      setTimeout(() => {
        e.classList.remove("highlight");
      }, 2000);
    });
  document.querySelectorAll("hr").forEach((element) => {
    element.title = "Click to save position";
  });
});
function bookmark() {}
