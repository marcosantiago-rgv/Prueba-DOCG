
// Chart Widget 5
var userchart = {
    chart: {
        height: 300,
        type: "area",
        fontFamily: "Inter, sans-serif",
        zoom: {
            enabled: false,
        },
        toolbar: {
            show: false,
        },
    },
    series: [
        {
            name: "Income",
            data: [8000, 1000, 7600, 2000, 15000, 7000, 15000],
        },
        {
            name: "Expenses",
            data: [7000, 1300, 9000, 1000, 12000, 6000, 14000],
        },
    ],
    dataLabels: {
        enabled: false,
    },
    stroke: {
        show: true,
        curve: "smooth",
        width: 3,
        lineCap: "square",
    },
    dropShadow: {
        enabled: false,
    },
    colors: ["#267DFF", "#00D085"],
    markers: {
        discrete: [
            {
                seriesIndex: 0,
                dataPointIndex: 4,
                fillColor: "#267DFF",
                strokeColor: "#fff",
                size: 6,
            },
            {
                seriesIndex: 1,
                dataPointIndex: 5,
                fillColor: "#00D085",
                strokeColor: "#fff",
                size: 6,
            },
        ],
    },
    labels: [
        "Jan 10",
        "Jan 11",
        "Jan 12",
        "Jan 13",
        "Jan 14",
        "Jan 15",
        "Jan 16",
    ],
    xaxis: {
        axisBorder: {
            show: false,
        },
        axisTicks: {
            show: false,
        },
        crosshairs: {
            show: true,
        },
        labels: {
            offsetX: 0,
            offsetY: 5,
            style: {
                fontSize: "16px",
                fontWeight: "600",
                colors: "#7780A1",
                cssClass: "apexcharts-xaxis-title",
            },
        },
    },
    yaxis: {
        tickAmount: 7,
        labels: {
            formatter: (value) => {
                return value / 1000 + "k";
            },
            offsetX: -10,
            offsetY: 0,
            style: {
                fontSize: "16px",
                fontWeight: "600",
                colors: "#7780A1",
                cssClass: "apexcharts-yaxis-title",
            },
        },
        opposite: false,
    },
    grid: {
        borderColor: "#e0e6ed",
        strokeDashArray: 7,
        xaxis: {
            lines: {
                show: true,
            },
        },
        yaxis: {
            lines: {
                show: false,
            },
        },
        padding: {
            top: 0,
            right: 0,
            bottom: 0,
            left: 25,
        },
    },
    legend: {
        position: "top",
        horizontalAlign: "center",
    },
    tooltip: {
        marker: {
            show: true,
        },
        x: {
            show: false,
        },
    },
    fill: {
        type: "gradient",
        gradient: {
            shadeIntensity: 1,
            inverseColors: !1,
            opacityFrom: 0,
            opacityTo: 0,
            stops: [100, 100],
        },
    },
};
var chart = new ApexCharts(document.querySelector("#capital"), userchart);
chart.render();
var userchart = {
    chart: {
        height: 300,
        type: "bar",
        fontFamily: "Inter, sans-serif",
        zoom: {
            enabled: false,
        },
        toolbar: {
            show: false,
        },
    },
    plotOptions: {
        bar: {
            horizontal: !1,
            endingShape: "rounded",
            columnWidth: "50%",
            borderRadius: 5,
        },
    },
    stroke: {
        show: !0,
        width: 4,
        colors: ["transparent"],
    },
    colors: ["rgba(123, 106, 254, .4)", "#7B6AFE"],
    series: [
        {
            name: "Income",
            data: [8000, 5000, 7600, 2200, 15000, 7000, 15000],
        },
        {
            name: "Expenses",
            data: [7000, 4500, 9000, 1600, 12000, 6000, 14000],
        },
    ],
    dataLabels: {
        enabled: false,
    },
    legend: {
        show: false,
    },
    labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    xaxis: {
        axisBorder: {
            show: false,
        },
        axisTicks: {
            show: false,
        },
        crosshairs: {
            show: true,
        },
        labels: {
            offsetX: 0,
            offsetY: 5,
            style: {
                fontSize: "16px",
                fontWeight: "600",
                colors: "#7780A1",
                cssClass: "apexcharts-xaxis-title",
            },
        },
    },
    yaxis: {
        show: false,
    },
    fill: { opacity: 1 },
    grid: {
        borderColor: "#e0e6ed",
        strokeDashArray: 7,
        xaxis: {
            lines: {
                show: false,
            },
        },
        yaxis: {
            lines: {
                show: false,
            },
        },
        padding: {
            top: 0,
            right: 0,
            bottom: 0,
            left: 0,
        },
    },
    tooltip: {
        y: {
            formatter: function (e) {
                return "" + e;
            },
        },
    },
};
var chart = new ApexCharts(
    document.querySelector("#projectvsaction"),
    userchart
);
chart.render();