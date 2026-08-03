const bouton = document.getElementById("darkMode");
const boutonMenu = document.getElementById("darkModeMenu");


function changerMode() {

    document.body.classList.toggle("sombre");

    if (document.body.classList.contains("sombre")) {

        bouton.textContent = "☀️ Mode clair";

        if (boutonMenu) {
            boutonMenu.textContent = "☀️ Mode clair";
        }

        localStorage.setItem("theme", "sombre");

    } else {

        bouton.textContent = "🌙 Mode sombre";

        if (boutonMenu) {
            boutonMenu.textContent = "🌙 Mode sombre";
        }

        localStorage.setItem("theme", "clair");

    }

}


bouton.addEventListener("click", changerMode);


if (boutonMenu) {
    boutonMenu.addEventListener("click", changerMode);
}


// Garde le mode quand on change de page

if (localStorage.getItem("theme") === "sombre") {

    document.body.classList.add("sombre");

    bouton.textContent = "☀️ Mode clair";

    if (boutonMenu) {
        boutonMenu.textContent = "☀️ Mode clair";
    }

}
