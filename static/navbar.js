// Navbar functionality
document.addEventListener("DOMContentLoaded", function() {
    const hamburger = document.querySelector(".hamburger");
    const navLinks = document.querySelector(".nav-links");

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
    const currentPage = window.location.pathname;
    links.forEach(link => {
        const href = link.getAttribute("href");
        if (href === currentPage || (currentPage === "/" && href === "/index")) {
            link.classList.add("active");
        }
    });
});
