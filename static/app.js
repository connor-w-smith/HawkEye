document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/finishedgoods")
    .then(response => response.json())
    .then(data => {
        const table = document.getElementById("data-table");

        data.forEach(item => {
            const row = document.createElement("tr");

            row.innerHTML = `
            <td>${item.finishedgoodid}</td>
            <td>${item.finishedgoodname}</td>
            `;

            table.appendChild(row);
        });
    })
    .catch(err => console.error("Error loading goods: ", err)); 
});