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


document.addEventListener("DOMContentLoaded", () => {
    const btnLogin = document.getElementById("btnLogin");
    if (btnLogin) {
        btnLogin.addEventListener("click", async () => {
            const username = document.getElementById("inputUsername").value;
            const password = document.getElementById("inputPassword").value;
            const messageBox = document.getElementById("message");

            // Clear previous messages
            if (messageBox) {
                messageBox.style.display = "none";
                messageBox.textContent = "";
                messageBox.className = "message-box";
            }

            // Validate inputs
            if (!username || !password) {
                if (messageBox) {
                    messageBox.textContent = "Please enter both username and password";
                    messageBox.classList.add("error");
                    messageBox.style.display = "block";
                }
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
                    if (messageBox) {
                        messageBox.textContent = data.message || "Login successful";
                        messageBox.classList.add("success");
                        messageBox.style.display = "block";
                    }

                    // Store username in sessionStorage
                    sessionStorage.setItem("username", username);

                    // Redirect to index page after successful login
                    setTimeout(() => {
                        window.location.href = "/index";
                    }, 1500);
                } else {
                    if (messageBox) {
                        messageBox.textContent = data.message || data.detail || "Login failed";
                        messageBox.classList.add("error");
                        messageBox.style.display = "block";
                    }
                }
            } catch (error) {
                if (messageBox) {
                    messageBox.textContent = "An error occurred. Please try again.";
                    messageBox.classList.add("error");
                    messageBox.style.display = "block";
                }
                console.error("Login error:", error);
            }
        });
    }

    const inputPassword = document.getElementById("inputPassword");
    if (inputPassword) {
        inputPassword.addEventListener("keypress", (event) => {
            if (event.key === "Enter") {
                const btn = document.getElementById("btnLogin");
                if (btn) btn.click();
            }
        });
    }

    // Password reset functionality
    const btnReset = document.getElementById("btnResetPassword");
    if (btnReset) {
        // detect token/email in URL (when user clicked email link)
        const urlParams = new URLSearchParams(window.location.search);
        const tokenParam = urlParams.get('token');
        const emailParam = urlParams.get('email');

        if (tokenParam) {
            // switch modal into "set new password" mode
            const pmEmail = document.getElementById('pm_email');
            const pmToken = document.getElementById('pm_token');
            const newPwFields = document.getElementById('new-password-fields');
            const emailWrapper = document.getElementById('request-email-wrapper');
            const header = document.getElementById('pm_header');
            if (pmEmail) pmEmail.value = emailParam || '';
            if (pmToken) pmToken.value = tokenParam || '';
            if (emailWrapper) emailWrapper.style.display = 'none';
            if (newPwFields) newPwFields.style.display = 'block';
            btnReset.textContent = 'Set New Password';
            if (header) header.textContent = 'Reset Your Password';

            btnReset.addEventListener('click', async () => {
                const messageBox = document.getElementById('message');
                if (messageBox) { messageBox.style.display = 'none'; messageBox.textContent = ''; messageBox.className = 'message-box'; }

                const newPassword = document.getElementById('pm_newPassword').value;
                const confirmPassword = document.getElementById('pm_confirmPassword').value;

                if (!newPassword || !confirmPassword) {
                    if (messageBox) { messageBox.textContent = 'Please enter and confirm your new password'; messageBox.classList.add('error'); messageBox.style.display = 'block'; }
                    return;
                }
                if (newPassword !== confirmPassword) {
                    if (messageBox) { messageBox.textContent = 'Passwords do not match'; messageBox.classList.add('error'); messageBox.style.display = 'block'; }
                    return;
                }

                try {
                    const res = await fetch('/api/reset-password-confirm', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: emailParam, token: tokenParam, new_password: newPassword })
                    });
                    const data = await res.json();
                    if (res.ok) {
                        if (messageBox) { messageBox.textContent = data.message || 'Password reset successful'; messageBox.classList.add('success'); messageBox.style.display = 'block'; }
                        setTimeout(() => { window.location.href = '/'; }, 1500);
                    } else {
                        if (messageBox) { messageBox.textContent = data.message || data.detail || 'Unable to reset password'; messageBox.classList.add('error'); messageBox.style.display = 'block'; }
                    }
                } catch (err) {
                    if (messageBox) { messageBox.textContent = 'An error occurred. Please try again.'; messageBox.classList.add('error'); messageBox.style.display = 'block'; }
                    console.error('Password reset confirm error', err);
                }
            });

            // skip adding the "request reset" handler below
            return;
        }
        btnReset.addEventListener("click", async () => {
            const emailEl = document.getElementById("inputEmail");
            const email = emailEl ? emailEl.value : null;
            const messageBox = document.getElementById("message");

            // Clear previous messages
            if (messageBox) {
                messageBox.style.display = "none";
                messageBox.textContent = "";
                messageBox.className = "message-box";
            }

            // Validate email
            if (!email) {
                if (messageBox) {
                    messageBox.textContent = "Please enter your email address";
                    messageBox.classList.add("error");
                    messageBox.style.display = "block";
                }
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
                    if (messageBox) {
                        messageBox.textContent = "Password reset link sent to your email. Please check your inbox.";
                        messageBox.classList.add("success");
                        messageBox.style.display = "block";
                    }
                    if (emailEl) emailEl.value = "";
                } else {
                    if (messageBox) {
                        messageBox.textContent = data.detail || data.message || "Email not found in our system";
                        messageBox.classList.add("error");
                        messageBox.style.display = "block";
                    }
                }
            } catch (error) {
                if (messageBox) {
                    messageBox.textContent = "An error occurred. Please try again.";
                    messageBox.classList.add("error");
                    messageBox.style.display = "block";
                }
                console.error("Password reset error:", error);
            }
        });
    }
});

// Handler for reset-password page (setting the new password)
document.addEventListener("DOMContentLoaded", () => {
    const btnSubmit = document.getElementById("btnSubmitNewPassword");
    if (!btnSubmit) return;

    btnSubmit.addEventListener("click", async () => {
        const email = document.getElementById("email").value;
        const token = document.getElementById("token").value;
        const newPassword = document.getElementById("newPassword").value;
        const confirmPassword = document.getElementById("confirmPassword").value;
        const msg = document.getElementById("resetMessage");

        if (msg) { msg.style.display = 'none'; msg.textContent = ''; msg.className = 'message-box'; }

        if (!newPassword || !confirmPassword) {
            if (msg) { msg.textContent = 'Please enter and confirm your new password'; msg.classList.add('error'); msg.style.display = 'block'; }
            return;
        }
        if (newPassword !== confirmPassword) {
            if (msg) { msg.textContent = 'Passwords do not match'; msg.classList.add('error'); msg.style.display = 'block'; }
            return;
        }

        try {
            const res = await fetch('/api/reset-password-confirm', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, token: token, new_password: newPassword })
            });

            const data = await res.json();
            if (res.ok) {
                if (msg) { msg.textContent = data.message || 'Password reset successful'; msg.classList.add('success'); msg.style.display = 'block'; }
                setTimeout(() => { window.location.href = '/'; }, 2000);
            } else {
                if (msg) { msg.textContent = data.message || data.detail || 'Unable to reset password'; msg.classList.add('error'); msg.style.display = 'block'; }
            }
        } catch (e) {
            if (msg) { msg.textContent = 'An error occurred. Please try again.'; msg.classList.add('error'); msg.style.display = 'block'; }
            console.error('Reset password error', e);
        }
    });
});
