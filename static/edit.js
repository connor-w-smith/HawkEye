// Edit Page JavaScript

document.addEventListener("DOMContentLoaded", async () => {
    // Check if user is admin
    if (typeof syncCurrentUserPermissions === "function") {
        await syncCurrentUserPermissions();
    }

    const isAdmin = sessionStorage.getItem("is_admin") === "true";
    if (!isAdmin) {
        window.location.href = "/index";
        return;
    }

    // Load finished goods with edit and delete buttons
    loadFinishedGoodsForEdit();

    // Handle Add Finished Good modal
    const addBtn = document.getElementById("btn-add-finished-good");
    const addModal = document.getElementById("add-finished-good-modal");
    const addCloseBtn = addModal ? addModal.querySelector(".close") : null;
    const addForm = document.getElementById("add-finished-good-form");
    const addModalMessage = document.getElementById("modal-message");
    
    if (addBtn && addModal) {
        addBtn.addEventListener("click", () => {
            addModal.style.display = "block";
        });
        
        if (addCloseBtn) {
            addCloseBtn.addEventListener("click", () => {
                addModal.style.display = "none";
            });
        }
        
        window.addEventListener("click", (event) => {
            if (event.target === addModal) {
                addModal.style.display = "none";
            }
        });
    }
    
    if (addForm) {
        addForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const finishedGoodName = document.getElementById("finished-good-name").value;
            
            if (!finishedGoodName.trim()) {
                if (addModalMessage) {
                    addModalMessage.style.color = "red";
                    addModalMessage.textContent = "Please enter a finished good name";
                }
                return;
            }
            
            try {
                const response = await fetch("/products/add-finished-good", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
                    },
                    body: JSON.stringify({
                        finished_good_name: finishedGoodName
                    })
                });
                
                if (response.ok) {
                    if (addModalMessage) {
                        addModalMessage.style.color = "green";
                        addModalMessage.textContent = "Finished good added successfully!";
                    }
                    setTimeout(() => {
                        addModal.style.display = "none";
                        addForm.reset();
                        if (addModalMessage) {
                            addModalMessage.textContent = "";
                            addModalMessage.style.color = "";
                        }
                        loadFinishedGoodsForEdit();
                    }, 1500);
                } else {
                    const error = await response.json();
                    if (addModalMessage) {
                        addModalMessage.style.color = "red";
                        addModalMessage.textContent = `Error: ${error.detail || "Unknown error"}`;
                    }
                }
            } catch (err) {
                console.error("Error adding finished good: ", err);
                if (addModalMessage) {
                    addModalMessage.style.color = "red";
                    addModalMessage.textContent = "Error adding finished good: " + err.message;
                }
            }
        });
    }

    // Handle Edit Finished Good modal
    const editModal = document.getElementById("edit-finished-good-modal");
    const editCloseBtn = editModal ? editModal.querySelector(".close") : null;
    const editForm = document.getElementById("edit-finished-good-form");
    const editModalMessage = document.getElementById("edit-modal-message");
    let currentEditingFinishedGood = null;
    
    if (editCloseBtn) {
        editCloseBtn.addEventListener("click", () => {
            editModal.style.display = "none";
        });
    }
    
    window.addEventListener("click", (event) => {
        if (event.target === editModal) {
            editModal.style.display = "none";
        }
    });
    
    if (editForm) {
        editForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const newName = document.getElementById("edit-finished-good-name").value;
            
            if (!newName.trim()) {
                if (editModalMessage) {
                    editModalMessage.style.color = "red";
                    editModalMessage.textContent = "Please enter a finished good name";
                }
                return;
            }
            
            try {
                const response = await fetch("/products/update-finished-good", {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
                    },
                    body: JSON.stringify({
                        old_finished_good_name: currentEditingFinishedGood,
                        new_finished_good_name: newName
                    })
                });
                
                if (response.ok) {
                    if (editModalMessage) {
                        editModalMessage.style.color = "green";
                        editModalMessage.textContent = "Finished good updated successfully!";
                    }
                    setTimeout(() => {
                        editModal.style.display = "none";
                        editForm.reset();
                        if (editModalMessage) {
                            editModalMessage.textContent = "";
                            editModalMessage.style.color = "";
                        }
                        loadFinishedGoodsForEdit();
                    }, 1500);
                } else {
                    const error = await response.json();
                    if (editModalMessage) {
                        editModalMessage.style.color = "red";
                        editModalMessage.textContent = `Error: ${error.detail || "Unknown error"}`;
                    }
                }
            } catch (err) {
                console.error("Error updating finished good: ", err);
                if (editModalMessage) {
                    editModalMessage.style.color = "red";
                    editModalMessage.textContent = "Error updating finished good: " + err.message;
                }
            }
        });
    }

    // Function to open edit modal
    window.openEditModal = function(finishedGoodName) {
        currentEditingFinishedGood = finishedGoodName;
        document.getElementById("edit-finished-good-name").value = finishedGoodName;
        if (editModalMessage) {
            editModalMessage.textContent = "";
            editModalMessage.style.color = "";
        }
        editModal.style.display = "block";
    };

    // Load finished goods with edit and delete buttons
    function loadFinishedGoodsForEdit() {
        const table = document.getElementById("data-table");
        fetch("/search/finished-goods")
        .then(response => response.json())
        .then(data => {
            const results = data.results || [];
            table.innerHTML = '';
            results.forEach(item => {
                const row = document.createElement("tr");

                row.innerHTML = `
                <td>${item.FinishedGoodID}</td>
                <td>${item.FinishedGoodName}</td>
                <td>
                    <button class="btn-edit" onclick="openEditModal('${item.FinishedGoodName}')">
                        <i class="fa fa-edit"></i> Edit
                    </button>
                    <button class="btn-delete" onclick="deleteFinishedGood('${item.FinishedGoodName}')">
                        <i class="fa fa-trash"></i> Delete
                    </button>
                </td>
                `;

                table.appendChild(row);
            });
        })
        .catch(err => console.error("Error loading goods: ", err));
    }

    // Fetch sensor data
    const sensorTable = document.getElementById("sensor-data-table");
    if (sensorTable) {
        fetch("/search/sensor-production")
        .then(response => response.json())
        .then(data => {
            sensorTable.innerHTML = '';
            if (!data || data.length === 0) {
                const row = document.createElement("tr");
                row.innerHTML = `<td colspan="3" style="text-align: center;">No sensor data available</td>`;
                sensorTable.appendChild(row);
                return;
            }

            data.forEach(sensor => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${sensor.sensorid || 'N/A'}</td>
                    <td>${sensor.last_hour || 0}</td>
                    <td>${sensor.total_today || 0}</td>
                `;
                sensorTable.appendChild(row);
            });
        })
        .catch(err => {
            console.error("Error loading sensor data: ", err);
            sensorTable.innerHTML = '<tr><td colspan="3" style="text-align: center;">Error loading sensor data</td></tr>';
        });
    }

    // Fetch currently packaging orders
    const packagingTable = document.getElementById("packaging-data-table");
    if (packagingTable) {
        fetch("/search/active-orders")
        .then(response => response.json())
        .then(data => {
            packagingTable.innerHTML = '';
            
            if (!data || data.length === 0) {
                const row = document.createElement("tr");
                row.innerHTML = `<td colspan="4" style="text-align: center;">No active packaging orders</td>`;
                packagingTable.appendChild(row);
                return;
            }

            data.forEach(order => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${order.orderid || 'N/A'}</td>
                    <td>${order.finishedgoodname || 'N/A'}</td>
                    <td>${order.sensorid || 'N/A'}</td>
                    <td>${order.partsproduced || 0}</td>
                `;
                packagingTable.appendChild(row);
            });
        })
        .catch(err => {
            console.error("Error loading packaging data: ", err);
            packagingTable.innerHTML = '<tr><td colspan="4" style="text-align: center;">Error loading packaging data</td></tr>';
        });
    }

    // Handle logout
    const logoutLink = document.getElementById("logout-link");
    if (logoutLink) {
        logoutLink.addEventListener("click", async (e) => {
            e.preventDefault();
            try {
                await fetch("/auth/logout", {
                    method: "POST",
                    headers: {
                        ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
                    }
                });
            } catch (error) {
                console.error("Logout error:", error);
            } finally {
                sessionStorage.removeItem("username");
                sessionStorage.removeItem("session_token");
                sessionStorage.removeItem("is_admin");
                window.location.href = "/";
            }
        });
    }
});
