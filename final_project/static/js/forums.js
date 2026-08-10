/**
 * Forums page interactions.
 *
 * Voting, replying, and creating posts are now real Django forms (see
 * forums.html) that POST to the server and reload the page — no JS needed
 * for those anymore. What's left here is purely cosmetic, client-side-only
 * UI that doesn't touch the database: expanding a comment thread, and
 * re-sorting/filtering the posts that are already on the page.
 */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    initCommentToggles();
    initSortTabs();
    initCategoryFilters();
  });

  /** Expands/collapses a post's comment thread. */
  function initCommentToggles() {
    document.querySelectorAll(".post-action-btn.comments-toggle").forEach((btn) => {
      btn.addEventListener("click", () => {
        const panel = document.getElementById(btn.dataset.commentsTarget);
        if (!panel) return;
        panel.classList.toggle("d-none");
      });
    });
  }

  /** "Hot" keeps original order, "New" sorts newest-first, "Top" sorts by votes. */
  function initSortTabs() {
    const tabs = document.querySelectorAll(".sort-tab");
    const feed = document.getElementById("postFeed");
    if (!tabs.length || !feed) return;

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");

        const cards = Array.from(feed.querySelectorAll(".post-card"));
        const sortBy = tab.dataset.sort;

        cards.sort((a, b) => {
          if (sortBy === "top") {
            return parseInt(b.dataset.votes, 10) - parseInt(a.dataset.votes, 10);
          }
          if (sortBy === "new") {
            return parseInt(b.dataset.order, 10) - parseInt(a.dataset.order, 10);
          }
          // "hot": original document order (server returns newest-first already)
          return parseInt(a.dataset.order, 10) - parseInt(b.dataset.order, 10);
        });

        cards.forEach((card) => feed.appendChild(card));
      });
    });
  }

  /** Shows/hides post cards based on the selected category chip. */
  function initCategoryFilters() {
    const chips = document.querySelectorAll(".chip[data-filter]");
    const cards = document.querySelectorAll(".post-card");
    if (!chips.length) return;

    chips.forEach((chip) => {
      chip.addEventListener("click", () => {
        chips.forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");

        const filter = chip.dataset.filter;
        cards.forEach((card) => {
          const match = filter === "all" || card.dataset.category === filter;
          card.classList.toggle("d-none", !match);
        });
      });
    });
  }
})();
