// Initialize form handlers with desktopId from data attribute

function initDesktopUserHandlers(desktopId) {
    // Shared error handler
    const showError = (message) => {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: message,
        });
    };

    // Form submission handler
    const handleFormSubmit = (formElement, endpoint, toastId) => {
        const form = $(formElement);
        let isSubmitting = false;

        form.on('submit', function(e) {
            e.preventDefault();
            
            if (isSubmitting) return;
            isSubmitting = true;
            
            const submitBtn = form.find('button[type="submit"]');
            const originalText = submitBtn.html();
            
            // Show loading state
            submitBtn.prop('disabled', true).html(
                '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...'
            );

            $.ajax({
                type: "POST",
                url: `/${endpoint}/${desktopId}/`,
                data: form.serialize(),
                success: (response) => {
                    if (response.success) {
                        // Hide modal
                        $(`#${form.closest('.modal').attr('id')}`).modal('hide');
                        
                        // Show toast
                        new bootstrap.Toast(document.getElementById(toastId)).show();
                        
                        // Reload page
                        setTimeout(() => {
                            window.location.href = `/desktop_details_view/${desktopId}/#pills-user`;
                        }, 800);
                    } else {
                        showError(response.error || "Update failed");
                    }
                },
                error: (xhr) => {
                    showError(xhr.responseJSON?.error || "Request failed");
                },
                complete: () => {
                    isSubmitting = false;
                    submitBtn.prop('disabled', false).html(originalText);
                }
            });
        });
    };

    // Initialize both forms
    handleFormSubmit('#editEndUserForm', 'update_end_user', 'updateSuccessToast_End_User');
    handleFormSubmit('#editAssetOwnerForm', 'update_asset_owner', 'updateSuccessToast_Asset_Owner');

    // Reset forms on modal close
    $('.modal').on('hidden.bs.modal', function() {
        $(this).find('form').trigger('reset');
    });
}

// Auto-initialize when loaded with data attribute
$(document).ready(function() {
    const scriptTag = document.currentScript;
    const desktopId = scriptTag.getAttribute('data-desktop-id');
    if (desktopId) {
        initDesktopUserHandlers(desktopId);
    }
});