const bouton = document.getElementById("darkMode");

// Quand on clique sur le bouton
bouton.addEventListener("click", function () {

    document.body.classList.toggle("sombre");

    // Change le texte du bouton
    if (document.body.classList.contains("sombre")) {
        bouton.textContent = "☀️ Mode clair";
        localStorage.setItem("theme", "sombre");
    } else {
        bouton.textContent = "🌙 Mode sombre";
        localStorage.setItem("theme", "clair");
    }

});


// Garde le choix après un changement de page
if (localStorage.getItem("theme") === "sombre") {
    document.body.classList.add("sombre");
    bouton.textContent = "☀️ Mode clair";
}
