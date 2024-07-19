import $ from 'jquery';
import Keycloak from "keycloak-js";


const keycloak = new Keycloak({
    url: window.location.origin + "/auth",
    realm: 'app',
    clientId: 'app',
});

keycloak.init({onLoad: 'login-required'})
.then((authenticated) => {
    if (!authenticated) {
        console.log("User not authenticated - reloading page...");
        window.location.reload()
    } else {
        console.log("User authenticated");

        $("#main").load("main.html");
        // document.body.innerHTML = "Logged in!";

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