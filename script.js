// MODE SOMBRE

const bouton = document.getElementById("darkMode");
const boutonMenu = document.getElementById("darkModeMenu");


function changerMode() {

    document.body.classList.toggle("sombre");


    if (document.body.classList.contains("sombre")) {

        if (bouton) {
            bouton.textContent = "☀️ Mode clair";
        }

        if (boutonMenu) {
            boutonMenu.textContent = "☀️ Mode clair";
        }

        localStorage.setItem("theme", "sombre");

    } else {

        if (bouton) {
            bouton.textContent = "🌙 Mode sombre";
        }

        if (boutonMenu) {
            boutonMenu.textContent = "🌙 Mode sombre";
        }

        localStorage.setItem("theme", "clair");

    }

}


// Bouton dans le header
if (bouton) {
    bouton.addEventListener("click", changerMode);
}


// Bouton dans le menu
if (boutonMenu) {
    boutonMenu.addEventListener("click", changerMode);
}



// Garde le mode sombre après changement de page

if (localStorage.getItem("theme") === "sombre") {

    document.body.classList.add("sombre");


    if (bouton) {
        bouton.textContent = "☀️ Mode clair";
    }


    if (boutonMenu) {
        boutonMenu.textContent = "☀️ Mode clair";
    }

}
