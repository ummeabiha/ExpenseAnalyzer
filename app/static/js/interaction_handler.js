document.addEventListener("DOMContentLoaded", function () {
    // Flash Messages Animation
    const flashMessages = document.querySelectorAll(".flash-message");
    flashMessages.forEach((message) => {
        setTimeout(() => {
            message.style.transition = "opacity 0.5s";
            message.style.opacity = "0";
            setTimeout(() => message.remove(), 1000);
        }, 5000);
    });

    // Prevent Duplicate Submissions
    const formsWithSubmitButtons = [
        { formId: "add-expense-form", buttonId: "add-expense-submit-button" },
        { formId: "edit-expense-form", buttonId: "edit-expense-submit-button" },
        { formId: "login-form", buttonId: "login-submit-button" },
        { formId: "register-form", buttonId: "register-submit-button" },
        { formId: "set-budget-form", buttonId: "set-budget-submit-button" },
        { formId: "update-budget-form", buttonId: "update-budget-submit-button" },
    ];

    formsWithSubmitButtons.forEach((entry) => {
        const form = document.getElementById(entry.formId);
        const submitButton = document.getElementById(entry.buttonId);

        if (form && submitButton) {
            form.addEventListener("submit", function (event) {
                if (submitButton.disabled) {
                    event.preventDefault();
                    return;
                }
                // Disable the submit button to prevent duplicate submissions
                submitButton.disabled = true;
                submitButton.textContent = "Processing...";
            });
        }
    });
});
