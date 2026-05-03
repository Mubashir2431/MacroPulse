/**
 * Macropulse API Client
 * Fetch wrapper for all backend calls with error handling and loading states.
 */

// Person 3 - US14: Updated to versioned /api/v1 endpoint
const API_BASE = (window.APP_CONFIG && window.APP_CONFIG.apiBase) || `${window.location.origin}/api/v1`;

async function apiRequest(endpoint) {
    const response = await fetch(`${API_BASE}${endpoint}`);
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}`);
    }
    return response.json();
}

/**
 * Search stocks by query string.
 * GET /api/search?q=<query>
 */
async function searchStocks(query) {
    if (!query || query.trim().length === 0) return { results: [] };
    return apiRequest(`/search?q=${encodeURIComponent(query.trim())}`);
}

/**
 * Get current stock info.
 * GET /api/stock/<symbol>
 */
async function getStock(symbol) {
    return apiRequest(`/stock/${encodeURIComponent(symbol)}`);
}

/**
 * Get historical OHLCV data.
 * GET /api/stock/<symbol>/history?period=1y
 */
async function getStockHistory(symbol, period = "1y") {
    return apiRequest(`/stock/${encodeURIComponent(symbol)}/history?period=${period}`);
}

/**
 *
 * GET /api/v1/signals/<symbol>
 */
async function getSignals(symbol) {
    return apiRequest(`/signals/${encodeURIComponent(symbol)}`);
}

/**
 * Get signal history for a stock.
 * GET /api/v1/signals/<symbol>/history
 */
async function getSignalHistory(symbol) {
    return apiRequest(`/signals/${encodeURIComponent(symbol)}/history`);
}

/**
 * Get the server-side watchlist.
 * GET /api/v1/watchlist
 */
async function getWatchlist() {
    return apiRequest(`/watchlist`);
}

/**
 * Add a symbol to the server-side watchlist.
 * POST /api/v1/watchlist/<symbol>
 */
async function addToWatchlist(symbol) {
    const response = await fetch(`${API_BASE}/watchlist/${encodeURIComponent(symbol)}`, { method: "POST" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
}

/**
 * Remove a symbol from the server-side watchlist.
 * DELETE /api/v1/watchlist/<symbol>
 */
async function removeFromWatchlist(symbol) {
    const response = await fetch(`${API_BASE}/watchlist/${encodeURIComponent(symbol)}`, { method: "DELETE" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
}
