document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("shipperOrderForm");

    if (!form) {
        return;
    }


    /* =========================================================
       Elements
    ========================================================= */

    const statusField = form.querySelector('[name="status"]');
    const notesField = form.querySelector('[name="notes"]');

    const statusBadge = document.getElementById(
        "currentStatusBadge"
    );

    const statusText = document.getElementById(
        "currentStatusText"
    );

    const statusDescription = document.getElementById(
        "statusDescription"
    );

    const feedbackBox = document.getElementById(
        "statusFeedback"
    );

    const feedbackTitle = document.getElementById(
        "statusFeedbackTitle"
    );

    const feedbackText = document.getElementById(
        "statusFeedbackText"
    );

    const feedbackIcon = feedbackBox
        ? feedbackBox.querySelector(
            ".status-feedback-icon i"
        )
        : null;

    const notesCounter = document.getElementById(
        "notesCounter"
    );

    const notesCount = document.getElementById(
        "notesCount"
    );

    const unsavedChanges = document.getElementById(
        "unsavedChanges"
    );

    const saveButton = document.getElementById(
        "saveOrderButton"
    );

    const editIcon = document.querySelector(
        "#editIcon i"
    );

    const modal = document.getElementById(
        "shipperConfirmModal"
    );

    const modalTitle = document.getElementById(
        "confirmModalTitle"
    );

    const modalText = document.getElementById(
        "confirmModalText"
    );

    const modalIcon = document.getElementById(
        "confirmModalIcon"
    );

    const confirmCancelButton = document.getElementById(
        "confirmCancelBtn"
    );

    const confirmSubmitButton = document.getElementById(
        "confirmSubmitBtn"
    );


    /* =========================================================
       Initial Values
    ========================================================= */

    const initialStatus = statusField
        ? statusField.value
        : "";

    const initialNotes = notesField
        ? notesField.value
        : "";

    let pendingSubmit = false;


    /* =========================================================
       Status Configuration
    ========================================================= */

    const statusConfig = {

        SHIPPED: {
            label: "Shipped",

            title: "Order is on the way",

            description:
                "The order has been handed over for delivery and is currently on its way to the customer.",

            icon:
                "fa-truck-fast",

            className:
                "status-shipped"
        },


        DELIVERED: {
            label: "Delivered",

            title: "Order delivered",

            description:
                "Confirm this only after the customer has received the order successfully.",

            icon:
                "fa-circle-check",

            className:
                "status-delivered"
        },


        RETURNED: {
            label: "Returned",

            title: "Order returned",

            description:
                "Use this status when the order has been returned and could not be completed.",

            icon:
                "fa-rotate-left",

            className:
                "status-returned"
        }

    };


    /* =========================================================
       Update Status UI
    ========================================================= */

    function updateStatusUI() {

        if (!statusField) {
            return;
        }

        const selectedStatus =
            statusField.value;

        const config =
            statusConfig[selectedStatus];

        if (!config) {
            return;
        }


        /* -----------------------------------------------------
           Badge
        ----------------------------------------------------- */

        if (statusBadge) {

            statusBadge.classList.remove(
                "status-shipped",
                "status-delivered",
                "status-returned"
            );

            statusBadge.classList.add(
                config.className
            );
        }


        if (statusText) {
            statusText.textContent =
                config.label;
        }


        /* -----------------------------------------------------
           Description
        ----------------------------------------------------- */

        if (statusDescription) {

            statusDescription.textContent =
                config.description;
        }


        /* -----------------------------------------------------
           Feedback
        ----------------------------------------------------- */

        if (feedbackTitle) {

            feedbackTitle.textContent =
                config.title;
        }


        if (feedbackText) {

            feedbackText.textContent =
                config.description;
        }


        if (feedbackBox) {

            feedbackBox.classList.remove(
                "status-changed"
            );

            /*
             * Force browser reflow so animation
             * can run every time.
             */
            void feedbackBox.offsetWidth;

            feedbackBox.classList.add(
                "status-changed"
            );

        }


        /* -----------------------------------------------------
           Feedback Icon
        ----------------------------------------------------- */

        if (feedbackIcon) {

            feedbackIcon.className =
                `fas ${config.icon}`;

        }


        /* -----------------------------------------------------
           Edit Icon
        ----------------------------------------------------- */

        if (editIcon) {

            editIcon.className =
                `fas ${config.icon}`;

        }


        updateUnsavedState();
    }


    /* =========================================================
       Notes Counter
    ========================================================= */

    function updateNotesCounter() {

        if (!notesField || !notesCount) {
            return;
        }

        const length =
            notesField.value.length;

        notesCount.textContent =
            length;


        if (!notesCounter) {
            return;
        }


        notesCounter.classList.remove(
            "near-limit",
            "at-limit"
        );


        if (length >= 450) {

            notesCounter.classList.add(
                "at-limit"
            );

        }
        else if (length >= 400) {

            notesCounter.classList.add(
                "near-limit"
            );

        }

    }


    /* =========================================================
       Unsaved Changes
    ========================================================= */

    function updateUnsavedState() {

        if (!unsavedChanges) {
            return;
        }

        const statusChanged =
            statusField &&
            statusField.value !== initialStatus;

        const notesChanged =
            notesField &&
            notesField.value !== initialNotes;


        if (statusChanged || notesChanged) {

            unsavedChanges.classList.add(
                "visible"
            );

        }
        else {

            unsavedChanges.classList.remove(
                "visible"
            );

        }

    }


    /* =========================================================
       Confirmation Modal
    ========================================================= */

    function openConfirmation() {

        if (!modal || !statusField) {
            return;
        }

        const selectedStatus =
            statusField.value;

        const config =
            statusConfig[selectedStatus];


        if (!config) {
            submitForm();
            return;
        }


        if (modalTitle) {

            modalTitle.textContent =
                `Mark Order as ${config.label}?`;

        }


        if (modalText) {

            modalText.textContent =
                config.description;

        }


        if (modalIcon) {

            modalIcon.innerHTML =
                `<i class="fas ${config.icon}"></i>`;

        }


        if (confirmSubmitButton) {

            confirmSubmitButton.classList.remove(
                "status-returned"
            );


            if (selectedStatus === "RETURNED") {

                confirmSubmitButton.classList.add(
                    "status-returned"
                );

                confirmSubmitButton.textContent =
                    "Confirm Return";

            }
            else if (selectedStatus === "DELIVERED") {

                confirmSubmitButton.textContent =
                    "Confirm Delivered";

            }
            else {

                confirmSubmitButton.textContent =
                    "Confirm Update";

            }

        }


        modal.classList.add(
            "active"
        );

        modal.setAttribute(
            "aria-hidden",
            "false"
        );


        document.body.classList.add(
            "modal-open"
        );


        if (confirmSubmitButton) {
            confirmSubmitButton.focus();
        }

    }


    function closeConfirmation() {

        if (!modal) {
            return;
        }


        modal.classList.remove(
            "active"
        );


        modal.setAttribute(
            "aria-hidden",
            "true"
        );


        document.body.classList.remove(
            "modal-open"
        );

    }


    /* =========================================================
       Submit
    ========================================================= */

    function submitForm() {

        if (pendingSubmit) {
            return;
        }


        pendingSubmit = true;


        if (saveButton) {

            saveButton.disabled =
                true;

            saveButton.classList.add(
                "is-loading"
            );


            saveButton.innerHTML = `
                <span class="save-button-content">
                    <i class="fas fa-spinner fa-spin"></i>
                    Updating...
                </span>
            `;

        }


        /*
         * Native submit avoids triggering
         * the submit event again.
         */
        form.submit();

    }


    /* =========================================================
       Status Change
    ========================================================= */

    if (statusField) {

        statusField.addEventListener(
            "change",
            updateStatusUI
        );

    }


    /* =========================================================
       Notes Change
    ========================================================= */

    if (notesField) {

        notesField.addEventListener(
            "input",
            function () {

                updateNotesCounter();

                updateUnsavedState();

            }
        );

    }


    /* =========================================================
       Form Submit
    ========================================================= */

    form.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();


            if (pendingSubmit) {
                return;
            }


            const statusChanged =
                statusField &&
                statusField.value !== initialStatus;


            const notesChanged =
                notesField &&
                notesField.value !== initialNotes;


            /* -------------------------------------------------
               Nothing changed
            ------------------------------------------------- */

            if (!statusChanged && !notesChanged) {

                if (unsavedChanges) {

                    const message =
                        unsavedChanges.querySelector(
                            "span"
                        );


                    unsavedChanges.classList.add(
                        "visible"
                    );


                    if (message) {

                        const originalText =
                            message.textContent;

                        message.textContent =
                            "There are no changes to save.";


                        setTimeout(function () {

                            message.textContent =
                                originalText;

                        }, 2200);

                    }

                }

                return;
            }


            /* -------------------------------------------------
               Confirmation for important statuses
            ------------------------------------------------- */

            if (
                statusField &&
                (
                    statusField.value === "DELIVERED" ||
                    statusField.value === "RETURNED"
                )
            ) {

                openConfirmation();

                return;

            }


            submitForm();

        }
    );


    /* =========================================================
       Confirmation Cancel
    ========================================================= */

    if (confirmCancelButton) {

        confirmCancelButton.addEventListener(
            "click",
            closeConfirmation
        );

    }


    /* =========================================================
       Confirmation Submit
    ========================================================= */

    if (confirmSubmitButton) {

        confirmSubmitButton.addEventListener(
            "click",
            function () {

                closeConfirmation();

                submitForm();

            }
        );

    }


    /* =========================================================
       Click Outside Modal
    ========================================================= */

    if (modal) {

        modal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target === modal
                ) {

                    closeConfirmation();

                }

            }
        );

    }


    /* =========================================================
       Escape Key
    ========================================================= */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal &&
                modal.classList.contains("active")
            ) {

                closeConfirmation();

            }

        }
    );


    /* =========================================================
       Prevent Accidental Page Leave
       ========================================================= */

    window.addEventListener(
        "beforeunload",
        function (event) {

            const statusChanged =
                statusField &&
                statusField.value !== initialStatus;


            const notesChanged =
                notesField &&
                notesField.value !== initialNotes;


            if (
                !pendingSubmit &&
                (statusChanged || notesChanged)
            ) {

                event.preventDefault();

                event.returnValue = "";

            }

        }
    );


    /* =========================================================
       Initialize
    ========================================================= */

    updateStatusUI();

    updateNotesCounter();

    updateUnsavedState();

});