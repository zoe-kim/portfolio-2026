const root = document.documentElement;
const themeToggle = document.querySelector("#theme-toggle");
const printButton = document.querySelector("#print-button");

const savedTheme = localStorage.getItem("portfolio-theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
const initialTheme = savedTheme || (prefersDark ? "dark" : "light");

function setTheme(theme) {
  const isDark = theme === "dark";
  root.dataset.theme = theme;
  themeToggle.setAttribute("aria-pressed", String(isDark));
  themeToggle.setAttribute(
    "aria-label",
    isDark ? "밝은 테마로 전환" : "어두운 테마로 전환",
  );
  localStorage.setItem("portfolio-theme", theme);
}

setTheme(initialTheme);

themeToggle.addEventListener("click", () => {
  setTheme(root.dataset.theme === "dark" ? "light" : "dark");
});

printButton.addEventListener("click", () => window.print());

console.assert(
  themeToggle && printButton && document.querySelectorAll("[data-project]").length === 4,
  "Portfolio structure is incomplete.",
);
