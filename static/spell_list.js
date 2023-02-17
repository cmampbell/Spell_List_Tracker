const dropZone = document.getElementById("target")
const spellOptions = document.querySelectorAll("option")

function allowDrop(evt) {
    evt.preventDefault();
}

function drag(evt) {
    evt.dataTransfer.setData("text", evt.target.id);
}

function drop(evt) {
    evt.preventDefault();
    let data = evt.dataTransfer.getData("text");

    // find the spell that was added to the list
    let addedSpell = Array.from(spellOptions).find(spell => spell.value == data)
    // set the spell in the hidden select field to true
    addedSpell.selected = true;

    if(dropZone.classList.contains('empty-list')){
        dropZone.classList.toggle('empty-list');
        dropZone.classList.toggle('has-items');
    }

    dropZone.appendChild(document.getElementById(data));
}

function start() {
    // hide the select field with all spell options
    const formSelectField = document.getElementById("spells");
    formSelectField.hidden = true;

    // get all spell cards
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
    if (parseInt(a.dataset.listPosition) < parseInt(b.dataset.listPosition))
        return -1;
    if (parseInt(a.dataset.listPosition) > parseInt(b.dataset.listPosition))
        return 1;
    return 0;
}
  
// Function to sort spells
function clearSpellList() {
    //reset drop-zone class
    if(dropZone.classList.contains('has-items')){
        dropZone.classList.toggle('empty-list')
        dropZone.classList.toggle('has-items')
    }
    // get all spells
    const allSpellCards = document.querySelectorAll("[data-list-position]");

    //make an array of all spells
    let spellArray = Array.from(allSpellCards).sort(compare);

    //append sorted list back to DOM
    spellArray.forEach(elem => document.querySelector("#avail-spells").appendChild(elem));

    //clear options
    Array.from(spellOptions).forEach(elem => elem.selected = false)
}

// TODO:
// Figure out how to save spells into a spell list on the server

//      I think we hide a select field, and when a user drops a spell into the dropZone
//         we add that selection into the hidden select field by spell id
//         if a user clears the list, we clear the selections
//          when a user hits save spell-list, we grab the selects from the hidden field and make the post request

// Need to make spell selection hidden
// When a spell is dropped in dropzone -> find spell id in select field, and make selected = True


// Should refactor these functions into OOP
// Should refactor server-side spell list functions into OOP, put them as methods in the
//      character model
// Set up page for users to look at their characters spell lists
// Write tests!!!!!