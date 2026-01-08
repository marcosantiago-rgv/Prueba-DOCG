    function update_record(record,column) {
        fetch(`/dynamic/${table_name}/double_table/update/${column}/${record.id}/${record[column]}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.message !== "" && data.status==='warning') {
                window.dispatchEvent(new CustomEvent('show-info', {
                    detail: data.message   // the message from your AJAX or backend
                }));
                warningInfo.style.display = 'flex';  // Show the warning message
                warningInfo.style.opacity = '1';  // Set opacity to 1 for showing
                setTimeout(function() {
                    warningInfo.style.opacity = '0';  // Start fading out
                    // After the fade-out animation is complete, hide the element
                    setTimeout(function() {
                        warningInfo.style.display = 'none';
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