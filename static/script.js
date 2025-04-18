// Open Sidebar
function openSidebar() {
    document.getElementById("sidebar").style.width = "250px";
}

// Close Sidebar
function closeSidebar() {
    document.getElementById("sidebar").style.width = "0";
}

// Close Sidebar when clicking outside
window.onclick = function(event) {
    if (!event.target.closest('.sidebar') && !event.target.closest('.menu-icon')) {
        closeSidebar();
    }
};
