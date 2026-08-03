const bouton = document.getElementById("darkMode");


bouton.addEventListener("click", function () {

    document.body.classList.toggle("sombre");


    if (document.body.classList.contains("sombre")) {

        bouton.textContent = "☀️ Mode clair";
        localStorage.setItem("theme", "sombre");

    } else {

        bouton.textContent = "🌙 Mode sombre";
        localStorage.setItem("theme", "clair");

    }

});


// Garde le mode choisi après changement de page

if (localStorage.getItem("theme") === "sombre") {

    document.body.classList.add("sombre");
    bouton.textContent = "☀️ Mode clair";

}
