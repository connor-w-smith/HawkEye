const table = document.getElementById("data-table");
const searchInput = document.getElementById("searchInput");

let debounceTimer;

//render results
function renderResults(data) {
    table.innerHTML = "";

    if (!data || data.length === 0) {
        const row = document.createElement("tr");
        row.innerHTML = `<td colspan="2" style="text-align:center">No results found</td>`;
        table.appendChild(row);
        return;
    }

    data.forEach(item => {
        const row = document.createElement("tr");
        row.style.cursor = "pointer";
        row.addEventListener("click", () => {
            window.location.href = `/product/${item.FinishedGoodID}`;
        });
        row.innerHTML = `
            <td>${item.FinishedGoodID}</td>
            <td>${item.FinishedGoodName}</td>
        `;
        table.appendChild(row);
    });
}

//fetch results
async function fetchResults(query = "") {
    try {
        const response = await fetch(
            `/search/finished-goods?search=${encodeURIComponent(query)}`
        );
        const data = await response.json();
        renderResults(data.results);
    } catch (err) {
        console.error("Search error:", err);
    }
}

//live typing
searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        fetchResults(searchInput.value.trim());
    }, 250);
});

//load all results on page load
document.addEventListener("DOMContentLoaded", () => {
    fetchResults();
});
