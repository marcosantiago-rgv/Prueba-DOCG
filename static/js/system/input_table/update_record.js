    function update_record(record,column) {
        const safeValue = encodeURIComponent(record[column]);
        fetch(`/dynamic/${table_name}/double_table/update/${column}/${record.id}/${safeValue}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.message !== "" && data.status==='warning') {
                window.dispatchEvent(new CustomEvent('show-warning', {
                    detail: data.message   // the message from your AJAX or backend
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
                if (data.value!=''){
                    record[column] = data.value;  
                    const input = document.querySelector(
                        `[data-record-id="${record.id}"][data-column="${column}"]`
                    );
                    if (input) {
                        input.value = data.value;
                    }
                }
            }
        })
        .catch(error => console.error("Error:", error));
    }