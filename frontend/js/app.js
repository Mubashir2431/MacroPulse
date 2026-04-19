/**
 * Macropulse - Dashboard Logic
 * Search bar with debounce, trending stocks, navigation.
 */

const TRENDING_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"];
const WATCHLIST_SYMBOLS = ["META", "JPM", "V", "JNJ", "WMT", "DIS"];

/* Yash Patel, 04/17/2026
Add new const variable and call function*/
const SAVED_STOCKS_KEY = "macropulseSavedStocks";

let searchTimeout = null;
let selectedSearchIndex = -1;

document.addEventListener("DOMContentLoaded", () => {
    initSearch();
    loadTrendingStocks();
    loadWatchlistStocks();
    loadSavedStocks();
});

// ===== Search =====

function initSearch() {
    const input = document.getElementById("search-input");
    const dropdown = document.getElementById("search-dropdown");

    input.addEventListener("input", () => {
        const query = input.value.trim();
        if (searchTimeout) clearTimeout(searchTimeout);
        selectedSearchIndex = -1;

        if (query.length === 0) {
            dropdown.classList.remove("active");
            updateSearchSelection(dropdown);
            return;
        }

        // Debounce: wait 350ms after typing stops
        searchTimeout = setTimeout(() => performSearch(query), 350);
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".search-wrapper")) {
            dropdown.classList.remove("active");
            selectedSearchIndex = -1;
            updateSearchSelection(dropdown);
        }
    });

    input.addEventListener("keydown", (e) => {
        const results = getSearchResults(dropdown);

        if (e.key === "ArrowDown") {
            if (results.length === 0) return;
            e.preventDefault();
            moveSearchSelection(dropdown, 1);
            return;
        }

        if (e.key === "ArrowUp") {
            if (results.length === 0) return;
            e.preventDefault();
            moveSearchSelection(dropdown, -1);
            return;
        }

        if (e.key === "Escape") {
            dropdown.classList.remove("active");
            selectedSearchIndex = -1;
            updateSearchSelection(dropdown);
            return;
        }

        if (e.key === "Enter") {
            const selectedItem = results[selectedSearchIndex];
            const firstItem = results[0];
            const targetItem = selectedItem || firstItem;

            if (targetItem) {
                e.preventDefault();
                targetItem.click();
                return;
            }

            const query = input.value.trim().toUpperCase();
            if (query) {
                navigateToStock(query);
            }
        }
    });
}

async function performSearch(query) {
    const dropdown = document.getElementById("search-dropdown");
    selectedSearchIndex = -1;

    dropdown.innerHTML = `<div class="search-loading"><i class="fa-solid fa-spinner fa-spin"></i> Searching...</div>`;
    dropdown.classList.add("active");

    try {
        const data = await searchStocks(query);
        // Person 1 - US8: Handle consistent error format from updated search API
        if (data.error) {
            dropdown.innerHTML = `<div class="search-no-results">${data.error}</div>`;
            return;
        }
        if (!data.results || data.results.length === 0) {
            dropdown.innerHTML = `<div class="search-no-results">No results found for "${query}"</div>`;
            return;
        }

        dropdown.innerHTML = data.results
            .slice(0, 8)
            .map(
                (r) => `
                <div class="search-result-item" onclick="navigateToStock('${r.symbol}')">
                    <span class="symbol">${r.symbol}</span>
                    <span class="name">${r.name}</span>
                    <span class="exchange">${r.exchange}</span>
                </div>
            `
            )
            .join("");

        attachSearchResultInteractions(dropdown);
        updateSearchSelection(dropdown);
    } catch (err) {
        dropdown.innerHTML = `<div class="search-no-results">Search error. Is the backend running?</div>`;
    }
}

function navigateToStock(symbol) {
    window.location.href = `stock.html?symbol=${encodeURIComponent(symbol)}`;
}

/* Yash Patel, 04/17/2026 
Retrieves, cleans, deduplicates, and returns saved stock symbols from localStorage safely*/
function getSavedStocks() {
    try {
        const saved = JSON.parse(localStorage.getItem(SAVED_STOCKS_KEY) || "[]");
        if (!Array.isArray(saved)) return [];

        return saved
            .map((symbol) => String(symbol || "").trim().toUpperCase())
            .filter((symbol, index, arr) => symbol && arr.indexOf(symbol) === index);
    } catch {
        return [];
    }
}

window.getSavedStocks = getSavedStocks;

function getSearchResults(dropdown) {
    return Array.from(dropdown.querySelectorAll(".search-result-item"));
}

function moveSearchSelection(dropdown, direction) {
    const results = getSearchResults(dropdown);
    if (results.length === 0) return;

    selectedSearchIndex =
        selectedSearchIndex < 0
            ? direction > 0
                ? 0
                : results.length - 1
            : (selectedSearchIndex + direction + results.length) % results.length;

    updateSearchSelection(dropdown);
}

function updateSearchSelection(dropdown) {
    const results = getSearchResults(dropdown);

    results.forEach((item, index) => {
        const isSelected = index === selectedSearchIndex;
        item.style.backgroundColor = isSelected ? "rgba(88, 166, 255, 0.12)" : "";
        item.style.outline = isSelected ? "1px solid rgba(88, 166, 255, 0.35)" : "";
        item.style.borderRadius = isSelected ? "10px" : "";
        item.setAttribute("aria-selected", isSelected ? "true" : "false");

        if (isSelected) {
            item.scrollIntoView({ block: "nearest" });
        }
    });
}

function attachSearchResultInteractions(dropdown) {
    const results = getSearchResults(dropdown);

    results.forEach((item, index) => {
        item.addEventListener("mouseenter", () => {
            selectedSearchIndex = index;
            updateSearchSelection(dropdown);
        });

        item.addEventListener("mouseleave", () => {
            selectedSearchIndex = -1;
            updateSearchSelection(dropdown);
        });
    });
}

// ===== Trending Stocks =====

async function loadTrendingStocks() {
    const grid = document.getElementById("trending-grid");
    const loading = document.getElementById("trending-loading");

    try {
        const cards = await Promise.allSettled(
            TRENDING_SYMBOLS.map((sym) => loadStockCard(sym))
        );

        loading.style.display = "none";

        const html = cards
            .filter((r) => r.status === "fulfilled" && r.value)
            .map((r) => r.value)
            .join("");

        if (html) {
            grid.innerHTML = html;
        } else {
            grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-plug-circle-xmark"></i><p>Could not load trending stocks. Make sure the backend is running.</p></div>`;
        }
    } catch {
        loading.style.display = "none";
        grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-plug-circle-xmark"></i><p>Backend connection failed.</p></div>`;
    }
}

async function loadWatchlistStocks() {
    const grid = document.getElementById("watchlist-grid");

    try {
        const cards = await Promise.allSettled(
            WATCHLIST_SYMBOLS.map((sym) => loadStockCard(sym))
        );

        const html = cards
            .filter((r) => r.status === "fulfilled" && r.value)
            .map((r) => r.value)
            .join("");

        if (html) {
            grid.innerHTML = html;
        } else {
            grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-chart-bar"></i><p>Could not load watchlist stocks.</p></div>`;
        }
    } catch {
        grid.innerHTML = "";
    }
}

/* Yash Patel, 04/17/2026 
Loads saved stocks, fetches cards, and displays successful results in grid*/
async function loadSavedStocks() {
    const grid = document.getElementById("saved-stocks-grid");
    if (!grid) return;

    const savedSymbols = getSavedStocks();

    if (savedSymbols.length === 0) {
        grid.innerHTML = "";
        return;
    }

    try {
        const cards = await Promise.allSettled(
            savedSymbols.map((sym) => loadStockCard(sym))
        );

        const html = cards
            .filter((r) => r.status === "fulfilled" && r.value)
            .map((r) => r.value)
            .join("");

        if (html) {
            grid.innerHTML = html;
        } else {
            grid.innerHTML = "";
        }
    } catch {
        grid.innerHTML = "";
    }
}

async function loadStockCard(symbol) {
    try {
        const data = await getStock(symbol);
        const changeClass = data.change >= 0 ? "positive" : "negative";
        const changeIcon = data.change >= 0 ? "fa-caret-up" : "fa-caret-down";
        const changeSign = data.change >= 0 ? "+" : "";

        return `
            <div class="stock-card" onclick="navigateToStock('${data.symbol}')">
                <div class="stock-header">
                    <div>
                        <div class="ticker">${data.symbol}</div>
                        <div class="stock-name">${data.name}</div>
                    </div>
                </div>
                <div class="price">$${data.price.toFixed(2)}</div>
                <div class="change ${changeClass}">
                    <i class="fa-solid ${changeIcon}"></i>
                    ${changeSign}${data.change.toFixed(2)} (${changeSign}${data.changePercent.toFixed(2)}%)
                </div>
            </div>
        `;
    } catch {
        return null;
    }
}
