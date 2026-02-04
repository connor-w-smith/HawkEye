//function to render results in the table
function renderResults(data) {
    const table = document.getElementById("data-table");
    //table.innerHTML = ""; //Clear previous results

    if (!data.length) {
        const row = document.createElement("tr");
        row.innerHTML = `<td colspan="2" style="text-align:center">No results found</td>`;
        table.appendChild(row);
        return;
    }

    data.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.FinishedGoodID}</td>
            <td>${item.FinishedGoodName}</td>
        `;
        table.appendChild(row);
    });
}

//search by Name
document.getElementById("searchNameBtn").addEventListener("click", async () => {
    const query = document.getElementById("searchNameInput").value.trim();
    if (!query) return;

    try {
        const response = await fetch(`/finished-good-name-search?finished_good_name=${encodeURIComponent(query)}`);
        const data = await response.json();
        renderResults(data.results);
    } catch (err) {
        console.error("Error searching by name:", err);
    }
});

//search by ID
document.getElementById("searchIdBtn").addEventListener("click", async () => {
    const query = document.getElementById("searchIdInput").value.trim();
    if (!query) return;

    try {
        const response = await fetch(`/finished-good-ID-search?finished_good_id=${encodeURIComponent(query)}`);
        const data = await response.json();
        renderResults(data.results);
    } catch (err) {
        console.error("Error searching by ID:", err);
    }
});
