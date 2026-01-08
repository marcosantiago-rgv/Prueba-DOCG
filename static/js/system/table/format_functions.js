function money_format(value) {
    return `$${new Intl.NumberFormat().format(value)}`;
}
function commafy(value) {
    if (typeof value !== "number" || isNaN(value)) return value; // Keep non-numeric values unchangeda
    return `${new Intl.NumberFormat().format(value)}`;
}
function round(value) {
    if (typeof value !== "number" || isNaN(value)) return value; // Keep non-numeric values unchangeda
    return `${new Intl.NumberFormat().format(value)}`;
}

