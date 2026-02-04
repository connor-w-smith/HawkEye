document.addEventListener("DOMContentLoaded", () => {
    // Display current user
    const username = sessionStorage.getItem("username");
    if (username) {
        document.getElementById("username").textContent = username;
    }

    // Fetch finished goods
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
});


 document.getElementById("btnLogin").addEventListener("click", async () => {
            const username = document.getElementById("inputUsername").value;
            const password = document.getElementById("inputPassword").value;
            const messageBox = document.getElementById("message");

            // Clear previous messages
            messageBox.style.display = "none";
            messageBox.textContent = "";
            messageBox.className = "message-box";

            // Validate inputs
            if (!username || !password) {
                messageBox.textContent = "Please enter both username and password";
                messageBox.classList.add("error");
                messageBox.style.display = "block";
                return;
            }

            try {
                const response = await fetch("/api/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    messageBox.textContent = data.message;
                    messageBox.classList.add("success");
                    messageBox.style.display = "block";
                    
                    // Store username in sessionStorage
                    sessionStorage.setItem("username", username);
                    
                    // Redirect to index page after successful login
                    setTimeout(() => {
                        window.location.href = "/index";
                    }, 1500);
                } else {
                    messageBox.textContent = data.message;
                    messageBox.classList.add("error");
                    messageBox.style.display = "block";
                }
            } catch (error) {
                messageBox.textContent = "An error occurred. Please try again.";
                messageBox.classList.add("error");
                messageBox.style.display = "block";
                console.error("Login error:", error);
            }
        });

        // Allow login by pressing Enter key
        document.getElementById("inputPassword").addEventListener("keypress", (event) => {
            if (event.key === "Enter") {
                document.getElementById("btnLogin").click();
            }
        });


// Password reset functionality
document.getElementById("btnResetPassword").addEventListener("click", async () => {
    const email = document.getElementById("inputEmail").value;
    const messageBox = document.getElementById("message");

    // Clear previous messages
    messageBox.style.display = "none";
    messageBox.textContent = "";
    messageBox.className = "message-box";

    // Validate email
    if (!email) {
        messageBox.textContent = "Please enter your email address";
        messageBox.classList.add("error");
        messageBox.style.display = "block";
        return;
    }

    try {
        const response = await fetch("/api/request-password-reset", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email
            })
        });

        const data = await response.json();

        if (response.ok) {
            messageBox.textContent = "Password reset link sent to your email. Please check your inbox.";
            messageBox.classList.add("success");
            messageBox.style.display = "block";
            document.getElementById("inputEmail").value = "";
        } else {
            messageBox.textContent = data.detail || "Email not found in our system";
            messageBox.classList.add("error");
            messageBox.style.display = "block";
        }
    } catch (error) {
        messageBox.textContent = "An error occurred. Please try again.";
        messageBox.classList.add("error");
        messageBox.style.display = "block";
        console.error("Password reset error:", error);
    }
});