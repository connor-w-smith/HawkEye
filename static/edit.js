// Edit Page JavaScript - Refactored for separate edit pages

// ================================
// GLOBAL FUNCTION DEFINITIONS
// ================================

// Load raw materials with edit and delete buttons
function loadRawMaterialsForEdit() {
    const table = document.getElementById("sensor-data-table");
    if (!table) return; // Exit if table not on this page
    
    fetch("/materials/raw-materials")
    .then(response => response.json())
    .then(data => {
        const materials = data.raw_materials || [];
        table.innerHTML = '';

        if (materials.length === 0) {
            const row = document.createElement("tr");
            row.innerHTML = `<td colspan="5" style="text-align: center;">No raw materials available</td>`;
            table.appendChild(row);
            return;
        }

        materials.forEach(material => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${material.material_id}</td>
                <td>${material.material_name}</td>
                <td>${material.quantity_in_stock}</td>
                <td>${material.unit_of_measure}</td>
                <td>
                    <div class="actions-container">
                        <button class="btn-edit" onclick="openEditRawMaterialModal('${material.material_name}', ${material.quantity_in_stock}, '${material.unit_of_measure}')">
                            <i class="fa fa-edit"></i> Edit
                        </button>
                        <button class="btn-delete" onclick="deleteRawMaterial('${material.material_name}')">
                            <i class="fa fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
            table.appendChild(row);
        });
    })
    .catch(err => {
        console.error("Error loading raw materials: ", err);
        table.innerHTML = '<tr><td colspan="5" style="text-align: center;">Error loading raw materials</td></tr>';
    });
}

// Load finished goods with edit and delete buttons
function loadFinishedGoodsForEdit() {
    const table = document.getElementById("data-table");
    if (!table) return; // Exit if table not on this page
    
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
                <div class="actions-container">
                    <button class="btn-edit" onclick="openEditModal('${item.FinishedGoodName}')">
                        <i class="fa fa-edit"></i> Edit
                    </button>
                    <button class="btn-delete" onclick="deleteFinishedGood('${item.FinishedGoodName}')">
                        <i class="fa fa-trash"></i> Delete
                    </button>
                </div>
            </td>
            `;

            table.appendChild(row);
        });
    })
    .catch(err => console.error("Error loading goods: ", err));
}

// Load recipes with edit and delete buttons
function loadRecipesForEdit() {
    const table = document.getElementById("packaging-data-table");
    if (!table) return; // Exit if table not on this page
    
    fetch("/materials/recipes")
    .then(response => response.json())
    .then(data => {
        const recipes = data.recipes || [];
        table.innerHTML = '';

        if (recipes.length === 0) {
            const row = document.createElement("tr");
            row.innerHTML = `<td colspan="4" style="text-align: center;">No recipes available</td>`;
            table.appendChild(row);
            return;
        }

        recipes.forEach(recipe => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${recipe.finished_good || 'N/A'}</td>
                <td>${recipe.raw_material || 'N/A'}</td>
                <td>${recipe.quantity_required || 0}</td>
                <td>
                    <div class="actions-container">
                        <button class="btn-edit" onclick="openEditRecipeModal('${recipe.finished_good}', '${recipe.raw_material}', ${recipe.quantity_required})">
                            <i class="fa fa-edit"></i> Edit
                        </button>
                        <button class="btn-delete" onclick="deleteRecipe('${recipe.finished_good}', '${recipe.raw_material}')">
                            <i class="fa fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
            table.appendChild(row);
        });
    })
    .catch(err => {
        console.error("Error loading recipes: ", err);
        table.innerHTML = '<tr><td colspan="4" style="text-align: center;">Error loading recipes</td></tr>';
    });
}

// Make these globally accessible for app.js and other files
window.loadRawMaterialsForEdit = loadRawMaterialsForEdit;
window.loadFinishedGoodsForEdit = loadFinishedGoodsForEdit;
window.loadRecipesForEdit = loadRecipesForEdit;

function ensureDeleteActionModal() {
    let modal = document.getElementById("delete-action-modal");

    if (!modal) {
        modal = document.createElement("div");
        modal.id = "delete-action-modal";
        modal.className = "modal";
        modal.style.display = "none";
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close" id="delete-action-close">&times;</span>
                <h2 id="delete-action-title"></h2>
                <p id="delete-action-text" style="margin-bottom: 20px;"></p>
                <div style="display: flex; gap: 10px; justify-content: flex-end;">
                    <button type="button" id="delete-action-cancel" class="btn-edit" style="margin-right: 0;">Cancel</button>
                    <button type="button" id="delete-action-confirm" class="btn-delete">Delete</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    return {
        modal,
        closeButton: document.getElementById("delete-action-close"),
        title: document.getElementById("delete-action-title"),
        text: document.getElementById("delete-action-text"),
        cancelButton: document.getElementById("delete-action-cancel"),
        confirmButton: document.getElementById("delete-action-confirm")
    };
}

function showCustomDeleteConfirm(itemName) {
    const refs = ensureDeleteActionModal();
    refs.title.textContent = "Confirm Delete";
    refs.text.textContent = `Are you sure you want to delete "${itemName}"?`;
    refs.cancelButton.style.display = "inline-block";
    refs.confirmButton.textContent = "Delete";
    refs.confirmButton.classList.add("btn-delete");
    refs.confirmButton.classList.remove("btn-submit");
    refs.modal.style.display = "block";

    return new Promise((resolve) => {
        const closeModal = (result) => {
            refs.modal.style.display = "none";
            window.removeEventListener("click", handleOutsideClick);
            document.removeEventListener("keydown", handleKeyDown);
            resolve(result);
        };

        const handleOutsideClick = (event) => {
            if (event.target === refs.modal) {
                closeModal(false);
            }
        };

        const handleKeyDown = (event) => {
            if (event.key === "Escape") {
                closeModal(false);
            }
        };

        refs.closeButton.onclick = () => closeModal(false);
        refs.cancelButton.onclick = () => closeModal(false);
        refs.confirmButton.onclick = () => closeModal(true);
        window.addEventListener("click", handleOutsideClick);
        document.addEventListener("keydown", handleKeyDown);
    });
}

function showCustomDeleteMessage(title, message, isError = false) {
    const refs = ensureDeleteActionModal();
    refs.title.textContent = title;
    refs.text.textContent = message;
    refs.cancelButton.style.display = "none";
    refs.confirmButton.textContent = "OK";
    refs.confirmButton.classList.add("btn-submit");
    refs.confirmButton.classList.remove("btn-delete");
    refs.text.style.color = isError ? "red" : "";
    refs.modal.style.display = "block";

    return new Promise((resolve) => {
        const closeModal = () => {
            refs.modal.style.display = "none";
            window.removeEventListener("click", handleOutsideClick);
            document.removeEventListener("keydown", handleKeyDown);
            resolve();
        };

        const handleOutsideClick = (event) => {
            if (event.target === refs.modal) {
                closeModal();
            }
        };

        const handleKeyDown = (event) => {
            if (event.key === "Escape" || event.key === "Enter") {
                closeModal();
            }
        };

        refs.closeButton.onclick = closeModal;
        refs.confirmButton.onclick = closeModal;
        window.addEventListener("click", handleOutsideClick);
        document.addEventListener("keydown", handleKeyDown);
    });
}

window.showCustomDeleteConfirm = showCustomDeleteConfirm;
window.showCustomDeleteMessage = showCustomDeleteMessage;

// ================================
// INITIALIZATION
// ================================

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

    // Conditionally load tables only if they exist on this page
    if (document.getElementById("sensor-data-table")) {
        loadRawMaterialsForEdit();
    }
    
    if (document.getElementById("data-table")) {
        loadFinishedGoodsForEdit();
    }
    
    if (document.getElementById("packaging-data-table")) {
        loadRecipesForEdit();
    }

    // Handle Add Raw Material modal
    const addRawModal = document.getElementById("add-raw-material-modal");
    const addRawCloseBtn = addRawModal ? addRawModal.querySelector(".close") : null;
    const addRawForm = document.getElementById("add-raw-material-form");
    const addRawModalMessage = document.getElementById("raw-material-modal-message");
    
    if (addRawCloseBtn) {
        addRawCloseBtn.addEventListener("click", () => {
            addRawModal.style.display = "none";
        });
    }
    
    window.addEventListener("click", (event) => {
        if (event.target === addRawModal) {
            addRawModal.style.display = "none";
        }
    });
    
    if (addRawForm) {
        addRawForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const materialName = document.getElementById("raw-material-name").value;
            const quantity = document.getElementById("raw-material-quantity").value;
            const unit = document.getElementById("raw-material-unit").value;
            
            if (!materialName.trim() || !quantity || !unit.trim()) {
                if (addRawModalMessage) {
                    addRawModalMessage.style.color = "red";
                    addRawModalMessage.textContent = "Please fill in all fields";
                }
                return;
            }
            
            try {
                const response = await fetch("/materials/add", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
                    },
                    body: JSON.stringify({
                        material_name: materialName,
                        quantity_in_stock: parseFloat(quantity),
                        unit_of_measure: unit
                    })
                });
                
                if (response.ok) {
                    if (addRawModalMessage) {
                        addRawModalMessage.style.color = "green";
                        addRawModalMessage.textContent = "Raw material added successfully!";
                    }
                    setTimeout(() => {
                        addRawModal.style.display = "none";
                        addRawForm.reset();
                        if (addRawModalMessage) {
                            addRawModalMessage.textContent = "";
                            addRawModalMessage.style.color = "";
                        }
                        loadRawMaterialsForEdit();
                    }, 1500);
                } else {
                    const error = await response.json();
                    if (addRawModalMessage) {
                        addRawModalMessage.style.color = "red";
                        addRawModalMessage.textContent = `Error: ${error.detail || "Unknown error"}`;
                    }
                }
            } catch (err) {
                console.error("Error adding raw material: ", err);
                if (addRawModalMessage) {
                    addRawModalMessage.style.color = "red";
                    addRawModalMessage.textContent = "Error adding raw material: " + err.message;
                }
            }
        });
    }

    // Handle Edit Raw Material modal
    const editRawModal = document.getElementById("edit-raw-material-modal");
    const editRawCloseBtn = editRawModal ? editRawModal.querySelector(".close") : null;
    const editRawForm = document.getElementById("edit-raw-material-form");
    const editRawModalMessage = document.getElementById("edit-raw-material-modal-message");
    let currentEditingRawMaterial = null;
    
    if (editRawCloseBtn) {
        editRawCloseBtn.addEventListener("click", () => {
            editRawModal.style.display = "none";
        });
    }
    
    window.addEventListener("click", (event) => {
        if (event.target === editRawModal) {
            editRawModal.style.display = "none";
        }
    });
    
    if (editRawForm) {
        editRawForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const newName = document.getElementById("edit-raw-material-name").value;
            const quantity = document.getElementById("edit-raw-material-quantity").value;
            const unit = document.getElementById("edit-raw-material-unit").value;
            
            if (!newName.trim() || !quantity || !unit.trim()) {
                if (editRawModalMessage) {
                    editRawModalMessage.style.color = "red";
                    editRawModalMessage.textContent = "Please fill in all fields";
                }
                return;
            }
            
            try {
                const response = await fetch("/materials/update", {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
                    },
                    body: JSON.stringify({
                        material_name: currentEditingRawMaterial,
                        quantity_in_stock: parseFloat(quantity),
                        unit_of_measure: unit
                    })
                });
                
                if (response.ok) {
                    if (editRawModalMessage) {
                        editRawModalMessage.style.color = "green";
                        editRawModalMessage.textContent = "Raw material updated successfully!";
                    }
                    setTimeout(() => {
                        editRawModal.style.display = "none";
                        editRawForm.reset();
                        if (editRawModalMessage) {
                            editRawModalMessage.textContent = "";
                            editRawModalMessage.style.color = "";
                        }
                        loadRawMaterialsForEdit();
                    }, 1500);
                } else {
                    const error = await response.json();
                    if (editRawModalMessage) {
                        editRawModalMessage.style.color = "red";
                        editRawModalMessage.textContent = `Error: ${error.detail || "Unknown error"}`;
                    }
                }
            } catch (err) {
                console.error("Error updating raw material: ", err);
                if (editRawModalMessage) {
                    editRawModalMessage.style.color = "red";
                    editRawModalMessage.textContent = "Error updating raw material: " + err.message;
                }
            }
        });
    }

    // Function to open edit raw material modal
    window.openEditRawMaterialModal = function(materialName, quantity, unit) {
        currentEditingRawMaterial = materialName;
        document.getElementById("edit-raw-material-name").value = materialName;
        document.getElementById("edit-raw-material-quantity").value = quantity;
        document.getElementById("edit-raw-material-unit").value = unit;
        if (editRawModalMessage) {
            editRawModalMessage.textContent = "";
            editRawModalMessage.style.color = "";
        }
        editRawModal.style.display = "block";
    };

    // Function to delete raw material
    window.deleteRawMaterial = async function(materialName) {
        const shouldDelete = await showCustomDeleteConfirm(materialName);
        if (!shouldDelete) {
            return;
        }

        try {
            const response = await fetch("/materials/delete", {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
                },
                body: JSON.stringify({
                    material_name: materialName
                })
            });

            if (response.ok) {
                loadRawMaterialsForEdit();
                await showCustomDeleteMessage("Delete Successful", `"${materialName}" was deleted.`);
            } else {
                const error = await response.json();
                await showCustomDeleteMessage("Delete Failed", `Error deleting raw material: ${error.detail || "Unknown error"}`, true);
            }
        } catch (err) {
            console.error("Error deleting raw material: ", err);
            await showCustomDeleteMessage("Delete Failed", "Error deleting raw material: " + err.message, true);
        }
    };

    // Handle Add Finished Good modal
    const addModal = document.getElementById("add-finished-good-modal");
    const addCloseBtn = addModal ? addModal.querySelector(".close") : null;
    const addForm = document.getElementById("add-finished-good-form");
    const addModalMessage = document.getElementById("modal-message");
    
    if (addCloseBtn) {
        addCloseBtn.addEventListener("click", () => {
            addModal.style.display = "none";
        });
        
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

    // Handle Add Recipe modal
    const addRecipeModal = document.getElementById("add-recipe-modal");
    const addRecipeCloseBtn = addRecipeModal ? addRecipeModal.querySelector(".close") : null;
    const addRecipeForm = document.getElementById("add-recipe-form");
    const addRecipeModalMessage = document.getElementById("recipe-modal-message");
    
    // Populate recipe dropdowns
    async function populateRecipeDropdowns() {
        try {
            // Fetch finished goods
            const finishedGoodsResponse = await fetch("/search/finished-goods");
            const finishedGoodsData = await finishedGoodsResponse.json();
            const finishedGoods = finishedGoodsData.results || [];
            
            // Fetch raw materials
            const rawMaterialsResponse = await fetch("/materials/raw-materials");
            const rawMaterialsData = await rawMaterialsResponse.json();
            const rawMaterials = rawMaterialsData.raw_materials || [];
            
            // Populate Add Recipe modal dropdowns
            const addFGSelect = document.getElementById("recipe-finished-good-id");
            const addRMSelect = document.getElementById("recipe-material-name");
            
            if (addFGSelect) {
                addFGSelect.innerHTML = '<option value="">Select a finished good</option>';
                finishedGoods.forEach(fg => {
                    const option = document.createElement("option");
                    option.value = fg.FinishedGoodName || '';
                    option.textContent = fg.FinishedGoodName || '';
                    addFGSelect.appendChild(option);
                });
            }
            
            if (addRMSelect) {
                addRMSelect.innerHTML = '<option value="">Select a raw material</option>';
                rawMaterials.forEach(rm => {
                    const option = document.createElement("option");
                    option.value = rm.material_name || '';
                    option.textContent = rm.material_name || '';
                    addRMSelect.appendChild(option);
                });
            }
            
            // Populate Edit Recipe modal dropdowns
            const editFGSelect = document.getElementById("edit-recipe-finished-good-id");
            const editRMSelect = document.getElementById("edit-recipe-material-name");
            
            if (editFGSelect) {
                editFGSelect.innerHTML = '<option value="">Select a finished good</option>';
                finishedGoods.forEach(fg => {
                    const option = document.createElement("option");
                    option.value = fg.FinishedGoodName || '';
                    option.textContent = fg.FinishedGoodName || '';
                    editFGSelect.appendChild(option);
                });
            }
            
            if (editRMSelect) {
                editRMSelect.innerHTML = '<option value="">Select a raw material</option>';
                rawMaterials.forEach(rm => {
                    const option = document.createElement("option");
                    option.value = rm.material_name || '';
                    option.textContent = rm.material_name || '';
                    editRMSelect.appendChild(option);
                });
            }
        } catch (err) {
            console.error("Error populating recipe dropdowns: ", err);
        }
    }
    
    // Populate dropdowns when page loads
    populateRecipeDropdowns();
    
    if (addRecipeCloseBtn) {
        addRecipeCloseBtn.addEventListener("click", () => {
            addRecipeModal.style.display = "none";
        });
    }
    
    window.addEventListener("click", (event) => {
        if (event.target === addRecipeModal) {
            addRecipeModal.style.display = "none";
        }
    });
    
    if (addRecipeForm) {
        addRecipeForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const finishedGoodId = document.getElementById("recipe-finished-good-id").value;
            const materialName = document.getElementById("recipe-material-name").value;
            const quantityRequired = document.getElementById("recipe-quantity-required").value;
            
            if (!finishedGoodId.trim() || !materialName.trim() || !quantityRequired) {
                if (addRecipeModalMessage) {
                    addRecipeModalMessage.style.color = "red";
                    addRecipeModalMessage.textContent = "Please fill in all fields";
                }
                return;
            }
            
            try {
                const response = await fetch("/materials/recipe/add", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
                    },
                    body: JSON.stringify({
                        finished_good_id: finishedGoodId,
                        material_name: materialName,
                        quantity_required: parseFloat(quantityRequired)
                    })
                });
                
                if (response.ok) {
                    if (addRecipeModalMessage) {
                        addRecipeModalMessage.style.color = "green";
                        addRecipeModalMessage.textContent = "Recipe added successfully!";
                    }
                    setTimeout(() => {
                        addRecipeModal.style.display = "none";
                        addRecipeForm.reset();
                        if (addRecipeModalMessage) {
                            addRecipeModalMessage.textContent = "";
                            addRecipeModalMessage.style.color = "";
                        }
                        loadRecipesForEdit();
                    }, 1500);
                } else {
                    const error = await response.json();
                    if (addRecipeModalMessage) {
                        addRecipeModalMessage.style.color = "red";
                        addRecipeModalMessage.textContent = `Error: ${error.detail || "Unknown error"}`;
                    }
                }
            } catch (err) {
                console.error("Error adding recipe: ", err);
                if (addRecipeModalMessage) {
                    addRecipeModalMessage.style.color = "red";
                    addRecipeModalMessage.textContent = "Error adding recipe: " + err.message;
                }
            }
        });
    }

    // Handle Edit Recipe modal
    const editRecipeModal = document.getElementById("edit-recipe-modal");
    const editRecipeCloseBtn = editRecipeModal ? editRecipeModal.querySelector(".close") : null;
    const editRecipeForm = document.getElementById("edit-recipe-form");
    const editRecipeModalMessage = document.getElementById("edit-recipe-modal-message");
    let currentEditingRecipe = null;
    
    if (editRecipeCloseBtn) {
        editRecipeCloseBtn.addEventListener("click", () => {
            editRecipeModal.style.display = "none";
        });
    }
    
    window.addEventListener("click", (event) => {
        if (event.target === editRecipeModal) {
            editRecipeModal.style.display = "none";
        }
    });
    
    if (editRecipeForm) {
        editRecipeForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const newFinishedGoodId = document.getElementById("edit-recipe-finished-good-id").value;
            const newMaterialName = document.getElementById("edit-recipe-material-name").value;
            const newQuantityRequired = document.getElementById("edit-recipe-quantity-required").value;
            
            if (!newFinishedGoodId.trim() || !newMaterialName.trim() || !newQuantityRequired) {
                if (editRecipeModalMessage) {
                    editRecipeModalMessage.style.color = "red";
                    editRecipeModalMessage.textContent = "Please fill in all fields";
                }
                return;
            }
            
            try {
                // Delete the old recipe
                const deleteResponse = await fetch("/materials/recipe/delete", {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
                    },
                    body: JSON.stringify({
                        finished_good_id: currentEditingRecipe.finished_good_id,
                        material_name: currentEditingRecipe.material_name
                    })
                });
                
                if (!deleteResponse.ok) {
                    const deleteError = await deleteResponse.json();
                    console.error("Delete recipe error:", deleteError);
                    throw new Error(`Failed to delete old recipe: ${deleteError.detail || "Unknown error"}`);
                }
                
                // Add the new recipe
                const addResponse = await fetch("/materials/recipe/add", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
                    },
                    body: JSON.stringify({
                        finished_good_id: newFinishedGoodId,
                        material_name: newMaterialName,
                        quantity_required: parseFloat(newQuantityRequired)
                    })
                });
                
                if (addResponse.ok) {
                    if (editRecipeModalMessage) {
                        editRecipeModalMessage.style.color = "green";
                        editRecipeModalMessage.textContent = "Recipe updated successfully!";
                    }
                    setTimeout(() => {
                        editRecipeModal.style.display = "none";
                        editRecipeForm.reset();
                        if (editRecipeModalMessage) {
                            editRecipeModalMessage.textContent = "";
                            editRecipeModalMessage.style.color = "";
                        }
                        loadRecipesForEdit();
                    }, 1500);
                } else {
                    const error = await addResponse.json();
                    if (editRecipeModalMessage) {
                        editRecipeModalMessage.style.color = "red";
                        editRecipeModalMessage.textContent = `Error: ${error.detail || "Unknown error"}`;
                    }
                }
            } catch (err) {
                console.error("Error updating recipe: ", err);
                if (editRecipeModalMessage) {
                    editRecipeModalMessage.style.color = "red";
                    editRecipeModalMessage.textContent = "Error updating recipe: " + err.message;
                }
            }
        });
    }

    // Function to open edit recipe modal
    window.openEditRecipeModal = function(finishedGoodId, materialName, quantityRequired) {
        // Populate the edit dropdowns with fresh data before setting values
        populateRecipeDropdowns().then(() => {
            currentEditingRecipe = { finished_good_id: finishedGoodId, material_name: materialName };
            document.getElementById("edit-recipe-finished-good-id").value = finishedGoodId;
            document.getElementById("edit-recipe-material-name").value = materialName;
            document.getElementById("edit-recipe-quantity-required").value = quantityRequired;
            if (editRecipeModalMessage) {
                editRecipeModalMessage.textContent = "";
                editRecipeModalMessage.style.color = "";
            }
            editRecipeModal.style.display = "block";
        });
    };

    // Function to delete recipe
    window.deleteRecipe = async function(finishedGoodId, materialName) {
        const shouldDelete = await showCustomDeleteConfirm(`${finishedGoodId} recipe with ${materialName}`);
        if (!shouldDelete) {
            return;
        }

        try {
            const response = await fetch("/materials/recipe/delete", {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
                },
                body: JSON.stringify({
                    finished_good_id: finishedGoodId,
                    material_name: materialName
                })
            });

            if (response.ok) {
                loadRecipesForEdit();
                await showCustomDeleteMessage("Delete Successful", "Recipe was deleted.");
            } else {
                const error = await response.json();
                await showCustomDeleteMessage("Delete Failed", `Error deleting recipe: ${error.detail || "Unknown error"}`, true);
            }
        } catch (err) {
            console.error("Error deleting recipe: ", err);
            await showCustomDeleteMessage("Delete Failed", "Error deleting recipe: " + err.message, true);
        }
    };

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
