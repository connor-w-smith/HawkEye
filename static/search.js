// Function to render results in the table
function renderResults(data) {
    const table = document.getElementById("data-table");
    table.innerHTML = ""; // Clear previous results

    if (!data.length) {
        const row = document.createElement("tr");
        row.innerHTML = `<td colspan="2" style="text-align:center">No results found</td>`;
        table.appendChild(row);
        return;
    }

    data.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.finishedgoodid}</td>
            <td>${item.finishedgoodname}</td>
        `;
        table.appendChild(row);
    });
}

// Search by Name
document.getElementById("searchNameBtn").addEventListener("click", async () => {
    const query = document.getElementById("searchNameInput").value.trim();
    if (!query) return;

    try {
        const response = await fetch(`/search/name?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        renderResults(data);
    } catch (err) {
        console.error("Error searching by name:", err);
    }
});

// Search by ID
document.getElementById("searchIdBtn").addEventListener("click", async () => {
    const query = document.getElementById("searchIdInput").value.trim();
    if (!query) return;

    try {
        const response = await fetch(`/search/id?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        renderResults(data);
    } catch (err) {
        console.error("Error searching by ID:", err);
    }
});
