// Navbar functionality
document.addEventListener("DOMContentLoaded", async function() {
    const hamburger = document.querySelector(".hamburger");
    const navLinks = document.querySelector(".nav-links");
    const currentPage = window.location.pathname;

    if (typeof syncCurrentUserPermissions === "function" && sessionStorage.getItem("session_token")) {
        await syncCurrentUserPermissions();
    }

    const isAdmin = sessionStorage.getItem("is_admin") === "true";
    const adminOnlyItems = document.querySelectorAll(".nav-links li.admin-only");
    adminOnlyItems.forEach(item => {
        if (isAdmin) {
            item.style.display = "list-item";
        } else {
            item.remove();
        }
    });

    const usersLink = document.querySelector('.nav-links a[href="/users"]');
    if (usersLink && !isAdmin) {
        const usersListItem = usersLink.closest("li");
        if (usersListItem) {
            usersListItem.remove();
        }
    }

    if (currentPage === "/users" && !isAdmin) {
        window.location.href = "/index";
        return;
    }

    // Toggle mobile menu
    if (hamburger) {
        hamburger.addEventListener("click", function() {
            navLinks.classList.toggle("active");
        });
    }

    // Close menu when a link is clicked
    const links = document.querySelectorAll(".nav-links a");
    links.forEach(link => {
        link.addEventListener("click", function() {
            navLinks.classList.remove("active");
        });
    });

    // Set active link based on current page
    links.forEach(link => {
        const href = link.getAttribute("href");
        if (href === currentPage || (currentPage === "/" && href === "/index")) {
            link.classList.add("active");
        }
    });
});
