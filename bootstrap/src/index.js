import $ from 'jquery';
import Keycloak from "keycloak-js";
import './scss/styles.scss';
import * as bootstrap from 'bootstrap'


const keycloak = new Keycloak({
    url: window.location.origin + "/auth",
    realm: 'app',
    clientId: 'app',
});

async function getCategories() {
    const r = await fetch(window.location.origin + "/backend/category/1",
        {
            headers: {
                Accept: 'application/json',
                Authorization: `Bearer ${keycloak.token}`
            }
        }
    );
    return r.json();
}


function setupTabs() {

    const homeTab = document.querySelector("#home-tab");
    const categoryTab = document.querySelector("#category-tab");

    const homeDiv = document.querySelector("#home");
    const categoryDiv = document.querySelector("#category");

    homeTab.addEventListener('click', event => {
        event.preventDefault();
        homeDiv.innerHTML = "Home set by button!"
    });

    categoryTab.addEventListener('click', event => {
        event.preventDefault();

        const r = getCategories();
        console.log(r);

        categoryDiv.innerHTML = "Category set by button!"
    });
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

