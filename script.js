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



// ===== MENU LATERAL =====

function toggleMenu(){

    const menu = document.getElementById("side-menu");
    const button = document.getElementById("menu-btn");

    menu.classList.toggle("open");

    if(menu.classList.contains("open")){

        button.style.display = "none";

    } else {

        button.style.display = "block";

    }

}



// ===== MODE SOMBRE =====

const darkButton = document.getElementById("darkModeMenu");


if(darkButton){

    darkButton.addEventListener("click", function(){

        document.body.classList.toggle("sombre");


        if(document.body.classList.contains("sombre")){

            darkButton.textContent = "Mode clair";

        } else {

            darkButton.textContent = "Mode sombre";

        }

    });

}



// ===== RECHERCHE =====

const form = document.getElementById("searchForm");
const input = document.getElementById("searchInput");
const articles = document.querySelectorAll(".card");


if(form){

    form.addEventListener("submit", function(e){

        e.preventDefault();


        let recherche = input.value.toLowerCase().trim();


        articles.forEach(function(article){

            let texte = article.innerText.toLowerCase();


            if(recherche === "" || texte.includes(recherche)){

                article.style.display = "block";

            } else {

                article.style.display = "none";

            }


        });


    });

}



const darkButton = document.getElementById("darkModeMenu");

console.log(darkButton);

darkButton.addEventListener("click", function(){

    console.log("CLIC MODE SOMBRE");

    document.body.classList.toggle("sombre");

});
