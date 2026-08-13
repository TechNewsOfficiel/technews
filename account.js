/* ================================= */
/* ===== AFFICHER LE MOT DE PASSE == */
/* ================================= */

function togglePassword(id, button) {

    const input = document.getElementById(id);

    if (input.type === "password") {

        input.type = "text";

        button.textContent = "🙈";

    } else {

        input.type = "password";

        button.textContent = "👁";

    }

}


/* ================================= */
/* ===== INSCRIPTION ================ */
/* ================================= */

const registerForm = document.getElementById("registerForm");


if (registerForm) {

    registerForm.addEventListener("submit", function(event) {

        event.preventDefault();


        const username =
            document.getElementById("username").value.trim();

        const email =
            document.getElementById("email").value.trim();

        const password =
            document.getElementById("password").value;

        const confirmPassword =
            document.getElementById("confirmPassword").value;

        const message =
            document.getElementById("registerMessage");


        /* Vérification du mot de passe */

        if (password !== confirmPassword) {

            message.textContent =
                "Les mots de passe ne correspondent pas.";

            message.className =
                "form-message error";

            return;

        }


        /* Vérification longueur */

        if (password.length < 8) {

            message.textContent =
                "Le mot de passe doit contenir au moins 8 caractères.";

            message.className =
                "form-message error";

            return;

        }


        /* Démo */

        message.textContent =
            "Compte créé ! Tu peux maintenant te connecter.";

        message.className =
            "form-message success";


        registerForm.reset();


    });

}


/* ================================= */
/* ===== CONNEXION ================== */
/* ================================= */

const loginForm = document.getElementById("loginForm");


if (loginForm) {

    loginForm.addEventListener("submit", function(event) {

        event.preventDefault();


        const email =
            document.getElementById("loginEmail").value.trim();

        const password =
            document.getElementById("loginPassword").value;

        const message =
            document.getElementById("loginMessage");


        if (!email || !password) {

            message.textContent =
                "Veuillez remplir tous les champs.";

            message.className =
                "form-message error";

            return;

        }


        /* Démo */

        message.textContent =
            "Connexion réussie !";

        message.className =
            "form-message success";


    });

}
