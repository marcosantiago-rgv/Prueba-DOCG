let getRecordRunCount = 0;

document.addEventListener('alpine:init', () => {
    Alpine.store('modalData', {
        record: null,

        getField(key) {
            // Si hay objeto plano (flat), preferirlo
            if (this.record && typeof this.record === 'object') {
                return this.record[key] ?? null;
            }
            return null;
        }
    });
});
function redirectActions(url) {
    if (url.includes("delete")) {
        // Para eliminación se confirma y se envía por POST
        if (confirm('¿Quieres eliminar el registro seleccionado?')) {
            const form = document.getElementById('action_buttons');
            form.action = url;
            form.method = "POST";
            form.submit();
        }
    } else if (url.includes("download_pdf")) {
        // Para descargar PDF se utiliza fetch y se procesa la descarga
        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                } else {
                    throw new Error("No se pudo descargar el archivo.");
                }
            })
            .then(blob => {
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = downloadUrl;
                a.download = `${url.split("=")[2]}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.location.reload();
            })
            .catch(error => {
                alert("Error al descargar el archivo: " + error.message);
            });
    } else {
        window.location.href = url;
    }
}

async function openActions(form, recordId, estatus) {
    showLoader();
    //document.getElementById('id_registro').textContent=recordId;

    // Normaliza estatus para evitar errores en tablas que no lo tienen (ej. existencias)
    const estatusTexto = (estatus ?? '').toString();
    const estatusLower = estatusTexto.toLowerCase();

    const estatusElement = document.getElementById('estatus');
    if (estatusElement) {
        estatusElement.textContent = estatusTexto;
    }

    const updateButton = document.querySelector('button[data-action="actualizar"]');
    const deleteButton = document.querySelector('button[data-action="delete"]');
    const downloadButton = document.querySelector('button[data-action="descargar"]');
    const filesButton = document.querySelector('button[data-action="files"]');

    const tablasProtegidas = ['cuenta_banco', 'categoria_gasto'];

    if (deleteButton) {
        const esTablaProtegida = tablasProtegidas.includes(form.toLowerCase());
        const tieneEstatusRestringido = ['pagado', 'activo', 'finalizada'].includes(estatusLower);

        if (esTablaProtegida || tieneEstatusRestringido) {
            deleteButton.classList.add('hidden');
            deleteButton.removeAttribute('onclick');
        } else {
            deleteButton.classList.remove('hidden');
            deleteButton.setAttribute('onclick', `redirectActions('/dynamic/${form}/delete?id=${recordId}')`);
        }
    }

    if (updateButton) {
        updateButton.setAttribute('onclick', `redirectActions('/dynamic/${form}/form?id=${recordId}')`);
    }

    if (deleteButton) {
        deleteButton.setAttribute('onclick', `redirectActions('/dynamic/${form}/delete?id=${recordId}')`);
    }

    if (downloadButton) {
        downloadButton.setAttribute('onclick', `redirectActions('/files/download_pdf?table=${form}&id=${recordId}')`);
    }
    if (filesButton) {
        filesButton.setAttribute('onclick', `redirectActions('/dynamic/${form}/files/${recordId}')`);
    }

    const data = await get_record(form, recordId);
    const popupActions = document.getElementById('modal');
    // Guardamos en el store la versión "plana" que regresa get_record
    // para que los templates personalizados (como transferencia_inventario)
    // puedan seguir usando propiedades como .id o .estatus.
    Alpine.store('modalData').record = data || null;
    popupActions.classList.remove('hidden');
    hideLoader();

}
function closeActions() {
    const popupActions = document.getElementById('modal');
    const container = document.getElementById('modal_content');
    container.innerHTML = '';
    popupActions.classList.add('hidden');
    getRecordRunCount = 0;
}

async function get_record(form, recordId) {
    try {
        getRecordRunCount++;
        // const path = `/dynamic/${form}/data/${recordId}`;
        // const response = await fetch(path);
        // if (!response.ok) {
        //     throw new Error(`Network response was not ok: ${response.statusText}`);
        // }
        // const data = await response.json();
        // const record = data[0]; // primer registro
        // const recordObj = Object.fromEntries(record);

        // const modal_content = document.getElementById('modal_content');
        // modal_content.innerHTML = '<tbody></tbody>';
        // const tbody_modal_content = modal_content.querySelector("tbody");

        // try {
        //     modal_content_relationship = document.getElementById('modal_content_relationship');
        //     modal_content_relationship.innerHTML = '<tbody></tbody>';
        //     tbody_modal_content_relationship = modal_content_relationship.querySelector("tbody");
        // } catch (error) {
        //     // Error silencioso si no existe el contenedor de relaciones
        // }

        // document.getElementById("modal_title").textContent = `${titleFormat(form)}`;
        // const buttons = document.getElementById("buttons_modal_exits");


        const path = `/dynamic/${form}/data/${recordId}`;
        const response = await fetch(path);

        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }

        const data = await response.json();
        const sections = data[0]; // array de secciones [{section, fields:[{key,value}]}]

        const modal_content = document.getElementById('modal_content');
        modal_content.innerHTML = '';

        let tbody_modal_content_relationship = null;
        try {
            const modal_content_relationship = document.getElementById('modal_content_relationship');
            modal_content_relationship.innerHTML = '<tbody></tbody>';
            tbody_modal_content_relationship = modal_content_relationship.querySelector("tbody");
        } catch (error) { }

        document.getElementById("modal_title").textContent = `${titleFormat(form)}`;

        const buttons = document.getElementById("buttons_modal_exits");
        if (getRecordRunCount === 1) {
            buttons.classList.remove("hidden");
        } else {
            buttons.classList.add("hidden");
        }

        //     for (const [key, rawValue] of Object.entries(recordObj)) {
        //         let value = rawValue;

        //         const excludeKeywords = ['telefono', 'cuenta', 'clabe'];
        //         const isExcluded = excludeKeywords.some(word => key.toLowerCase().includes(word));

        //         if (value !== null && value !== "" && !isExcluded) {
        //             // Si la columna está marcada como moneda en el sistema
        //             if (typeof money_format_columns !== 'undefined' && money_format_columns.includes(key) && !isNaN(value)) {
        //                 value = formatCurrency(value);
        //             } 
        //             // Si es un número pero NO es un teléfono 
        //             else if (!isNaN(value) && String(value).length < 10) {
        //                 value = formatNumber(value);
        //             }
        //         }

        //         const tr = document.createElement('tr');

        //         if(String(value).includes('/dynamic')){
        //             tr.innerHTML = `<td style="border-right: 1px solid #ccc; padding: 8px;">${titleFormat(key)}</td>
        //             <td style="text-align: center;">
        //                 <button type="submit"
        //                     @click.stop="window.location.href='${value}'"
        //                     class="btn border text-primary border-transparent rounded-md transition-all duration-300 hover:text-white hover:bg-primary bg-primary/10">
        //                     Ver
        //                 </button>
        //             </td>`;
        //             tbody_modal_content_relationship.appendChild(tr);
        //         } 
        //         // Lista de IDs técnicos que no queremos mostrar en la modal
        //         else if (!['id', 'id_proveedor', 'id_categoria_de_gasto', 'id_cuenta_de_banco'].includes(key)) {

        //             if(key.includes('archivo') && value && String(value).includes('__')){
        //                 const [uuid, name] = value.split("__");
        //                 tr.innerHTML = `
        //                     <td style="white-space:normal;border-right:1px solid #ccc; padding:8px;">
        //                         ${titleFormat(key)}
        //                     </td>
        //                     <td class="clickable-td"
        //                         style="word-break:break-word; white-space:normal; overflow-wrap:anywhere; max-width:300px;">
        //                         <a href="#"
        //                         style="display:block; width:100%; height:100%; text-decoration:none; color:inherit;"
        //                         onclick="downloadFile('${uuid}','view')">
        //                             ${name}
        //                         </a>
        //                     </td>
        //                 `;
        //             }                    
        //             else if(value && String(value).includes('__')){
        //                 const [before, id, table_name] = value.split("__");
        //                 tr.innerHTML = `
        //                     <td style="white-space:normal;border-right:1px solid #ccc; padding:8px;">
        //                         ${titleFormat(key)}
        //                     </td>
        //                     <td class="clickable-td"
        //                         style="word-break:break-word; white-space:normal; overflow-wrap:anywhere; max-width:300px;">
        //                         <a href="#"
        //                         style="display:block; width:100%; height:100%; text-decoration:none; color:inherit;"
        //                         onclick="openActions('${table_name}', '${id}', '')">
        //                             ${before}
        //                         </a>
        //                     </td>
        //                 `;
        //             } else {
        //                 tr.innerHTML = `
        //                     <td style="border-right: 1px solid #ccc; padding: 8px;">${titleFormat(key)}</td>
        //                     <td style="word-break: break-word; white-space: normal; overflow-wrap: anywhere; max-width: 300px;">${value}</td>
        //                 `;
        //             }
        //             tbody_modal_content.appendChild(tr);                    
        //         }
        //     }
        //     return recordObj;
        // } catch (error) {
        //     console.error("Error fetching or processing data:", error);
        //     return null; 

        // ===============================
        // SECTION LOOP (ORDER PRESERVED)
        // ===============================
        sections.forEach(sectionObj => {
            const sectionName = sectionObj.section;
            const fields = sectionObj.fields;

            // ---- Section title ----
            const sectionTitle = document.createElement('h3');
            sectionTitle.textContent = titleFormat(sectionName);
            sectionTitle.style.marginTop = '20px';
            sectionTitle.style.marginBottom = '10px';
            sectionTitle.style.fontWeight = '600';
            modal_content.appendChild(sectionTitle);

            // ---- Table ----
            const table = document.createElement('table');
            table.className = 'w-full border-collapse';

            const tbody = document.createElement('tbody');
            // ===============================
            // FIELD LOOP (ORIGINAL LOGIC)
            // ===============================
            fields.forEach(({ key, value: rawValue }) => {
                let value = rawValue;
                if (money_format_columns.includes(key) && !isNaN(value)) {
                    value = formatCurrency(value);
                } else if (!isNaN(value) && !key.includes('telefono') && !key.includes('celular') && !key.includes('periodo')) {
                    value = formatNumber(value);
                }

                const tr = document.createElement('tr');
                // ---- Relationships ----
                if (sectionName === 'registros_relacionados') {
                    tr.innerHTML = `
                        <td style="white-space:normal;border-bottom:1px solid ; padding:8px;" class="bg-gray/10">
                            ${titleFormat(key)}
                        </td>
                        <td style="white-space:normal;border-bottom:1px solid ; padding:8px;text-align:center;">
                            <button type="submit"
                                
                                class="btn border text-primary border-transparent rounded-md transition-all duration-300 hover:text-white hover:bg-primary bg-primary/10"
                                onclick="window.location.href='${value}'">
                                Ver
                            </button>
                        </td>
                    `;
                } else if (!['id'].includes(key)) {
                    // ---- File ----
                    if (key.includes('archivo')) {
                        const [uuid, name] = value.split("__");
                        tr.innerHTML = `
                            <td style="white-space:normal;border-right:1px solid padding:8px;" class="bg-gray/10">
                                ${titleFormat(key)}
                            </td>
                            <td class="clickable-td"
                                style="white-space:normal;border-bottom:1px solid ; padding:8px;">
                                <a href="#"
                                   style="display:block; width:100%; height:100%; text-decoration:none; color:inherit;"
                                   onclick="downloadFile('${uuid}','view')">
                                    ${name}
                                </a>
                            </td>
                        `;
                    }

                    // ---- FK link ----
                    else if (typeof value === 'string' && value.includes('__')) {
                        const [before, id, table_name] = value.split("__");
                        tr.innerHTML = `
                            <td style="white-space:normal;border-bottom:1px solid ; padding:8px;" class="bg-gray/10">
                                ${titleFormat(key)}
                            </td>
                            <td class="clickable-td"
                                style="white-space:normal;border-bottom:1px solid ; padding:8px;">
                                <a href="#"
                                   style="display:block; width:100%; height:100%; text-decoration:none; color:inherit;"
                                   onclick="openActions('${table_name}', '${id}', '')">
                                    ${before}
                                </a>
                            </td>
                        `;
                    }

                    // ---- Normal value ----
                    else {
                        tr.innerHTML = `
                            <td style="white-space:normal;border-bottom:1px solid ; padding:8px;" class="bg-gray/10">
                                ${titleFormat(key)}
                            </td>
                            <td style="white-space:normal;border-bottom:1px solid ; padding:8px;">
                                ${value}
                            </td>
                        `;
                    }
                }
                tbody.appendChild(tr);
            });

            table.appendChild(tbody);
            modal_content.appendChild(table);
        });

        // Construimos un objeto plano { clave: valor }
        // a partir de todas las secciones y campos,
        // útil para los botones personalizados del modal.
        const flatRecord = {};
        sections.forEach(sectionObj => {
            sectionObj.fields.forEach(({ key, value }) => {
                flatRecord[key] = value;
            });
        });

        return flatRecord;

    } catch (error) {
        console.error("Error fetching or processing data:", error);
        return null;
    }
}


document.addEventListener('keydown', function (event) {
    // If ESC key is pressed
    if (event.key === "Escape") {
        closeActions();
    }
});