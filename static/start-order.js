// Start Order Page functionality
document.addEventListener("DOMContentLoaded", () => {
    // Display current user
    const username = sessionStorage.getItem("username");
    if (username) {
        document.getElementById("username").textContent = username;
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

    if (btnCreateOrder) {
        btnCreateOrder.addEventListener("click", async () => {
            const finishedgoodid = document.getElementById("finishedgoodid").value.trim();
            const targetQuantity = document.getElementById("target-quantity").value;

            // Clear previous messages
            messageBox.style.display = "none";
            messageBox.textContent = "";
            messageBox.className = "message-box";

            // Validate inputs
            if (!finishedgoodid) {
                messageBox.textContent = "Please enter a Finished Good ID";
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

            // Validate UUID format (basic check)
            const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
            if (!uuidRegex.test(finishedgoodid)) {
                messageBox.textContent = "Invalid UUID format";
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
                        target_quantity: parseInt(targetQuantity)
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    messageBox.textContent = `✓ Production Order Created! Order ID: ${data.orderid} | Target: ${data.target_quantity} parts`;
                    messageBox.className = "message-box success";
                    messageBox.style.display = "block";

                    // Clear form
                    document.getElementById("finishedgoodid").value = "";
                    document.getElementById("target-quantity").value = "";

                    // Re-enable button after 3 seconds
                    setTimeout(() => {
                        btnCreateOrder.disabled = false;
                    }, 3000);
                } else {
                    messageBox.textContent = `✗ Error: ${data.detail || "Failed to create production order"}`;
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
