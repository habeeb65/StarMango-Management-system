// Update the autocomplete display to show product quantities
django.jQuery(document).ready(function($) {
    // Listen for lot selection changes
    $('#id_lot').on('select2:select', function(e) {
        const lotId = e.params.data.id;
        // Fetch detailed product info (optional)
        django.jQuery.get(`/admin/Accounts/purchaseinvoice/${lotId}/change/`, function(data) {
            // Parse and display product quantities here
            console.log("Lot selected:", data);
            console.log("Custom JS loaded!");
        });
    });
});
