/**
 * Macropulse - Chart.js price and volume charts.
 */

let priceChart = null;

function renderPriceChart(canvasId, historyData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Destroy existing chart
    if (priceChart) {
        priceChart.destroy();
        priceChart = null;
    }

    const labels = historyData.map((d) => d.date);
    const closePrices = historyData.map((d) => d.close);
    const volumes = historyData.map((d) => d.volume);

    // Determine price color (green if up overall, red if down)
    const firstPrice = closePrices[0];
    const lastPrice = closePrices[closePrices.length - 1];
    const isUp = lastPrice >= firstPrice;
    const lineColor = isUp ? "#3fb950" : "#f85149";
    const fillColor = isUp ? "rgba(63, 185, 80, 0.08)" : "rgba(248, 81, 73, 0.08)";

    // Scale volumes to fit in bottom portion of chart
    const maxPrice = Math.max(...closePrices);
    const minPrice = Math.min(...closePrices);
    const priceRange = maxPrice - minPrice;
    const maxVolume = Math.max(...volumes);
    const scaledVolumes = volumes.map(
        (v) => minPrice - priceRange * 0.02 + (v / maxVolume) * priceRange * 0.2
    );

    
