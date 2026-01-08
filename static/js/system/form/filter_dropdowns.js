Object.entries(filters).forEach(([childColumn, parentColumn]) => {
	const $parent = $(`#${parentColumn}`);
	const $child = $(`#${childColumn}`);
	if ($parent.length === 0 || $child.length === 0) return;
	// Save all original options (excluding the default one)
	const allOptions = $child.find("option").not('[value=""]').clone();
	function filterChildOptions() {
		const selectedValue = $parent.val();
		// Clear everything
		$child.empty();
		// Always add default option
		$child.append('<option value="">Selecciona una opción</option>');
		// Append only matching options
		allOptions
		.filter((_, opt) => $(opt).data("filter") == selectedValue)
		.each((_, opt) => $child.append($(opt).clone()));
		// Refresh Select2
		$child.trigger("change");
	}
	// Init Select2 (if not already)
	if (!$child.data("select2")) {
		$child.select2({
		placeholder: "Selecciona una opción",
		allowClear: true
		});
	}
	// Attach listener
	$parent.on("change", filterChildOptions);
	// Run once at page load
	filterChildOptions();
});