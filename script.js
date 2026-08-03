/* ===== MENU LATERAL ===== */

function toggleMenu(){

    const menu = document.getElementById("side-menu");
    const button = document.getElementById("menu-btn");

    if(!menu) return;


    menu.classList.toggle("open");


    if(menu.classList.contains("open")){

        if(button){
            button.style.display = "none";
        }

    } else {

        if(button){
            button.style.display = "block";
        }

    }

}



/* ===== RECHERCHE ===== */

const form = document.getElementById("searchForm");
const input = document.getElementById("searchInput");


if(form && input){


    form.addEventListener("submit", function(e){

        e.preventDefault();


        const recherche = input.value.toLowerCase().trim();

        const articles = document.querySelectorAll(".card");


        articles.forEach(function(article){


            const texte = article.innerText.toLowerCase();


            if(recherche === "" || texte.includes(recherche)){


                article.style.display = "block";


            } else {


                article.style.display = "none";


            }


        });


    });


}



/* ===== MODE SOMBRE ===== */


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
