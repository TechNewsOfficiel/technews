// =========================
// MENU LATERAL
// =========================

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





// =========================
// MODE SOMBRE
// =========================


document.addEventListener("DOMContentLoaded", function(){


    const darkButton = document.getElementById("darkModeMenu");


    if(darkButton){


        darkButton.addEventListener("click", function(){


            document.body.classList.toggle("sombre");



            if(document.body.classList.contains("sombre")){

                darkButton.textContent = "Mode clair";

            }

            else{

                darkButton.textContent = "Mode sombre";

            }


        });


    }



});





// =========================
// RECHERCHE
// =========================


document.addEventListener("DOMContentLoaded", function(){


    const form = document.getElementById("searchForm");

    const input = document.getElementById("searchInput");

    const articles = document.querySelectorAll(".card");



    if(form && input){


        form.addEventListener("submit", function(e){


            e.preventDefault();



            let recherche = input.value.toLowerCase().trim();



            articles.forEach(function(article){


                let texte = article.innerText.toLowerCase();



                if(recherche === "" || texte.includes(recherche)){


                    article.style.display = "block";


                }

                else{


                    article.style.display = "none";


                }


            });



        });



    }



});


// =========================
// SYSTEME DE FAVORIS
// =========================


document.addEventListener("DOMContentLoaded", function(){


const buttons = document.querySelectorAll(".favorite-btn");


let favoris = JSON.parse(localStorage.getItem("favoris")) || [];



buttons.forEach(function(button){


let titre = button.dataset.title;
let lien = button.dataset.link;



// Vérifie si déjà en favoris

let existe = favoris.some(function(article){

return article.link === lien;

});



if(existe){

button.textContent = "★ Retirer des favoris";

button.classList.add("active");

}





button.addEventListener("click", function(){



let index = favoris.findIndex(function(article){

return article.link === lien;

});



if(index === -1){


// Ajouter

favoris.push({

title:titre,

link:lien

});


button.textContent="★ Retirer des favoris";

button.classList.add("active");


}

else{


// Retirer

favoris.splice(index,1);


button.textContent="☆ Ajouter aux favoris";

button.classList.remove("active");


}



localStorage.setItem("favoris", JSON.stringify(favoris));



});


});


});

function aimerArticle(button){


    let article = button.closest(".card");


    let titre = article.querySelector("h3").innerText;


    let favoris = JSON.parse(localStorage.getItem("favoris")) || [];


    if(!favoris.includes(titre)){


        favoris.push(titre);


        localStorage.setItem(
            "favoris",
            JSON.stringify(favoris)
        );

    }



    button.classList.add("anim");


    setTimeout(function(){

        button.classList.remove("anim");

    },400);



    button.innerHTML="👍 <span>Vous aimez cet article</span>";

}

function retirerFavori(button){

    let article = button.closest(".card");

    let titre = article.querySelector("h3").innerText;


    let favoris = JSON.parse(localStorage.getItem("favoris")) || [];


    favoris = favoris.filter(function(item){

        return item !== titre;

    });


    localStorage.setItem(
        "favoris",
        JSON.stringify(favoris)
    );


    let like = article.querySelector(".like-btn");


    like.innerHTML="👍 <span>J'aime</span>";

    like.style.background="#22c55e";

}

// ===============================
// STATISTIQUES DU SITE
// ===============================


// Création des données si elles n'existent pas
if(localStorage.getItem("vues") === null){
    localStorage.setItem("vues", 0);
}

if(localStorage.getItem("likes") === null){
    localStorage.setItem("likes", 0);
}

if(localStorage.getItem("utilisateurs") === null){
    localStorage.setItem("utilisateurs", 0);
}

if(localStorage.getItem("articles") === null){
    localStorage.setItem("articles", 0);
}



// ===============================
// AJOUT D'UNE VUE
// ===============================

function ajouterVue(){

    let vues = Number(localStorage.getItem("vues"));

    vues++;

    localStorage.setItem("vues", vues);
}



// ===============================
// AJOUT D'UN UTILISATEUR
// ===============================

function ajouterUtilisateur(){

    let dejaVu = localStorage.getItem("visiteur");

    if(dejaVu === null){

        let utilisateurs =
        Number(localStorage.getItem("utilisateurs"));

        utilisateurs++;

        localStorage.setItem(
            "utilisateurs",
            utilisateurs
        );

        localStorage.setItem(
            "visiteur",
            "oui"
        );
    }
}



// ===============================
// SYSTEME DE LIKE
// ===============================

function aimerArticle(){

    let aimeDeja =
    localStorage.getItem("aime");

    if(aimeDeja === null){

        let likes =
        Number(localStorage.getItem("likes"));

        likes++;

        localStorage.setItem(
            "likes",
            likes
        );

        localStorage.setItem(
            "aime",
            "oui"
        );

        alert("Merci pour votre 👍 !");

    }else{

        alert("Vous avez déjà aimé cet article.");

    }

}



// ===============================
// AFFICHAGE DES STATISTIQUES
// ===============================

function afficherStatistiques(){


    let vues =
    document.getElementById("vues");


    let likes =
    document.getElementById("likes");


    let utilisateurs =
    document.getElementById("utilisateurs");



    if(vues){

        vues.innerHTML =
        localStorage.getItem("vues");

    }


    if(likes){

        likes.innerHTML =
        localStorage.getItem("likes");

    }


    if(utilisateurs){

        utilisateurs.innerHTML =
        localStorage.getItem("utilisateurs");

    }

}



// ===============================
// LANCEMENT AUTOMATIQUE
// ===============================


ajouterVue();

ajouterUtilisateur();

afficherStatistiques();
