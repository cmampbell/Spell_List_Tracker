function allowDrop(evt) {
    evt.preventDefault();
    console.log(evt.dataTransfer.getData("text"))
}

function drag(evt) {
    evt.dataTransfer.setData("text", evt.target.id);
    console.log(evt.dataTransfer.getData("text"))
}

function drop(evt) {
    evt.preventDefault();
    let data = evt.dataTransfer.getData("text");

    let dropZone = document.getElementById("target")
    if (dropZone.classList.contains('empty-list')){
        dropZone.classList.toggle('empty-list')
        dropZone.classList.toggle('has-items')
    }
    dropZone.appendChild(document.getElementById(data));
}

function clickClearButton(evt){
    console.log('in click')
    evt.preventDefault()
    const dropZone = document.getElementById("target")
    const availSpells = document.getElementById('avail-spells')

    for(child in dropZone.children){
        console.log(child)
        availSpells.prepend(child)
    }
    dropZone.innerHTML = ''
    dropZone.classList.toggle('empty-list')
    dropZone.classList.toggle('has-items')
}

function start() {
    const allSpellCards = document.getElementById("avail-spells");

    const spellCards = allSpellCards.children

    for (card of spellCards){
        card.addEventListener("dragstart", drag);
    }

    const dropZone = document.getElementById("target")
    dropZone.addEventListener("dragover", allowDrop)
    dropZone.addEventListener("drop", drop)

    const clearButton = document.getElementById('clear-button')
    clearButton.addEventListener("click", clickClearButton)
}

window.addEventListener("DOMContentLoaded", start)

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