(function () {
  "use strict";

  const DEBOUNCE_MS = 250;

  function createDebouncer(waitMs, scheduler, callback) {
    let timer = null;

    return function debounced(...args) {
      if (timer) {
        scheduler.clear(timer);
      }
      timer = scheduler.set(function invoke() {
        timer = null;
        callback.apply(null, args);
      }, waitMs);
    };
  }

  function createStaleGuard() {
    let latestToken = 0;

    return {
      next: function nextToken() {
        latestToken += 1;
        return latestToken;
      },
      isCurrent: function isCurrent(token) {
        return token === latestToken;
      },
    };
  }

  function toInt(value, fallback) {
    const parsed = parseInt(value, 10);
    return Number.isFinite(parsed) ? parsed : fallback;
  }

  function buildAutocompleteRuntime(root) {
    const input = root.querySelector(".django-smart-filters-autocomplete__input");
    const hiddenValue = root.querySelector('[data-role="autocomplete-value"]');
    const selectedLabel = root.querySelector('[data-role="selected-label"]');
    const resultsList = root.querySelector('[data-role="results"]');
    const loadMoreButton = root.querySelector('[data-role="load-more"]');

    if (!input || !hiddenValue || !selectedLabel || !resultsList || !loadMoreButton) {
      return null;
    }

    const endpoint = root.getAttribute("data-autocomplete-url") || "";
    const field = root.getAttribute("data-autocomplete-field") || "";
    const minQueryLength = toInt(root.getAttribute("data-min-query-length"), 2);
    const pageSize = toInt(root.getAttribute("data-page-size"), 20);

    const staleGuard = createStaleGuard();
    let currentQuery = "";
    let currentPage = 1;
    let hasNext = false;

    function setLoadMoreVisible(visible) {
      loadMoreButton.style.display = visible ? "inline-block" : "none";
    }

    function renderResults(results, append) {
      if (!append) {
        resultsList.innerHTML = "";
      }

      results.forEach(function (item) {
        const li = document.createElement("li");
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = item.label;
        button.dataset.value = item.value;
        button.dataset.label = item.label;
        button.className = "django-smart-filters-autocomplete__option";
        li.appendChild(button);
        resultsList.appendChild(li);
      });
    }

    function applySelection(value, label) {
      hiddenValue.value = value;
      selectedLabel.textContent = label;
      input.value = label;
      setLoadMoreVisible(false);
    }

    function requestPage(query, page, append) {
      if (query.length < minQueryLength) {
        renderResults([], false);
        setLoadMoreVisible(false);
        return Promise.resolve({ skipped: true });
      }

      const params = new URLSearchParams();
      params.set("field", field);
      params.set("query", query);
      params.set("page", String(page));
      params.set("limit", String(pageSize));

      const token = staleGuard.next();
      return fetch(endpoint + "?" + params.toString(), {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then(function (response) {
          return response.json();
        })
        .then(function (payload) {
          if (!staleGuard.isCurrent(token)) {
            return { stale: true };
          }

          const results = payload.results || [];
          renderResults(results, append);

          const pagination = payload.pagination || {};
          hasNext = Boolean(pagination.has_next);
          currentPage = toInt(pagination.page, page);
          setLoadMoreVisible(hasNext);

          return { stale: false, payload: payload };
        })
        .catch(function () {
          setLoadMoreVisible(false);
          return { error: true };
        });
    }

    const debouncedSearch = createDebouncer(
      DEBOUNCE_MS,
      {
        set: function (cb, ms) {
          return window.setTimeout(cb, ms);
        },
        clear: function (id) {
          window.clearTimeout(id);
        },
      },
      function (value) {
        currentQuery = value;
        currentPage = 1;
        requestPage(value, 1, false);
      }
    );

    input.addEventListener("input", function () {
      debouncedSearch(input.value.trim());
    });

    loadMoreButton.addEventListener("click", function () {
      if (!hasNext) {
        return;
      }
      requestPage(currentQuery, currentPage + 1, true);
    });

    resultsList.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) {
        return;
      }

      if (!target.classList.contains("django-smart-filters-autocomplete__option")) {
        return;
      }

      applySelection(target.dataset.value || "", target.dataset.label || "");
    });

    return {
      requestPage: requestPage,
      applySelection: applySelection,
      getState: function () {
        return {
          currentQuery: currentQuery,
          currentPage: currentPage,
          hasNext: hasNext,
        };
      },
    };
  }

  function initAutocompleteControls() {
    const roots = document.querySelectorAll('[data-smart-filter-autocomplete="true"]');
    roots.forEach(function (root) {
      buildAutocompleteRuntime(root);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAutocompleteControls);
  } else {
    initAutocompleteControls();
  }

  window.DjangoSmartFiltersAutocomplete = {
    DEBOUNCE_MS: DEBOUNCE_MS,
    createDebouncer: createDebouncer,
    createStaleGuard: createStaleGuard,
    buildAutocompleteRuntime: buildAutocompleteRuntime,
  };
})();
