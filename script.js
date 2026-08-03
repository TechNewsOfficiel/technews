// ===== MENU LATERAL =====

function toggleMenu(){

    const menu = document.getElementById("side-menu");
    const button = document.getElementById("menu-btn");


    menu.classList.toggle("open");


    if(menu.classList.contains("open")){

        button.style.display = "none";

    }
    else{

        button.style.display = "block";

    }

}



// ===== MODE SOMBRE =====

document.addEventListener("DOMContentLoaded", function () {

    const darkButton = document.getElementById("darkModeMenu");

    if (!darkButton) {
        console.log("Bouton mode sombre introuvable");
        return;
    }


    darkButton.addEventListener("click", function () {

        document.body.classList.toggle("sombre");


        if (document.body.classList.contains("sombre")) {

            darkButton.innerText = "Mode clair";

        } else {

            darkButton.innerText = "Mode sombre";

        }

    });

});



const darkButton = document.getElementById("darkModeMenu");

console.log(darkButton);

darkButton.addEventListener("click", function(){

    console.log("CLIC MODE SOMBRE");

    document.body.classList.toggle("sombre");

});
