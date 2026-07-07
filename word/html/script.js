window.addEventListener("load", (event) => {
  document.querySelectorAll(".bookmark").forEach((element) => {
    element.addEventListener("click", function (event) {
      let e = document.getElementById(event.target.parentElement.id);
      event.target.classList.add("highlight");
      setTimeout(() => {
        event.target.classList.remove("highlight");
      }, 2000);
      localStorage.setItem("bookmark", e.id);
    });
  });
  document
    .getElementById("gotopage")
    .addEventListener("click", function (event) {
      let bookmark = localStorage.getItem("bookmark");
      console.log(bookmark);
      let e = document.getElementById(bookmark);
      let url = location.href;
      location.href = "#" + bookmark;
      history.replaceState(null, null, url);   //Don't like hashes. Changing it back.
      e.firstChild.classList.add("highlight");
      setTimeout(() => {
        e.firstChild.classList.remove("highlight");
      }, 2000);
    });
  document.querySelectorAll("hr").forEach((element) => {
    element.title = "Click to save position";
  });
});
function bookmark() {}
