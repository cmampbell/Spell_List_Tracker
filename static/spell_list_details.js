const spellContainer = document.getElementById("spell-cards")
const base_url = 'https://www.dnd5eapi.co'

let origHTML = {};
async function handleCardClick(evt) {
    // get spell card
    spellCard = evt.target.closest('.spell-card')
    spellIndex = spellCard.dataset.spellIndex

    if (spellCard.classList.contains('small')) {
        // keep initial html for spell card in variable
        origHTML[spellIndex] = spellCard.innerHTML

        //make request to api for spell info
        json = await axios.get(`${base_url}/api/spells/${spellIndex}`)

        //update spellCard with new data
        updateSpellCard(spellCard, json.data)

    }
    else if (spellCard.classList.contains('large')) {
        spellCard.innerHTML = origHTML[spellIndex]
        delete origHTML[spellIndex]
    }

    //toggle spell card class for css styling
    spellCard.classList.toggle('small')
    spellCard.classList.toggle('large')
}

function updateSpellCard(spell, data) {
    //card is html, spell is json data

    let { components, desc, higher_level, material, ritual, area_of_effect, attack_type, damage} = data

    let cardBody = spell.querySelector('.card-body');

    cardBody.innerHTML += (`<p>Components: ${components.join(', ')}</p> <p>Description: ${desc.join(" <br> ")}</p>`)

    if(damage){
        if('damage_type' in damage){
            cardBody.innerHTML += (`<p>Damage Type: ${damage.damage_type.name}`)
        }
    }

    if(attack_type){
        cardBody.innerHTML += `<p>Attack Type: ${attack_type.charAt(0).toUpperCase() + attack_type.slice(1)}</p>`
    }

    if(area_of_effect){
        cardBody.innerHTML +=`<p>Area of Effect: ${area_of_effect.size} ft. ${area_of_effect.type}</p>`
    }

    if(material){
        cardBody.innerHTML += `<p>Material: ${material}</p>`
    }

    if(higher_level.length > 0){
        cardBody.innerHTML += `<p>Higher Level: ${higher_level}</p>`
    }

    if(ritual){
        cardBody.innerHTML += `<p>This spell is a ritual</p>`
    }
}

function start() {

    // get all spell cards
    const spellCards = spellContainer.children

    for (card of spellCards) {
        card.addEventListener("click", handleCardClick)
    }
}

window.addEventListener("DOMContentLoaded", start)