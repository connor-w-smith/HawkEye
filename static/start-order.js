// Start Order Page functionality
document.addEventListener("DOMContentLoaded", async () => {
    // Display current user
    const username = sessionStorage.getItem("username");
    if (username) {
        document.getElementById("username").textContent = username;
    }

    // Populate finished goods dropdown
    try {
        const response = await fetch("/products/finished-goods?search=");
        const data = await response.json();
        
        if (data.status === "success" && data.results) {
            const dropdown = document.getElementById("finishedgoodid");
            data.results.forEach(item => {
                const option = document.createElement("option");
                option.value = item.FinishedGoodID;
                option.textContent = item.FinishedGoodName;
                dropdown.appendChild(option);
            });
        }
    } catch (error) {
        console.error("Error loading finished goods:", error);
    }

    // Default sensor dropdown to whichever sensor is not currently assigned to an active order
    try {
        const sensorDropdown = document.getElementById("sensor-id");
        if (sensorDropdown) {
            const response = await fetch("/api/production/active-orders");
            const activeOrders = await response.json();

            const occupiedSensors = new Set(
                (Array.isArray(activeOrders) ? activeOrders : [])
                    .map(order => (order.sensor_id || "").trim())
                    .filter(Boolean)
            );

            if (!occupiedSensors.has("Sensor_A")) {
                sensorDropdown.value = "Sensor_A";
            } else if (!occupiedSensors.has("Sensor_B")) {
                sensorDropdown.value = "Sensor_B";
            } else {
                sensorDropdown.value = "Sensor_A";
            }
        }
    } catch (error) {
        console.error("Error determining default sensor:", error);
        const sensorDropdown = document.getElementById("sensor-id");
        if (sensorDropdown) {
            sensorDropdown.value = "Sensor_A";
        }
    }

    // Handle logout
    document.getElementById("logout-link").addEventListener("click", async (e) => {
        e.preventDefault();
        try {
            await fetch("/api/logout", {
                method: "POST"
            });
            sessionStorage.removeItem("username");
            window.location.href = "/";
        } catch (error) {
            console.error("Logout error:", error);
            sessionStorage.removeItem("username");
            window.location.href = "/";
        }
    });

    // Handle create production order
    const btnCreateOrder = document.getElementById("btnCreateOrder");
    const messageBox = document.getElementById("orderMessage");
    const shortageModal = document.getElementById("shortage-modal");
    const shortageModalClose = document.getElementById("shortage-modal-close");
    const shortageModalOk = document.getElementById("shortage-modal-ok");
    const shortageModalSummary = document.getElementById("shortage-modal-summary");
    const shortageMaterialList = document.getElementById("shortage-material-list");

    const closeShortageModal = () => {
        if (shortageModal) {
            shortageModal.style.display = "none";
        }
    };

    const showShortageModal = (shortages, finishedGoodName) => {
        if (!shortageModal || !shortageModalSummary || !shortageMaterialList) {
            return;
        }

        shortageModalSummary.textContent = `There is not enough inventory to create ${finishedGoodName}.`;
        shortageMaterialList.innerHTML = "";

        shortages.forEach(item => {
            const li = document.createElement("li");
            li.textContent = `${item.material_name}: only ${item.available} available`;
            shortageMaterialList.appendChild(li);
        });

        shortageModal.style.display = "block";
    };

    if (shortageModalClose) {
        shortageModalClose.addEventListener("click", closeShortageModal);
    }

    if (shortageModalOk) {
        shortageModalOk.addEventListener("click", closeShortageModal);
    }

    window.addEventListener("click", (event) => {
        if (event.target === shortageModal) {
            closeShortageModal();
        }
    });

    if (btnCreateOrder) {
        btnCreateOrder.addEventListener("click", async () => {
            const finishedGoodSelect = document.getElementById("finishedgoodid");
            const finishedgoodid = finishedGoodSelect.value.trim();
            const finishedGoodName = finishedGoodSelect.options[finishedGoodSelect.selectedIndex]?.text || "the selected finished good";
            const targetQuantity = document.getElementById("target-quantity").value;
            const sensorId = document.getElementById("sensor-id").value.trim() || null;

            // Clear previous messages
            messageBox.style.display = "none";
            messageBox.textContent = "";
            messageBox.className = "message-box";

            // Validate inputs
            if (!finishedgoodid) {
                messageBox.textContent = "Please select a Finished Good";
                messageBox.classList.add("error");
                messageBox.style.display = "block";
                return;
            }

            if (!targetQuantity || parseInt(targetQuantity) < 1) {
                messageBox.textContent = "Please enter a valid target quantity (must be at least 1)";
                messageBox.classList.add("error");
                messageBox.style.display = "block";
                return;
            }

            // Disable button to prevent double submission
            btnCreateOrder.disabled = true;
            messageBox.textContent = "Creating production order...";
            messageBox.classList.add("info");
            messageBox.style.display = "block";

            try {
                const response = await fetch("/orders/create-production-order", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        finishedgoodid: finishedgoodid,
                        target_quantity: parseInt(targetQuantity),
                        sensor_id: sensorId
                    })
                });

                const data = await response.json();

                const hasShortages = Array.isArray(data.shortages) && data.shortages.length > 0;
                const requestSucceeded = response.ok && data.status !== "error";

                if (requestSucceeded) {
                    const sensorText = data.sensor_id ? ` | Sensor: ${data.sensor_id}` : "";
                    messageBox.textContent = `✓ Production Order Created! Order ID: ${data.orderid} | Target: ${data.target_quantity} parts${sensorText}`;
                    messageBox.className = "message-box success";
                    messageBox.style.display = "block";

                    // Clear form
                    document.getElementById("finishedgoodid").value = "";
                    document.getElementById("target-quantity").value = "";
                    document.getElementById("sensor-id").value = "";

                    // Re-enable button after 3 seconds
                    setTimeout(() => {
                        btnCreateOrder.disabled = false;
                    }, 3000);
                } else {
                    if (hasShortages) {
                        showShortageModal(data.shortages, finishedGoodName);
                    }

                    messageBox.textContent = `✗ Error: ${data.detail || data.message || "Failed to create production order"}`;
                    messageBox.classList.add("error");
                    messageBox.style.display = "block";
                    btnCreateOrder.disabled = false;
                }
            } catch (error) {
                console.error("Error creating production order:", error);
                messageBox.textContent = `✗ Error: ${error.message}`;
                messageBox.classList.add("error");
                messageBox.style.display = "block";
                btnCreateOrder.disabled = false;
            }
        });

        // Allow Enter key to submit
        document.getElementById("target-quantity").addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                btnCreateOrder.click();
            }
        });
    }
});
