$(document).ready(function() {
    let isSubmitting = false;

    // Handle End User Form
    $("#editEndUserForm").submit(function(event) {
        event.preventDefault();
        if (isSubmitting) return false;
        isSubmitting = true;

        let desktopId = $(this).data("desktop-id");
        let formData = $(this).serialize();

        let submitBtn = $(this).find('button[type="submit"]');
        submitBtn.prop('disabled', true).html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...'
        );

        $.ajax({
            type: "POST",
            url: "/updateeee_end_user/" + desktopId + "/",
            data: formData,
            success: function(response) {
                if (response.success) {
                    var modal = bootstrap.Modal.getInstance(document.getElementById('editEndUserModal'));
                    modal.hide();
                    var toast = new bootstrap.Toast(document.getElementById('updateSuccessToast_End_User'));
                    toast.show();
                    setTimeout(function() {
                        window.location.href = window.location.href.split('#')[0] + '#pills-user';
                        window.location.reload();
                    }, 1000);
                } else {
                    showError(response.error || "Failed to update End User");
                }
            },
            error: function(xhr) {
                showError(xhr.responseJSON?.error || "Something went wrong");
            },
            complete: function() {
                isSubmitting = false;
            }
        });
    });

    // Handle Asset Owner Form
    $("#editAssetOwnerForm").submit(function(event) {
        event.preventDefault();
        if (isSubmitting) return false;
        isSubmitting = true;

        let desktopId = $(this).data("desktop-id");
        let formData = $(this).serialize();

        let submitBtn = $(this).find('button[type="submit"]');
        submitBtn.prop('disabled', true).html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...'
        );

        $.ajax({
            type: "POST",
            url: "/update_asset_owner/" + desktopId + "/",
            data: formData,
            success: function(response) {
                if (response.success) {
                    var modal = bootstrap.Modal.getInstance(document.getElementById('editAssetOwnerModal'));
                    modal.hide();
                    var toast = new bootstrap.Toast(document.getElementById('updateSuccessToast_Asset_Owner'));
                    toast.show();
                    setTimeout(function() {
                        window.location.href = window.location.href.split('#')[0] + '#pills-user';
                        window.location.reload();
                    }, 1000);
                } else {
                    showError(response.error || "Failed to update Asset Owner");
                }
            },
            error: function(xhr) {
                showError(xhr.responseJSON?.error || "Something went wrong");
            },
            complete: function() {
                isSubmitting = false;
            }
        });
    });
});
