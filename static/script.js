function openSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;
  sidebar.style.width = "260px";
  document.body.style.overflow = "hidden";
  sidebar.setAttribute("aria-hidden", "false");
}

function closeSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;
  sidebar.style.width = "0";
  document.body.style.overflow = "";
  sidebar.setAttribute("aria-hidden", "true");
}

document.addEventListener("DOMContentLoaded", () => {
  const resultContainers = document.querySelectorAll(".result-card");
  resultContainers.forEach(r => r.style.display = "none");

  // Close sidebar when clicking outside it (for better UX)
  document.addEventListener("click", (e) => {
    const sidebar = document.getElementById("sidebar");
    const menuBtn = document.querySelector(".menu-icon");
    if (!sidebar) return;
    const isClickInsideSidebar = sidebar.contains(e.target);
    const isClickOnMenu = menuBtn && menuBtn.contains(e.target);

    if (!isClickInsideSidebar && !isClickOnMenu && sidebar.style.width && sidebar.style.width !== "0px") {
      closeSidebar();
    }
  });

  // Close sidebar with Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeSidebar();
  });

  // Make sure sidebar has appropriate aria-hidden state initially
  const sidebar = document.getElementById("sidebar");
  if (sidebar) sidebar.setAttribute("aria-hidden", "true");
});
