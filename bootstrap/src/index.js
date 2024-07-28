import $ from 'jquery';
import Keycloak from "keycloak-js";
import './scss/styles.scss';
import * as bootstrap from 'bootstrap'

import { getCategories } from './category';


const keycloak = new Keycloak({
    url: window.location.origin + "/auth",
    realm: 'app',
    clientId: 'app',
});


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

        categoryDiv.innerHTML = "";
        const r = getCategories(keycloak.token);

        const ul = document.createElement("ul");
        r.then((json) => {
            console.log(json);
            for (let cat of json) {
                let li = document.createElement("li");
                li.innerText = cat.name;
                ul.appendChild(li);
            }
        });

        categoryDiv.appendChild(ul);
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

