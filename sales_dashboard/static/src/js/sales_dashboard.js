/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
const { onWillStart } = owl;

class SalesDashboard extends Component {
    static template = "sales_dashboard.SalesDashboard";

    // Initialize state in the setup method
    setup() {
        this.orm = this.env.services.orm;

        // Initialize state variables using useState
        this.state = useState({
            totalSales: 0,
            totalSalesChange: 0,
            companySales: [],  // Holds sales data for each company
            linearGraphData: [],
            dailySalesGraphData: [],
            monthlySalesData: [],
            orderAvg: 0,
            orderCount: 0,
            discountAvg: 0,
            orderAvgChange: 0,
            orderCountChange: 0,
            discountAvgChange: 0,
            loading: true,
            currentProductData: [],  // State for current month product inventory
            previousProductData: [], // State for previous month product inventory
            currentTotalQuantity: 0,  // Total quantity for current month products
            currentTotalCost: 0,       // Total cost for current month products
            previousTotalQuantity: 0,  // Total quantity for previous month products
            previousTotalCost: 0,      // Total cost for previous month products
            todaySales: 0,             // State for today's sales amount
            todaySalesChange: 0,       // Change in today's sales compared to the same day last month
            sellerRanking: [],         // Seller ranking data
            todaySalesData: [],        // New state for today's sales data by company
            bestSellingProducts: [],
            monthlyPaymentsData: [], // Stores payments data
            categories: [],          // List of categories (CASH, BANKS, ROOMCHARGE)
            paymentMethods: {},
            payment_methods_names: {},
            currency_payments: {},
        });

        this.state.expandedTodayRows = useState({});

        // Use onWillStart to load data before component is rendered
        onWillStart(async () => {
            await this.loadSalesData();
        });

        // Use onMounted to render the graph once the component is rendered
        onMounted(() => {
            this.renderGraph();
            this.addToggleListeners();
            this.renderDailySalesGraph();
            this.renderCategoryBarGraph();
        });
    }

    addToggleListeners() {
        // Find all rows with the 'sales-section' class
        const salesRows = document.querySelectorAll(".sales-section");
        salesRows.forEach((row) => {
            row.addEventListener("click", () => {
                // Toggle visibility of the next sibling row with 'ticket-section'
                const nextRow = row.nextElementSibling;
                if (nextRow && nextRow.classList.contains("ticket-section")) {
                    nextRow.classList.toggle("ticket-show");
                }
            });
        });
    }
    // Class method to fetch and load sales data
    async loadSalesData() {
        try {
            console.log("Loading sales data...");

            // Fetch data from the backend using ORM service
            const result = await this.orm.call("pos.order", "get_dashboard_data", []);

            // Update state with fetched data
            this.state.totalSales = result.total_sales;
            this.state.totalSalesChange = result.total_sales_change;
            this.state.companySales = result.daily_sales;
            this.state.todaySales = result.today_sales;
            this.state.todaySalesChange = result.today_sales_change;
            this.state.linearGraphData = result.linear_graph_data || [];
            this.state.orderAvg = result.order_avg;
            this.state.orderCount = result.order_count;
            this.state.discountAvg = result.discount_avg;
            this.state.OrderProdAvg = result.order_prod_avg;
            this.state.orderAvgChange = result.order_avg_change;
            this.state.orderCountChange = result.order_count_change;
            this.state.discountAvgChange = result.discount_avg_change;

            // Set the new inventory totals based on the backend response
            this.state.currentTotalQuantity = result.currentTotalQuantity || 0;
            this.state.currentTotalCost = result.currentTotalCost || 0;
            this.state.previousTotalQuantity = result.previousTotalQuantity || 0;
            this.state.previousTotalCost = result.previousTotalCost || 0;
            this.state.bestSellingProducts = result.best_selling_products || [];
            this.state.dailySalesGraphData = result.daily_sales_graph_data || [];
            this.state.monthlySalesData = result.monthly_sales_data || [];
            this.state.monthlyPaymentsData = result.monthlyPaymentsData || [];
            this.state.categories = result.categories || [];
            this.state.paymentMethods = result.paymentMethods || {};
            this.state.paymentMethodsNames = result.payment_methods_names || {};
            this.state.currencyPayments = result.currency_payments || {};
            this.state.categoryStockData = result.category_stock_data || [];

            // Set today's sales data
            this.state.todaySales = result.today_sales || 0;
            this.state.todaySalesChange = result.today_sales_change || 0;

            // Set today's sales by company data
            this.state.todaySalesData = result.today_sales_data.map((entry, index) => ({
                ...entry,
            }));

            // Set seller ranking data, including discount_avg and discount_change
            this.state.sellerRanking = (result.seller_ranking || []).map(seller => ({
                ...seller,
                discount_avg: seller.discount_avg || 0,
                discount_change: seller.discount_change || undefined,
                avg_products_sold: seller.avg_products_sold || 0, // New field
                avg_order_count: seller.avg_order_count || 0, // New field
                avg_products_per_order: seller.avg_products_per_order || 0, // New field
            }));

            this.state.loading = false;

            console.log("Sales Data Loaded Successfully: ", this.state);
        } catch (error) {
            console.error("Error fetching sales data: ", error);
            this.state.loading = false;
        }
    }

    renderDailySalesGraph() {
        const data = this.state.dailySalesGraphData;

        if (!data || data.length === 0) {
            console.warn("No daily sales data available to render.");
            return;
        }

        // Define fixed colors
        const fixedColors = ["blue", "green", "purple", "lightblue", "grey"];

        // Prepare labels (days of the month)
        const labels = Array.from({ length: new Date().getDate() }, (_, i) => i + 1); // Days from 1 to today

        // Prepare datasets for each company
        const datasets = data.map((companyData, index) => ({
            label: companyData.company,
            data: companyData.data.map(day => day.sales),
            borderColor: fixedColors[index % fixedColors.length], // Assign fixed colors cyclically
            borderWidth: 2,
            fill: false,
        }));

        // Render the graph using Chart.js
        const ctx = document.getElementById("dailySalesGraph").getContext("2d");
        new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: datasets,
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                },
                scales: {
                    x: { title: { display: true, text: 'Day of the Month' } },
                    y: { title: { display: true, text: 'Sales Amount' }, beginAtZero: true },
                },
            },
        });
    }

    renderCategoryBarGraph() {
        const data = this.state.categoryStockData;

        if (!data || data.length === 0) {
            console.warn("No category stock data available to render.");
            return;
        }

        // Sort categories dynamically by quantity
        const sortCategoriesByDataset = (dataset, labels) => {
            const categoryData = labels.map((label, index) => ({
                category_name: label,
                quantity: dataset.data[index],
            }));
            categoryData.sort((a, b) => b.quantity - a.quantity);
            return {
                sortedLabels: categoryData.map(item => item.category_name),
                sortedData: categoryData.map(item => item.quantity),
            };
        };

        // Prepare initial labels (sorted by "Legacy" dataset by default)
        const legacyData = data.find(company => company.company_name === "Legacy");
        const initialLabels = legacyData
            ? legacyData.categories
                  .sort((a, b) => b.total_quantity - a.total_quantity)
                  .map(category => category.category_name)
            : [...new Set(data.flatMap(company => company.categories.map(category => category.category_name)))];

        // Prepare datasets
        const datasets = data.map(company => ({
            label: company.company_name,
            data: initialLabels.map(label => {
                const category = company.categories.find(cat => cat.category_name === label);
                return category ? category.total_quantity : 0;
            }),
            backgroundColor: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.6)`,
            borderColor: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 1)`,
            borderWidth: 1,
            hidden: company.company_name !== "Legacy", // Default to showing only "Legacy"
        }));

        // Select the graph container
        const graphContainer = document.getElementById("categoryBarGraphContainer");
        if (graphContainer) {
            graphContainer.style.width = "2000px"; // Adjust width to occupy full space
            graphContainer.style.height = "500px"; // Increase graph height
        }

        // Render the Chart.js graph
        const ctx = document.getElementById("categoryBarGraph").getContext("2d");

        const chartConfig = {
            type: "bar",
            data: {
                labels: initialLabels,
                datasets: datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        onClick: (e, legendItem) => {
                            const chart = this.categoryBarGraphInstance; // Use the instance of the chart
                            const dataset = chart.data.datasets[legendItem.datasetIndex];

                            // Hide all datasets except the clicked one
                            chart.data.datasets.forEach((ds, index) => {
                                ds.hidden = index !== legendItem.datasetIndex; // Hide all others
                            });

                            // Sort the labels and data for the selected dataset
                            const { sortedLabels, sortedData } = sortCategoriesByDataset(dataset, chart.data.labels);

                            // Update labels and align the dataset data
                            chart.data.labels = sortedLabels;
                            dataset.data = sortedData;

                            chart.update();
                        },
                    },
                },
                scales: {
                    x: {
                        stacked: true,
                        title: { display: true, text: 'Product Categories' },
                        ticks: {
                            callback: function (value) {
                                return this.getLabelForValue(value);
                            },
                        },
                    },
                    y: { stacked: true, title: { display: true, text: 'Total Quantity' } },
                },
            },
        };

        if (this.categoryBarGraphInstance) {
            this.categoryBarGraphInstance.destroy();
        }

        this.categoryBarGraphInstance = new Chart(ctx, chartConfig);
    }

    renderGraph() {
        if (!this.state.linearGraphData || this.state.linearGraphData.length === 0) {
            console.warn("No graph data available to render.");
            return;
        }

        const $canvasElement = $(document).find("#salesPredictionGraph");
        if ($canvasElement.length === 0) {
            console.error("Canvas element with ID 'salesPredictionGraph' not found!");
            return;
        }

        $canvasElement.parent().css({
            width: "100%",
            height: "420px",
        });

        const ctx = $canvasElement[0].getContext("2d");
        if (!ctx) {
            console.error("Failed to get canvas context for rendering the graph.");
            return;
        }

        // Prepare datasets with predicted sales sorted by total sales on the last day of the month
        let datasets = this.state.linearGraphData.map(companyData => {
            const lastDayData = companyData.data[companyData.data.length - 1];
            const totalPredictedSales = lastDayData ? lastDayData.predicted_amount : 0;

            const formattedSales = new Intl.NumberFormat('en-US', {
                style: 'decimal',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(totalPredictedSales);

            const label = `${companyData.company} - $${formattedSales}`;

            return {
                companyName: companyData.company, // Used for sorting
                totalSales: totalPredictedSales, // Used for sorting
                chartData: {
                    label: label,
                    data: companyData.data.map(point => point.predicted_amount),
                    borderColor: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 1)`, // Random colors for each company
                    borderWidth: 2,
                    fill: false,
                }
            };
        });

        // Sort datasets by total predicted sales (descending order)
        datasets = datasets.sort((a, b) => b.totalSales - a.totalSales).map(d => d.chartData);

        const labels = Array.from({ length: 31 }, (_, i) => i + 1); // Days of the month

        new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: datasets,
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                },
                scales: {
                    x: { beginAtZero: true },
                    y: { beginAtZero: true },
                },
            },
        });

        console.log("Graph rendered successfully with sorted labels by predicted sales.");

        // Prepare the data
        const productCategories = this.state.bestSellingProducts.map(
            (product) => `${product.category}` // Already includes product count
        );
        const productPercentages = this.state.bestSellingProducts.map((product) => product.percentage);
        const productTotalSales = this.state.bestSellingProducts.map((product) => product.total_sales);

        // Create the pie chart
        const data = [{
            type: "pie",
            labels: productCategories,
            values: productPercentages, // Use percentages for slice sizes
            textinfo: "label+percent", // Show label and percentage
            textposition: "inside", // Position text inside the slices
            hoverinfo: "none", // Disable hover interactions
            texttemplate: "%{label}<br>%{value}%<br>$%{customdata}", // Include total sales in the text
            customdata: productTotalSales, // Pass total sales as custom data
            automargin: true, // Adjust margins for better fit
            marker: {
                colors: [
                    "rgba(255, 99, 132, 0.6)",
                    "rgba(54, 162, 235, 0.6)",
                    "rgba(255, 206, 86, 0.6)",
                    "rgba(75, 192, 192, 0.6)",
                    "rgba(153, 102, 255, 0.6)",
                    "rgba(255, 159, 64, 0.6)",
                    "rgba(199, 199, 199, 0.6)",
                    "rgba(83, 102, 255, 0.6)",
                    "rgba(255, 209, 64, 0.6)",
                    "rgba(173, 102, 255, 0.6)"
                ]
            },
            textfont: {
                size: 18, // Font size
                color: "black", // Font color
            },
            insidetextorientation: "horizontal", // Ensure horizontal alignment of text
        }];

        // Define the layout
        const layout = {
            title: null, // Remove the title
            paper_bgcolor: "rgba(0,0,0,0)", // Transparent background
            plot_bgcolor: "rgba(0,0,0,0)", // Transparent plot area background
            height: 800,
            width: 800,
            margin: { t: 0, b: 50, l: 50, r: 50 }, // Adjust chart margins
            showlegend: false, // Disable legend
        };

        // Render the chart
        Plotly.newPlot("bestSellingProductsGraph", data, layout);
    }
}

// Register the component under the correct action tag
registry.category("actions").add("sales_dashboard_js_action", SalesDashboard);
