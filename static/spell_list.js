//areas to drag and drop spells
const dropZone = document.getElementById("target")
const spellContainer = document.getElementById("spell-cards-div")

// spell options in the hidden multiple select field
const spellOptions = document.querySelectorAll("option")
// select field for form
const formSelectField = document.getElementById("spells");

function allowDrop(evt) {
    evt.preventDefault();
}

function drag(evt) {
    evt.dataTransfer.setData("text", evt.target.id);
}

function addToListOnDrop(evt) {
    evt.preventDefault();
    let data = evt.dataTransfer.getData("text");

    // find the spell that was added to the list
    let addedSpell = Array.from(spellOptions).find(spell => spell.value == data)
    // set the spell in the hidden select field to true
    addedSpell.selected = true;

    dropZone.appendChild(document.getElementById(data));

    toggleDropZone()
}

function returnToSpellsOnDrop(evt) {
    evt.preventDefault();
    let data = evt.dataTransfer.getData("text");

    // find the spell that was added to the list
    let addedSpell = Array.from(spellOptions).find(spell => spell.value == data)
    // set the spell in the hidden select field to true
    addedSpell.selected = false;

    spellContainer.appendChild(document.getElementById(data));

    //make an array of all spells
    let spellArray = Array.from(spellContainer.children).sort(compare);

    //append sorted list back to DOM
    spellArray.forEach(elem => spellContainer.appendChild(elem));

    toggleDropZone()
}

function compare(a, b) {
    if (parseInt(a.dataset.listPosition) < parseInt(b.dataset.listPosition))
        return -1;
    if (parseInt(a.dataset.listPosition) > parseInt(b.dataset.listPosition))
        return 1;
    return 0;
}
  
// Function to sort spells
function clearSpellList() {

    // get all spells
    const allSpellCards = document.querySelectorAll("[data-list-position]");

    //make an array of all spells
    let spellArray = Array.from(allSpellCards).sort(compare);

    //append sorted list back to DOM
    spellArray.forEach(elem => document.querySelector("#avail-spells").appendChild(elem));

    //clear options
    Array.from(spellOptions).forEach(elem => elem.selected = false)

    //reset drop-zone class
    toggleDropZone()
}

function toggleDropZone() {
    if (dropZone.childElementCount === 0){
        dropZone.classList.remove('has-items');
        dropZone.classList.add('empty-list');
    }
    else if (dropZone.childElementCount > 0){
        dropZone.classList.remove('empty-list');
        dropZone.classList.add('has-items');
    }
}

function start() {

    // hide the select field with all spell options
    formSelectField.hidden = true;

    // get all spell cards

    const spellCards = spellContainer.children

    for (card of spellCards){
        card.addEventListener("dragstart", drag);
    }

    dropZone.addEventListener("dragover", allowDrop)
    dropZone.addEventListener("drop", addToListOnDrop)

    spellContainer.addEventListener("dragover", allowDrop)
    spellContainer.addEventListener("drop", returnToSpellsOnDrop)

    const clearButton = document.getElementById('clear-button')
    clearButton.addEventListener("click", clearSpellList)
}

window.addEventListener("DOMContentLoaded", start)



// TODO:

// Should refactor these functions into OOP
// Should refactor server-side spell list functions into OOP, put them as methods in the
//      character model
// Write tests!!!!!