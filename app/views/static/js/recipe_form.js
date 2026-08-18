document.addEventListener("DOMContentLoaded", () => {
    const rowsContainer = document.getElementById("ingredient-rows");
    const template = document.getElementById("ingredient-row-template");
    const addButton = document.getElementById("add-ingredient");

    function bindRemove(row) {
        row.querySelector(".remove-row").addEventListener("click", () => row.remove());
    }

    rowsContainer.querySelectorAll(".ingredient-row").forEach(bindRemove);

    addButton.addEventListener("click", () => {
        const row = template.content.firstElementChild.cloneNode(true);
        bindRemove(row);
        rowsContainer.appendChild(row);
    });

    if (rowsContainer.children.length === 0) {
        addButton.click();
    }
});
