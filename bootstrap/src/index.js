import $ from 'jquery';
import Keycloak from "keycloak-js";
import './scss/styles.scss';
import * as bootstrap from 'bootstrap'


const keycloak = new Keycloak({
    url: window.location.origin + "/auth",
    realm: 'app',
    clientId: 'app',
});

function setupTabs() {
    const triggerTabList = document.querySelectorAll('#mainMenu button')
    console.log(triggerTabList);
    triggerTabList.forEach(triggerEl => {
        const tabTrigger = new bootstrap.Tab(triggerEl)
        const mainDiv = document.querySelector("#mainMenuContent");

        triggerEl.addEventListener('click', event => {
            event.preventDefault()
            console.log(triggerEl.id);
            if (triggerEl.id == "home-tab") {
                mainDiv.innerHTML = "This is home"
            }
            if (triggerEl.id == "category-tab") {
                mainDiv.innerHTML = "These are the categories"
            }
            tabTrigger.show()
        })
    })
}

keycloak.init({onLoad: 'login-required'})
.then((authenticated) => {
    if (!authenticated) {
        console.log("User not authenticated - reloading page...");
        window.location.reload()
    } else {
        console.log("User authenticated");

        $("#main").load("main.html", setupTabs);

        console.log("Set up token refresher");
        setInterval(() => {
            keycloak.updateToken(250)
            .then(() => {
                console.log("Token refreshed");
            })
            .catch(() => {
                console.error("Failed to refresh token");
            })
        }, 250000)
    }
})
.catch((error) => {
    console.log("There was a problem initializing the Keycloak adapter!");
});

