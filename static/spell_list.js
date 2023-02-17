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
    dropZone.appendChild(document.getElementById(data));
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
}

window.addEventListener("DOMContentLoaded", start)