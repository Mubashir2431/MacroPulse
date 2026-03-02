/**
 * Macropulse - Dashboard Logic
 * Search bar with debounce, trending stocks, navigation.
 */

const TRENDING_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"];
const WATCHLIST_SYMBOLS = ["META", "JPM", "V", "JNJ", "WMT", "DIS"];

let searchTimeout = null;

document.addEventListener("DOMContentLoaded", () => {
    initSearch();
    loadTrendingStocks();
    loadWatchlistStocks();
});

// ===== Search =====

function initSearch() {
    const input = document.getElementById("search-input");
    const dropdown = document.getElementById("search-dropdown");

    input.addEventListener("input", () => {
        const query = input.value.trim();
        if (searchTimeout) clearTimeout(searchTimeout);

        if (query.length === 0) {
            dropdown.classList.remove("active");
            return;
        }

        // Debounce: wait 350ms after typing stops
        searchTimeout = setTimeout(() => performSearch(query), 350);
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".search-wrapper")) {
            dropdown.classList.remove("active");
        }
    });

    // Navigate on enter with first result
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            const firstItem = dropdown.querySelector(".search-result-item");
            if (firstItem) {
                firstItem.click();
            } else {
                const query = input.value.trim().toUpperCase();
                if (query) navigateToStock(query);
            }
        }
    });
}

async function performSearch(query) {
    const dropdown = document.getElementById("search-dropdown");

    dropdown.innerHTML = `<div class="search-loading"><i class="fa-solid fa-spinner fa-spin"></i> Searching...</div>`;
    dropdown.classList.add("active");

    try {
        const data = await searchStocks(query);
        if (data.results.length === 0) {
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
    } catch (err) {
        dropdown.innerHTML = `<div class="search-no-results">Search error. Is the backend running?</div>`;
    }
}

function navigateToStock(symbol) {
    window.location.href = `stock.html?symbol=${encodeURIComponent(symbol)}`;
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
/**
 * Macropulse - Dashboard Logic
 * Search bar with debounce, trending stocks, navigation.
 */

const TRENDING_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"];
const WATCHLIST_SYMBOLS = ["META", "JPM", "V", "JNJ", "WMT", "DIS"];

let searchTimeout = null;

document.addEventListener("DOMContentLoaded", () => {
    initSearch();
    loadTrendingStocks();
    loadWatchlistStocks();
});

// ===== Search =====

function initSearch() {
    const input = document.getElementById("search-input");
    const dropdown = document.getElementById("search-dropdown");

    input.addEventListener("input", () => {
        const query = input.value.trim();
        if (searchTimeout) clearTimeout(searchTimeout);

        if (query.length === 0) {
            dropdown.classList.remove("active");
            return;
        }

        // Debounce: wait 350ms after typing stops
        searchTimeout = setTimeout(() => performSearch(query), 350);
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".search-wrapper")) {
            dropdown.classList.remove("active");
        }
    });

    // Navigate on enter with first result
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            const firstItem = dropdown.querySelector(".search-result-item");
            if (firstItem) {
                firstItem.click();
            } else {
                const query = input.value.trim().toUpperCase();
                if (query) navigateToStock(query);
            }
        }
    });
}

async function performSearch(query) {
    const dropdown = document.getElementById("search-dropdown");

    dropdown.innerHTML = `<div class="search-loading"><i class="fa-solid fa-spinner fa-spin"></i> Searching...</div>`;
    dropdown.classList.add("active");

    try {
        const data = await searchStocks(query);
        if (data.results.length === 0) {
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
    } catch (err) {
        dropdown.innerHTML = `<div class="search-no-results">Search error. Is the backend running?</div>`;
    }
}

function navigateToStock(symbol) {
    window.location.href = `stock.html?symbol=${encodeURIComponent(symbol)}`;
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
