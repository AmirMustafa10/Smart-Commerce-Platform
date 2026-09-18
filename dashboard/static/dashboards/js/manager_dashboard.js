document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       Bootstrap Tooltips
       ========================================================= */

    const tooltipElements =
        document.querySelectorAll(
            '[data-bs-toggle="tooltip"]'
        );

    if (
        tooltipElements.length &&
        typeof bootstrap !== "undefined"
    ) {

        tooltipElements.forEach(function (element) {

            new bootstrap.Tooltip(element);

        });

    }


    /* =========================================================
       Sales Chart
       ========================================================= */

    const canvas =
        document.getElementById("salesChart");

    if (
        !canvas ||
        typeof Chart === "undefined"
    ) {
        return;
    }


    const salesDataElement =
        document.getElementById(
            "manager-sales-data"
        );

    let salesData = [];


    if (salesDataElement) {

        try {

            salesData =
                JSON.parse(
                    salesDataElement.textContent
                );

        } catch (error) {

            console.error(
                "Unable to parse manager sales data:",
                error
            );

            salesData = [];

        }

    }


    /*
     * Supports common backend structures:
     *
     * [
     *     {
     *         "date": "2026-09-12",
     *         "sales": 1200
     *     }
     * ]
     *
     * Also supports:
     * label / revenue / total / amount
     */


    const labels =
        salesData.map(function (item) {

            return (
                item.date ||
                item.label ||
                ""
            );

        });


    const values =
        salesData.map(function (item) {

            return Number(
                item.sales ??
                item.revenue ??
                item.total ??
                item.amount ??
                0
            );

        });


    const context =
        canvas.getContext("2d");


    new Chart(context, {

        type: "line",


        data: {

            labels: labels,


            datasets: [

                {

                    label: "Sales",

                    data: values,

                    fill: true,

                    tension: 0.38,

                    borderWidth: 2,

                    borderColor: "#25d366",

                    backgroundColor:
                        "rgba(37, 211, 102, 0.10)",

                    pointRadius: 4,

                    pointHoverRadius: 7,

                    pointBackgroundColor:
                        "#25d366",

                    pointBorderColor:
                        "#ffffff",

                    pointBorderWidth: 2

                }

            ]

        },


        options: {

            responsive: true,

            maintainAspectRatio: false,


            interaction: {

                intersect: false,

                mode: "index"

            },


            plugins: {

                legend: {

                    display: false

                },


                tooltip: {

                    padding: 11,

                    displayColors: false,


                    callbacks: {

                        label: function (context) {

                            return (
                                "Sales: " +
                                context.parsed.y
                            );

                        }

                    }

                }

            },


            scales: {

                x: {

                    grid: {

                        display: false

                    },


                    ticks: {

                        color: "#8b9891",

                        font: {

                            size: 11

                        }

                    }

                },


                y: {

                    beginAtZero: true,


                    grid: {

                        color:
                            "rgba(22, 53, 42, 0.06)"

                    },


                    ticks: {

                        color: "#8b9891",

                        font: {

                            size: 11

                        }

                    }

                }

            }

        }

    });

});