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
        });

        // Use onWillStart to load data before component is rendered
        onWillStart(async () => {
            await this.loadSalesData();
        });

        // Use onMounted to render the graph once the component is rendered
        onMounted(() => {
            this.renderGraph();
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
            this.state.orderAvgChange = result.order_avg_change;
            this.state.orderCountChange = result.order_count_change;
            this.state.discountAvgChange = result.discount_avg_change;

            // Set the new inventory totals based on the backend response
            this.state.currentTotalQuantity = result.currentTotalQuantity || 0;
            this.state.currentTotalCost = result.currentTotalCost || 0;
            this.state.previousTotalQuantity = result.previousTotalQuantity || 0;
            this.state.previousTotalCost = result.previousTotalCost || 0;
            this.state.bestSellingProducts = result.best_selling_products || [];

            // Set today's sales data
            this.state.todaySales = result.today_sales || 0;
            this.state.todaySalesChange = result.today_sales_change || 0;

            // Set today's sales by company data
            this.state.todaySalesData = result.today_sales_data || [];

            // Set seller ranking data, including discount_avg and discount_change
            this.state.sellerRanking = (result.seller_ranking || []).map(seller => ({
                ...seller,
                discount_avg: seller.discount_avg || 0,   // Add discount average
                discount_change: seller.discount_change || undefined  // Add discount change percentage
            }));

            this.state.loading = false;

            console.log("Sales Data Loaded Successfully: ", this.state);
        } catch (error) {
            console.error("Error fetching sales data: ", error);
            this.state.loading = false;
        }
    }

    renderGraph() {
        // Ensure that graph data is available
        if (!this.state.linearGraphData || this.state.linearGraphData.length === 0) {
            console.warn("No graph data available to render.");
            return;
        }

        // Use jQuery-style selector to access the canvas element
        const $canvasElement = $(document).find("#salesPredictionGraph");
        if ($canvasElement.length === 0) {
            console.error("Canvas element with ID 'salesPredictionGraph' not found!");
            return;
        }

        // Set the desired width and height for the graph container
        $canvasElement.parent().css({
            width: "100%",
            height: "420px",  // Set the desired height here
        });

        const ctx = $canvasElement[0].getContext("2d");
        if (!ctx) {
            console.error("Failed to get canvas context for rendering the graph.");
            return;
        }

        const labels = this.state.linearGraphData.map((g) => g.day);
        const data = this.state.linearGraphData.map((g) => g.predicted_amount);

        // Render the graph using Chart.js
        new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Predicted Sales",
                        data: data,
                        borderColor: "rgba(75, 192, 192, 1)",
                        borderWidth: 2,
                        fill: false,
                    },
                ],
            },
            options: {
                responsive: true,
                scales: {
                    x: { beginAtZero: true },
                    y: { beginAtZero: true },
                },
            },
        });

        console.log("Graph rendered successfully with custom dimensions!");

        // Pie chart for Best Selling Products by Category
        const bestSellingCanvas = $(document).find("#bestSellingProductsGraph");
        if (bestSellingCanvas.length === 0) {
            console.error("Canvas element with ID 'bestSellingProductsGraph' not found!");
            return;
        }

        const bestSellingCtx = bestSellingCanvas[0].getContext("2d");
        if (!bestSellingCtx) {
            console.error("Failed to get canvas context for rendering the pie chart.");
            return;
        }

        const categories = this.state.bestSellingProducts.map((product) => product.category);
        const quantity = this.state.bestSellingProducts.map((product) => product.quantity);

        // Render the pie chart using Chart.js
        new Chart(bestSellingCtx, {
            type: "pie",
            data: {
                labels: categories,
                datasets: [{
                    data: quantity,
                    backgroundColor: [
                        "rgba(255, 99, 132, 0.2)",
                        "rgba(54, 162, 235, 0.2)",
                        "rgba(255, 206, 86, 0.2)",
                        "rgba(75, 192, 192, 0.2)",
                        "rgba(153, 102, 255, 0.2)",
                        "rgba(255, 159, 64, 0.2)",
                        "rgba(199, 199, 199, 0.2)",
                        "rgba(83, 102, 255, 0.2)",
                        "rgba(255, 209, 64, 0.2)",
                        "rgba(173, 102, 255, 0.2)"
                    ],
                    borderColor: [
                        "rgba(255, 99, 132, 1)",
                        "rgba(54, 162, 235, 1)",
                        "rgba(255, 206, 86, 1)",
                        "rgba(75, 192, 192, 1)",
                        "rgba(153, 102, 255, 1)",
                        "rgba(255, 159, 64, 1)",
                        "rgba(199, 199, 199, 1)",
                        "rgba(83, 102, 255, 1)",
                        "rgba(255, 209, 64, 1)",
                        "rgba(173, 102, 255, 1)"
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                }
            }
        });
    }
}

// Register the component under the correct action tag
registry.category("actions").add("sales_dashboard_js_action", SalesDashboard);
