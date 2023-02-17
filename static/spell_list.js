const dropZone = document.getElementById("target")

function allowDrop(evt) {
    evt.preventDefault();
}

function drag(evt) {
    evt.dataTransfer.setData("text", evt.target.id);
}

function drop(evt) {
    evt.preventDefault();
    let data = evt.dataTransfer.getData("text");

    toggleDropZoneClass()

    dropZone.appendChild(document.getElementById(data));
}

function start() {
    const allSpellCards = document.getElementById("avail-spells");

    const spellCards = allSpellCards.children

    for (card of spellCards){
        card.addEventListener("dragstart", drag);
    }

    dropZone.addEventListener("dragover", allowDrop)
    dropZone.addEventListener("drop", drop)

    const clearButton = document.getElementById('clear-button')
    clearButton.addEventListener("click", clearSpellList)
}

window.addEventListener("DOMContentLoaded", start)

function compare(a, b) {
    if (a.dataset.listPosition < b.dataset.listPosition)
        return -1;
    if (a.dataset.listPosition > b.dataset.listPosition)
        return 1;
    return 0;
}
  
// Function to sort spells
function clearSpellList() {
    //reset drop-zone class
    toggleDropZoneClass()
    // get all spells
    const allSpellCards = document.querySelectorAll("[data-list-position]");

    console.log(allSpellCards)
    //make an array of all spells
    let spellArray = Array.from(allSpellCards).sort(compare);

    spellArray.forEach(elem => document.querySelector("#avail-spells").appendChild(elem));
}

function toggleDropZoneClass(){
    dropZone.classList.toggle('empty-list')
    dropZone.classList.toggle('has-items')
}

// TODO:
// Get clear list button working
//      on click it should clear the list of spells and reset their positions
// Figure out how to save spells into a spell list on the server
//      I'm thinking that we can get all the children from the DOM elements in target
//      and grab their id's put them in a list, and using axios send that list to the server
//      then we process the request server side, and save the spell list in the database
// Should refactor these functions into OOP
// Should refactor server-side spell list functions into OOP, put them as methods in the
//      character model
// Set up page for users to look at their characters spell lists
// Write tests!!!!!