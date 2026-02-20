// Users Management Page JavaScript

document.addEventListener("DOMContentLoaded", function() {
    initializeUsersPage();
    initializePasswordModal();
});

async function initializeUsersPage() {
    if (typeof syncCurrentUserPermissions === "function") {
        await syncCurrentUserPermissions();
    }

    const isAdmin = sessionStorage.getItem("is_admin") === "true";
    if (!isAdmin) {
        window.location.href = "/index";
        return;
    }

    loadUsers();
    document.getElementById("addUserForm").addEventListener("submit", handleAddUser);
}

// Load and display all users
function loadUsers() {
    fetch("/users/users", {
        headers: {
            ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
        }
    })
        .then(response => response.json())
        .then(users => {
            const tbody = document.getElementById("usersTableBody");
            tbody.innerHTML = "";

            if (users.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" style="text-align: center;">No users found</td></tr>';
                return;
            }

            users.forEach(user => {
                const row = document.createElement("tr");
                const adminStatus = user.isadmin ? 
                    '<span class="admin-badge">Admin</span>' : 
                    '<span class="user-badge">User</span>';
                
                row.innerHTML = `
                    <td>${user.username}</td>
                    <td>${adminStatus}</td>
                    <td>
                        <button class="btn-delete" onclick="deleteUser('${user.username}')">
                            <i class="fa fa-trash"></i> Delete
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error("Error loading users:", error);
            const tbody = document.getElementById("usersTableBody");
            tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: red;">Error loading users</td></tr>';
        });
}

// Handle adding a new user
function handleAddUser(event) {
    event.preventDefault();

    const username = document.getElementById("newUsername").value.trim();
    const password = document.getElementById("newPassword").value;
    const isAdmin = document.getElementById("isAdmin").checked;
    const messageBox = document.getElementById("addUserMessage");

    // Validation
    if (!username || !password) {
        showMessage(messageBox, "Please fill in all fields", "error");
        return;
    }

    if (password.length < 6) {
        showMessage(messageBox, "Password must be at least 6 characters", "error");
        return;
    }

    fetch("/users/add-user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
        },
        body: JSON.stringify({
            username: username,
            password: password,
            is_admin: isAdmin
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                showMessage(messageBox, "User added successfully!", "success");
                document.getElementById("addUserForm").reset();
                loadUsers(); // Reload the users list
                setTimeout(() => messageBox.classList.remove("success"), 3000);
            } else {
                showMessage(messageBox, data.message || "Error adding user", "error");
            }
        })
        .catch(error => {
            console.error("Error adding user:", error);
            showMessage(messageBox, "An error occurred while adding the user", "error");
        });
}

// Delete a user
function deleteUser(username) {
    if (!confirm(`Are you sure you want to delete user "${username}"?`)) {
        return;
    }

    fetch(`/users/delete-user/${username}`, {
        method: "DELETE",
        headers: {
            ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("User deleted successfully!");
                loadUsers(); // Reload the users list
            } else {
                alert(data.message || "Error deleting user");
            }
        })
        .catch(error => {
            console.error("Error deleting user:", error);
            alert("An error occurred while deleting the user");
        });
}

// Helper function to show messages
function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `message-box ${type}`;
    if (type === "error") {
        setTimeout(() => element.classList.remove("error"), 4000);
    }
}

// Initialize password change modal
function initializePasswordModal() {
    const modal = document.getElementById("passwordChangeModal");
    const openBtn = document.getElementById("btnOpenPasswordModal");
    const closeBtn = document.querySelector(".close-modal");
    const form = document.getElementById("changePasswordForm");

    // Open modal
    openBtn.addEventListener("click", function() {
        modal.style.display = "flex";
        form.reset();
        document.getElementById("passwordChangeMessage").className = "message-box";
        document.getElementById("passwordChangeMessage").textContent = "";
    });

    // Close modal
    closeBtn.addEventListener("click", function() {
        modal.style.display = "none";
    });

    // Close modal when clicking outside
    window.addEventListener("click", function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // Handle form submission
    form.addEventListener("submit", handlePasswordChange);
}

// Handle password change
async function handlePasswordChange(event) {
    event.preventDefault();

    const currentPassword = document.getElementById("currentPassword").value;
    const newPassword = document.getElementById("modalNewPassword").value;
    const confirmPassword = document.getElementById("modalConfirmPassword").value;
    const messageBox = document.getElementById("passwordChangeMessage");
    const username = sessionStorage.getItem("username");

    // Validation
    if (newPassword.length < 6) {
        showMessage(messageBox, "New password must be at least 6 characters", "error");
        return;
    }

    if (newPassword !== confirmPassword) {
        showMessage(messageBox, "New passwords do not match", "error");
        return;
    }

    if (currentPassword === newPassword) {
        showMessage(messageBox, "New password must be different from current password", "error");
        return;
    }

    try {
        const response = await fetch("/users/user-reset-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...(typeof getAuthHeaders === "function" ? getAuthHeaders() : {})
            },
            body: JSON.stringify({
                username: username,
                old_password: currentPassword,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (response.ok && data.status === "success") {
            showMessage(messageBox, "Password changed successfully!", "success");
            setTimeout(() => {
                document.getElementById("passwordChangeModal").style.display = "none";
                document.getElementById("changePasswordForm").reset();
            }, 2000);
        } else {
            showMessage(messageBox, data.detail || data.message || "Error changing password", "error");
        }
    } catch (error) {
        console.error("Error changing password:", error);
        showMessage(messageBox, "An error occurred while changing password", "error");
    }
}

