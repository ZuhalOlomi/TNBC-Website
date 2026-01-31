// Ensures that it runs on every page
document.addEventListener("DOMContentLoaded", () => {
    const loggedIn = localStorage.getItem("loggedIn") === "true";

    if (loggedIn) {
        const loginBtn = document.querySelector(".btn-secondary");
        if (loginBtn) loginBtn.textContent = "Dashboard";
    }
});

// Login function -- to be fixed later
function login() {
    localStorage.setItem("loggedIn", "true");
    window.location.href = "home.html"; // redirect after login
}

// Logout function
function logout() {
    localStorage.removeItem("loggedIn");
    window.location.href = "home.html";
}
