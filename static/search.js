document.getElementById("searchBtn").addEventListener("click", async () => {
    const query = document.getElementById("searchInput").value.trim();
    const table = document.getElementById("data-table");

    // Clear previous results
    table.innerHTML = "";

    if (!query) {
        return;
    }

    try {
        const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (!response.ok || data.length === 0) {
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

    } catch (err) {
        console.error("Search error:", err);
    }
});
