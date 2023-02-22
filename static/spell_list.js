//areas to drag and drop spells
const dropZone = document.getElementById("target")
const spellContainer = document.getElementById("spell-cards-div")

// spell options in the hidden multiple select field
const spellOptions = document.querySelectorAll("option")
// select field for form
const formSelectField = document.getElementById("spells");

const base_url = 'https://www.dnd5eapi.co'

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
function clearSpellList(evt) {

    evt.preventDefault();

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

let origHTML;
async function handleCardClick(evt){
    // get spell card
    spellCard = evt.target.closest('.spell-card')
    spellIndex = spellCard.dataset.spellIndex

    if (spellCard.classList.contains('small')){
        // keep initial html for spell card in variable
        origHTML = spellCard.innerHTML

        //make request to api for spell info
        json = await axios.get(`${base_url}/api/spells/${spellIndex}`)

        //update spellCard with new data
        updateSpellCard(spellCard, json.data)
        
    }
    else if (spellCard.classList.contains('large')){
        spellCard.innerHTML = origHTML
    }
    
    //toggle spell card class for css styling
    spellCard.classList.toggle('small')
    spellCard.classList.toggle('large')

}

function updateSpellCard(spell, data){
    //card is html, spell is json data

    let { components, desc, higher_level, material, ritual} = data
    let cardBody;
    console.log(desc)
    cardBody = spell.querySelector('.card-body')

    //this is janky and I need to fix, will do when I get to styling
    cardBody.innerHTML += `<p>Components: ${components}</p> <p>Description: ${desc}</p> <p>Higher Level: ${higher_level}</p>
    <p>Material: ${material}</p> <p>Ritual: ${ritual}</p>`

}

function start() {

    // hide the select field with all spell options
    formSelectField.hidden = true;

    // get all spell cards

    const spellCards = spellContainer.children

    for (card of spellCards){
        card.addEventListener("dragstart", drag);
        card.addEventListener("click", handleCardClick)
    }

    dropZone.addEventListener("dragover", allowDrop)
    dropZone.addEventListener("drop", addToListOnDrop)

    spellContainer.addEventListener("dragover", allowDrop)
    spellContainer.addEventListener("drop", returnToSpellsOnDrop)

    const clearButton = document.getElementById('clear-button')
    clearButton.addEventListener("click", clearSpellList)

}

window.addEventListener("DOMContentLoaded", start)