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

    priceChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Price",
                    data: closePrices,
                    borderColor: lineColor,
                    backgroundColor: fillColor,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHitRadius: 10,
                    yAxisID: "y",
                },
                {
                    label: "Volume",
                    data: scaledVolumes,
                    type: "bar",
                    backgroundColor: "rgba(88, 166, 255, 0.15)",
                    borderColor: "transparent",
                    yAxisID: "y",
                    barPercentage: 0.8,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false,
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "#161b22",
                    borderColor: "#30363d",
                    borderWidth: 1,
                    titleColor: "#e6edf3",
                    bodyColor: "#8b949e",
                    padding: 12,
                    callbacks: {
                        label: function (context) {
                            if (context.datasetIndex === 0) {
                                return `Price: $${context.parsed.y.toFixed(2)}`;
                            }
                            const idx = context.dataIndex;
                            return `Volume: ${(volumes[idx] / 1e6).toFixed(1)}M`;
                        },
                    },
                },
            },
            scales: {
                x: {
                    grid: { color: "rgba(48, 54, 61, 0.5)" },
                    ticks: {
                        color: "#6e7681",
                        maxTicksLimit: 8,
                        maxRotation: 0,
                    },
                    border: { color: "#30363d" },
                },
                y: {
                    position: "right",
                    grid: { color: "rgba(48, 54, 61, 0.5)" },
                    ticks: {
                        color: "#6e7681",
                        callback: (val) => "$" + val.toFixed(0),
                    },
                    border: { color: "#30363d" },
                },
            },
        },
    });
}
