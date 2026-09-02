document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       ELEMENTS
    ===================================================== */

    const settingsForm =
        document.getElementById("storeSettingsForm");

    const saveButton =
        document.getElementById("settingsSaveButton");

    const tokenToggle =
        document.getElementById("tokenToggle");

    const tokenInput =
        document.querySelector(
            'input[name="meta_api_token"]'
        );

    const deactivateButton =
        document.getElementById("openDeactivateModal");

    const deactivateForm =
        document.getElementById("deactivateForm");

    const deactivateSubmit =
        document.getElementById("deactivateSubmit");

    const activateForm =
        document.getElementById("activateForm");

    const activateSubmit =
        document.getElementById("activateSubmit");


    /* =====================================================
       API TOKEN SHOW / HIDE
    ===================================================== */

    if (tokenToggle && tokenInput) {

        tokenToggle.addEventListener(
            "click",
            () => {

                const showToken =
                    tokenInput.type === "password";

                tokenInput.type =
                    showToken
                        ? "text"
                        : "password";


                tokenToggle.innerHTML =
                    showToken
                        ? '<i class="fas fa-eye-slash"></i>'
                        : '<i class="fas fa-eye"></i>';


                tokenToggle.setAttribute(
                    "aria-label",
                    showToken
                        ? "Hide API token"
                        : "Show API token"
                );


                tokenInput.focus();

            }
        );

    }


    /* =====================================================
       SAVE SETTINGS
    ===================================================== */

    if (settingsForm && saveButton) {

        settingsForm.addEventListener(
            "submit",
            (event) => {

                /*
                 * Let Django handle the real validation.
                 * This only gives the browser basic UX feedback.
                 */

                if (!settingsForm.checkValidity()) {

                    event.preventDefault();

                    settingsForm.classList.add(
                        "was-validated"
                    );

                    return;

                }


                saveButton.classList.add(
                    "loading"
                );

                saveButton.disabled = true;

            }
        );

    }


    /* =====================================================
       DEACTIVATE MODAL
    ===================================================== */

    if (deactivateButton) {

        deactivateButton.addEventListener(
            "click",
            () => {

                const modalElement =
                    document.getElementById(
                        "deactivateModal"
                    );


                if (
                    !modalElement ||
                    typeof bootstrap === "undefined"
                ) {
                    return;
                }


                const modal =
                    bootstrap.Modal.getOrCreateInstance(
                        modalElement
                    );


                modal.show();

            }
        );

    }


    /* =====================================================
       DEACTIVATE STORE
    ===================================================== */

    if (deactivateForm && deactivateSubmit) {

        deactivateForm.addEventListener(
            "submit",
            () => {

                deactivateSubmit.classList.add(
                    "loading"
                );

                deactivateSubmit.disabled =
                    true;

            }
        );

    }


    /* =====================================================
       ACTIVATE STORE
    ===================================================== */

    if (activateForm && activateSubmit) {

        activateForm.addEventListener(
            "submit",
            () => {

                activateSubmit.classList.add(
                    "loading"
                );

                activateSubmit.disabled =
                    true;

            }
        );

    }


    /* =====================================================
       CLOSE ALERTS
    ===================================================== */

    const alertCloseButtons =
        document.querySelectorAll(
            ".settings-alert-close"
        );


    alertCloseButtons.forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                const alert =
                    button.closest(
                        ".settings-alert"
                    );


                if (!alert) {
                    return;
                }


                alert.style.opacity = "0";

                alert.style.transform =
                    "translateY(-5px)";

                alert.style.transition =
                    "opacity .2s ease, transform .2s ease";


                setTimeout(() => {

                    alert.remove();

                }, 220);

            }
        );

    });


    /* =====================================================
       FIELD MICRO INTERACTION
    ===================================================== */

    const fields =
        document.querySelectorAll(
            ".settings-fields .form-control"
        );


    fields.forEach((field) => {

        field.addEventListener(
            "focus",
            () => {

                const wrapper =
                    field.closest(".mb-3");


                if (wrapper) {

                    wrapper.style.transform =
                        "translateY(-1px)";

                    wrapper.style.transition =
                        "transform .2s ease";

                }

            }
        );


        field.addEventListener(
            "blur",
            () => {

                const wrapper =
                    field.closest(".mb-3");


                if (wrapper) {

                    wrapper.style.transform =
                        "translateY(0)";

                }

            }
        );

    });


    /* =====================================================
       DIRTY FORM DETECTION
    ===================================================== */

    if (settingsForm) {

        let formChanged = false;


        const formFields =
            settingsForm.querySelectorAll(
                "input, select, textarea"
            );


        formFields.forEach((field) => {

            field.addEventListener(
                "input",
                () => {
                    formChanged = true;
                }
            );


            field.addEventListener(
                "change",
                () => {
                    formChanged = true;
                }
            );

        });


        settingsForm.addEventListener(
            "submit",
            () => {
                formChanged = false;
            }
        );


        window.addEventListener(
            "beforeunload",
            (event) => {

                if (!formChanged) {
                    return;
                }


                event.preventDefault();

                event.returnValue = "";

            }
        );

    }

});