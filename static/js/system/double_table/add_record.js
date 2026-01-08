async function addRecord(tableName,modelFirstTable, modelSecondTable, mainId, recordId, csrfToken) {
    showLoader();
    const url = `/dynamic/${tableName}/double_table/add/${modelFirstTable}/${modelSecondTable}/${mainId}/${recordId}`;
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({}) // you can send extra data if needed
        });

        if (response.ok) {
            reload_tables();
        } else {
            alert("Error al eliminar el reigstro.");
        }
    } catch (error) {
        window.dispatchEvent(new CustomEvent('show-warning', {
            detail: 'Error al eliminar el registro'  // the message from your AJAX or backend
        }));
        warningAlert.style.display = 'flex';  // Show the warning message
        warningAlert.style.opacity = '1';  // Set opacity to 1 for showing
        setTimeout(function() {
            warningAlert.style.opacity = '0';  // Start fading out
            // After the fade-out animation is complete, hide the element
            setTimeout(function() {
                warningAlert.style.display = 'none';
            }, 1000);  // Match this delay with the CSS transition time (1s)
        }, 3000);
    }
}