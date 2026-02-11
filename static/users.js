// Users Management Page JavaScript

document.addEventListener("DOMContentLoaded", function() {
    loadUsers();
    document.getElementById("addUserForm").addEventListener("submit", handleAddUser);
});

// Load and display all users
function loadUsers() {
    fetch("/api/users")
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

    fetch("/api/users", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
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

    fetch(`/api/users/${username}`, {
        method: "DELETE"
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
