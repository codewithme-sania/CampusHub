// CampusHub JavaScript

// Login button
const loginButton = document.querySelector(".login-btn");

loginButton.addEventListener("click", function () {
    alert("CampusHub Login feature coming soon!");
});


// Explore Opportunities button
const exploreButton = document.querySelector(".primary-btn");

exploreButton.addEventListener("click", function () {
    document.querySelector(".opportunities").scrollIntoView({
        behavior: "smooth"
    });
});


// View Events button
const eventsButton = document.querySelector(".secondary-btn");

eventsButton.addEventListener("click", function () {
    alert("Events section coming soon!");
});


// Opportunity cards
const cards = document.querySelectorAll(".card");

cards.forEach(function (card) {

    card.addEventListener("click", function () {

        const title = card.querySelector("h3").textContent;

        alert("You selected: " + title);

    });

});