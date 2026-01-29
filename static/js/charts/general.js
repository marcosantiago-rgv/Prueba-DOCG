// Global chart registry
window.dashboardCharts = [];

/**
 * Registers a chart in the global registry
 * @param {ApexCharts} chart - The ApexCharts instance
 */
function registerChart(chart) {
    if (chart && chart instanceof ApexCharts) {
        window.dashboardCharts.push(chart);
    }
}
async function destroyAllApexCharts() {
    const charts = window.dashboardCharts || [];

    for (const chart of charts) {
        try {
            await chart.destroy();
        } catch (err) {
            console.warn("Error destroying chart:", err);
        }
    }

    // Clear registry
    window.dashboardCharts = [];

    // Ensure no old canvases remain
    document.querySelectorAll(".apexcharts-canvas, .apexcharts-svg").forEach(el => {
        const container = el.closest("div[id^='grafica_']");
        if (container) container.innerHTML = "";
        else el.remove();
    });
}

// funcion para hacer graficas con mas de una categoria
function generar_grafica_categorias(nombre_grafica, tipo_grafica, x_key, y_key, z_key, path, options) {
    fetch(path)
        .then(response => {
            if (!response.ok) throw new Error(`Network response was not ok: ${response.statusText}`);
            return response.json();
        })
        .then(data => {
            if (!Array.isArray(data)) throw new Error("Fetched data is not an array.");
            const xValues = [...new Set(data.map(item => item[x_key]))];
            const zValues = [...new Set(data.map(item => item[z_key]))];
            const series = zValues.map(z => {
                return {
                    name: (typeof z === 'number' || (!isNaN(z) && z.trim && z.trim() !== ''))
                        ? String(z)
                        : capitalizeWords(z),
                    data: xValues.map(x => {
                        const match = data.find(d => d[x_key] === x && d[z_key] === z);
                        return match ? Number(match[y_key]) || 0 : 0;
                    })
                };
            });
            renderizar_grafica(nombre_grafica, tipo_grafica, series, xValues, options);
        })
        .catch(error => {
            console.error("Error fetching or processing data:", error);
        });
}



// funcion para hacer grafica de Transferencias de inventario por día
// Mismo estilo visual que "Tendencias de Gastos Diarios"


// Nueva función: gráfica de barras por almacén origen
function cargar_transferencias_inventario_productos() {
    const container = document.querySelector('#grafica_transferencias_producto');
    if (container) {
        container.innerHTML = '<div class="flex justify-center items-center h-64"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div></div>';
    }

    // Usar la consulta agregada por almacén origen
    const path = '/dashboard_queries/transferencias_por_almacen_origen';
    fetch(path)
        .then(response => {
            if (!response.ok) throw new Error(`Network response was not ok: ${response.statusText}`);
            return response.json();
        })
        .then(data => {
            const rows = Array.isArray(data) ? data : (data.items || []);
            if (!rows.length) {
                if (typeof mostrarSinDatos === 'function') mostrarSinDatos('#grafica_transferencias_producto');
                return;
            }
            // Evitar duplicados y leyenda/colores de categorías
            const almacenes = rows.map(row => row.almacen_origen);
            const totales = rows.map(row => Number(row.total_transferido) || 0);
            // Limpiar el contenedor antes de renderizar la gráfica para quitar el loading
            if (container) container.innerHTML = '';
            renderizar_grafica(
                '#grafica_transferencias_producto',
                'bar',
                [{ name: '', data: totales }],
                almacenes,
                {
                    colors: ['#267DFF'],
                    legend: { show: false },
                    plotOptions: { bar: { distributed: false } },
                    yaxis: {
                        title: { text: 'Total transferido', style: { color: '#7780A1', fontSize: '12px', fontWeight: 400 } }
                    },
                    xaxis: {
                        categories: almacenes,
                        labels: { rotate: -45 }
                    },
                    tooltip: {
                        y: {
                            formatter: val => `${val.toLocaleString('es-MX')} unidades`
                        }
                    }
                }
            );
        })
        .catch(error => {
            console.error('Error cargando transferencias de inventario:', error);
            if (typeof mostrarError === 'function') mostrarError('#grafica_transferencias_producto');
        });
}


// funcion para hacer grafica de resumen de inventario (productos, almacenes, transferencias)
// Espera que el endpoint devuelva una sola fila con
// total_productos, total_almacenes, total_transferencias
function cargar_total_inventario() {
    const path = '/dashboard_queries/total_inventario';
    const selector = '#grafica_total_inventario';
    fetch(path)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            const rows = Array.isArray(data) ? data : (data.items || []);
            if (!rows.length) {
                console.warn('No hay datos para el resumen de inventario.');
                return;
            }

            const row = rows[0];
            const labels = [
                'Productos activos',
                'Almacenes activos',
                'Transferencias mes actual',
            ];
            const values = [
                Number(row.total_productos) || 0,
                Number(row.total_almacenes) || 0,
                Number(row.total_transferencias) || 0,
            ];

            // Misma idea visual que "Distribución de Gastos":
            // gráfica de barras sencilla, color azul, sin eje Y visible.
            const options = {
                chart: {
                    height: 300,
                    type: "bar",
                    fontFamily: "Inter, sans-serif",
                    zoom: { enabled: false },
                    toolbar: { show: false }
                },
                plotOptions: {
                    bar: {
                        horizontal: false,
                        endingShape: "rounded",
                        columnWidth: "50%",
                        borderRadius: 5,
                    },
                },
                stroke: {
                    show: true,
                    width: 4,
                    colors: ["transparent"],
                },
                colors: ["#267DFF"],
                dataLabels: {
                    enabled: false,
                },
                legend: {
                    show: false,
                },
                yaxis: {
                    show: false,
                },
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
                        formatter: function (val) {
                            return `${val.toLocaleString()} registros`;
                        }
                    }
                }
            };

            renderizar_grafica(
                selector,
                'bar',
                [{ name: 'Inventario', data: values }],
                labels,
                options
            );
        })
        .catch(error => {
            console.error('Error cargando resumen de inventario:', error);
        });
}













function generar_grafica(nombre_grafica, tipo_grafica, dataXKey, dataYKey, path, options) {
    fetch(path)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // Check if data is an array
            if (!Array.isArray(data)) {
                throw new Error("Fetched data is not an array.");
            }
            const y = data.map(item => Number(item[dataYKey]));
            const x = data.map(item => item[dataXKey]);
            if (tipo_grafica === 'pie') {
                renderizar_pie(nombre_grafica, y, x);
            } else if (tipo_grafica === 'avance') {
                y.push(1 - y[0]);  // Converts the result to a string before pushing
                renderizar_avance(nombre_grafica, "bar", y, x, { valueType: valor_tipo });
            } else {
                renderizar_grafica(nombre_grafica, tipo_grafica, y, x, options);
            }
        })
        .catch(error => {
            console.error("Error fetching or processing data:", error);
        });
}

// funcion para generar grafica generala
function renderizar_grafica(selector, chartType, data_y, data_x, options = {}) {
    if (!selector || !document.querySelector(selector)) {
        console.error("Invalid selector or element not found:", selector);
        return;
    }

    const valueType = options.valueType || "normal"; // "percent", "currency", or "normal"

    // Define custom formatter based on valueType
    const yAxisFormatter = value => {
        switch (valueType) {
            case "percent":
                return `${(value * 100).toFixed(1)}%`; // assumes value is in 0–1 range
            case "currency":
                return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            case "normal":
            default:
                return value.toLocaleString();
        }
    };
    const computeTotals = (series) => {
        if (!Array.isArray(series) || !series.length) return [];
        const len = series[0].data.length;
        const totals = new Array(len).fill(0);
        series.forEach(s => {
            s.data.forEach((val, i) => {
                totals[i] += Number(val) || 0; // force numeric addition
            });
        });
        return totals;
    };
    let isStacked;
    if (chartType === 'bar_stacked') {
        isStacked = true;
        chartType = 'bar'
    } else {
        isStacked = false;
    }
    const series = Array.isArray(data_y) && data_y.length && typeof data_y[0] === "object" && "data" in data_y[0]
        ? data_y
        : [{ name: options.seriesName || "", data: data_y }];
    const totals = isStacked ? computeTotals(series) : [];

    const defaultOptions = {
        series:
            Array.isArray(data_y) && data_y.length && typeof data_y[0] === "object" && "data" in data_y[0]
                ? data_y
                : [{ name: options.seriesName || "", data: data_y }],
        chart: {
            height: options.height || 300,
            type: chartType || "bar",
            stacked: isStacked, // 🔑 make stacked when multiple series
            events: options.events || {},
            toolbar: { show: false },
            fontFamily: "Inter, sans-serif",
            zoom: { enabled: false },
            events: {
                mounted: function (chartContext, config) {
                    const el = chartContext.el;
                    // Let wheel/touch scroll events bubble up to the page
                    el.addEventListener('wheel', (e) => e.stopPropagation(), { capture: true });
                }
            },
        },
        stroke: {
            width: 2,
            curve: 'smooth',
        },
        colors: options.colors || [
            "#267DFF", "#FF51A4", "#FF7C51", "#00D085", "#FFC41F", "#FF3232",
        ],
        plotOptions: {
            bar: {
                columnWidth: "20%",
                borderRadius: 5,
                distributed: !isStacked,
                dataLabels: {
                    total: {
                        enabled: isStacked, // ✅ only show total if stacked
                        offsetY: -10,
                        style: {
                            fontSize: "13px",
                            fontWeight: "700",
                            colors: ["#111"]
                        },
                        formatter: (val) => yAxisFormatter(val),
                    },
                },
                ...options.plotOptions?.bar,
            },
        },
        dataLabels: {
            enabled: (isStacked && chartType === 'bar') ? true : false,
            formatter: (val, { seriesIndex, dataPointIndex }) => {
                if (isStacked) {
                    const total = totals[dataPointIndex] || 0;
                    if (!total) return "0%";
                    const pct = (val / total) * 100;
                    return `${pct.toFixed(1)}%`;
                }
            },
            style: {
                fontSize: "11px",
                fontWeight: "600",
                colors: ["#fff"],
            },
            ...options.dataLabels,
        },
        legend: {
            show: true,
            ...options.legend,
        },
        yaxis: {
            axisBorder: { show: false },
            axisTicks: { show: false },
            tickAmount: 5,
            labels: {
                formatter: yAxisFormatter,
                offsetX: -10,
                offsetY: 0,
                style: {
                    fontSize: "12px",
                    fontWeight: "600",
                    colors: "#7780A1",
                    cssClass: "apexcharts-xaxis-title",
                },
            },
            opposite: false,
            ...options.yaxis,
        },
        xaxis: {
            tickAmount: 7,
            axisBorder: { show: false },
            axisTicks: { show: false },
            categories: data_x,
            labels: {
                style: {
                    fontSize: "12px",
                    fontWeight: "600",
                    colors: "#7780A1",
                    cssClass: "apexcharts-xaxis-title",
                },
            },
            ...options.xaxis,
        },
        grid: {
            borderColor: "#e0e6ed",
            strokeDashArray: 2,
            xaxis: { lines: { show: false } },
            yaxis: { lines: { show: true } },
            padding: {
                top: 0,
                right: 0,
                bottom: 0,
                left: 25,
            },
            ...options.grid,
        },
    };

    const mergedOptions = { ...defaultOptions, ...options };

    const chartKey = selector.replace(/[^a-zA-Z0-9]/g, "");
    if (window[chartKey] && typeof window[chartKey].destroy === 'function') {
        window[chartKey].destroy();
    }
    window[chartKey] = new ApexCharts(document.querySelector(selector), mergedOptions);
    window[chartKey].render();
    registerChart(window[chartKey]);
}
function renderizar_pie(selector, data_y, data_x, options = {}) {
    if (!selector || !document.querySelector(selector)) {
        console.error("Invalid selector or element not found:", selector);
        return;
    }

    // Ensure data_y is numeric
    const numericData_y = data_y.map(value => {
        const parsedValue = parseInt(value, 10);
        return isNaN(parsedValue) ? 0 : parsedValue;
    });

    const simpleOptions = {
        series: numericData_y,
        chart: {
            height: options.height || 300,
            type: "pie",
            width: "100%",  // 👈 make chart responsive
            toolbar: { show: false },
            zoom: { enabled: false },
            events: {
                mounted: function (chartContext, config) {
                    const el = chartContext.el;
                    // Let wheel/touch scroll events bubble up to the page
                    el.addEventListener('wheel', (e) => e.stopPropagation(), { capture: true });
                }
            },
        },
        labels: data_x,
        colors: options.colors || [
            "#267DFF", "#FF51A4", "#FF7C51", "#00D085", "#FFC41F", "#FF3232",
        ],
        dataLabels: {
            enabled: true,
            formatter: (val) => `${val.toFixed(1)}%`,
        },
        tooltip: {
            enabled: true,
            y: {
                formatter: (val) => `$${val.toLocaleString()}`,
            },
            theme: "dark",
        },
        legend: {
            show: true,
        },
    };

    const mergedOptions = { ...simpleOptions, ...options };
    const chartKey = selector.replace(/[^a-zA-Z0-9]/g, "");

    try {
        if (window[chartKey]) {
            window[chartKey].destroy();
        }

        window[chartKey] = new ApexCharts(document.querySelector(selector), mergedOptions);

        window[chartKey].render().then(() => {
            window.dispatchEvent(new Event("resize"));
        });
        registerChart(window[chartKey]);
    } catch (e) {
        console.error("Error rendering chart:", e);
    }
}
