/**
 * News page interactions — category filter chips and Latest/Trending/Popular
 * sort tabs for the News grid. "Read More" everywhere is a plain Bootstrap
 * modal (data-bs-toggle, no JS needed). Purely client-side; nothing here
 * fetches or persists data anywhere.
 */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    initCategoryFilters();
    initSortTabs();
  });

  function initCategoryFilters() {
    const chips = document.querySelectorAll(".tag-chip[data-filter]");
    const cols = document.querySelectorAll(".article-col");
    if (!chips.length) return;

    chips.forEach((chip) => {
      chip.addEventListener("click", () => {
        chips.forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");

        const filter = chip.dataset.filter;
        cols.forEach((col) => {
          const match = filter === "all" || col.dataset.category === filter;
          col.classList.toggle("d-none", !match);
        });
      });
    });
  }

  /** "Latest" keeps original order, "Trending" sorts by trend rank, "Popular" by views. */
  function initSortTabs() {
    const tabs = document.querySelectorAll(".sort-tab");
    const grid = document.getElementById("newsGrid");
    if (!tabs.length || !grid) return;

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");

        const cols = Array.from(grid.querySelectorAll(".article-col"));
        const sortBy = tab.dataset.sort;

        cols.sort((a, b) => {
          if (sortBy === "popular") {
            return parseInt(b.dataset.views, 10) - parseInt(a.dataset.views, 10);
          }
          if (sortBy === "trending") {
            return parseInt(a.dataset.trend, 10) - parseInt(b.dataset.trend, 10);
          }
          return parseInt(a.dataset.order, 10) - parseInt(b.dataset.order, 10);
        });

        cols.forEach((col) => grid.appendChild(col));
      });
    });
  }
})();
