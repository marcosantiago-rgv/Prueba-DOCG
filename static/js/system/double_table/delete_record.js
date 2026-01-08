async function deleteRecord(tableName, modelSecondTable, mainId, recordId, csrfToken) {
    showLoader();
    fetch(`/dynamic/${tableName}/double_table/delete/${modelSecondTable}/${mainId}/${recordId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.message !== "" && data.status==='warning') {
            window.dispatchEvent(new CustomEvent('show-info', {
                detail: data.message   // the message from your AJAX or backend
            }));
            infoAlert.style.display = 'flex';  // Show the warning message
            infoAlert.style.opacity = '1';  // Set opacity to 1 for showing
            setTimeout(function() {
                infoAlert.style.opacity = '0';  // Start fading out
                // After the fade-out animation is complete, hide the element
                setTimeout(function() {
                    infoAlert.style.display = 'none';
                }, 1000);  // Match this delay with the CSS transition time (1s)
            }, 3000);
            reload_tables();
        }else{
            reload_tables();
        }
    })
    .catch(error => console.error("Error:", error));    
}