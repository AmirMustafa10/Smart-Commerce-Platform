document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       ALERT CLOSE
    ===================================================== */

    const alertButtons =
        document.querySelectorAll(".profile-alert-close");

    alertButtons.forEach((button) => {

        button.addEventListener("click", () => {

            const alert =
                button.closest(".profile-alert");

            if (!alert) {
                return;
            }

            alert.style.opacity = "0";
            alert.style.transform = "translateY(-5px)";
            alert.style.transition =
                "opacity .2s ease, transform .2s ease";

            setTimeout(() => {
                alert.remove();
            }, 220);

        });

    });


    /* =====================================================
       PROFILE FORM
    ===================================================== */

    const profileForm =
        document.getElementById("profileForm");

    const profileSaveButton =
        document.getElementById("profileSaveButton");


    if (profileForm && profileSaveButton) {

        profileForm.addEventListener(
            "submit",
            (event) => {

                if (!profileForm.checkValidity()) {

                    event.preventDefault();

                    profileForm.classList.add(
                        "was-validated"
                    );

                    return;
                }

                profileSaveButton.classList.add(
                    "loading"
                );

                profileSaveButton.disabled = true;

            }
        );

    }


    /* =====================================================
       PASSWORD FORM
    ===================================================== */

    const passwordForm =
        document.getElementById("passwordForm");

    const passwordSubmitButton =
        document.getElementById("passwordSubmitButton");


    if (passwordForm && passwordSubmitButton) {

        passwordForm.addEventListener(
            "submit",
            (event) => {

                if (!passwordForm.checkValidity()) {

                    event.preventDefault();

                    passwordForm.classList.add(
                        "was-validated"
                    );

                    return;
                }

                passwordSubmitButton.classList.add(
                    "loading"
                );

                passwordSubmitButton.disabled =
                    true;

            }
        );

    }


    /* =====================================================
       PASSWORD SHOW / HIDE
    ===================================================== */

    const passwordInputs =
        document.querySelectorAll(
            '#passwordForm input[type="password"]'
        );


    passwordInputs.forEach((input) => {

        const parent =
            input.parentElement;

        if (!parent) {
            return;
        }

        parent.style.position =
            "relative";

        input.style.paddingRight =
            "42px";


        const toggle =
            document.createElement("button");

        toggle.type = "button";

        toggle.className =
            "profile-password-toggle";

        toggle.setAttribute(
            "aria-label",
            "Show password"
        );

        toggle.innerHTML =
            '<i class="fas fa-eye"></i>';


        Object.assign(
            toggle.style,
            {
                position: "absolute",
                right: "8px",
                top: "50%",
                width: "30px",
                height: "30px",
                transform: "translateY(-50%)",
                border: "0",
                borderRadius: "7px",
                background: "transparent",
                color: "#98a2b3",
                display: "grid",
                placeItems: "center",
                cursor: "pointer"
            }
        );


        parent.appendChild(toggle);


        toggle.addEventListener(
            "click",
            () => {

                const show =
                    input.type === "password";

                input.type =
                    show ? "text" : "password";

                toggle.innerHTML =
                    show
                        ? '<i class="fas fa-eye-slash"></i>'
                        : '<i class="fas fa-eye"></i>';

                toggle.setAttribute(
                    "aria-label",
                    show
                        ? "Hide password"
                        : "Show password"
                );

                input.focus();

            }
        );

    });


    /* =====================================================
       FIELD MICRO INTERACTION
    ===================================================== */

    const inputs =
        document.querySelectorAll(
            ".profile-form .form-control, .password-form .form-control"
        );


    inputs.forEach((input) => {

        input.addEventListener(
            "focus",
            () => {

                const wrapper =
                    input.closest(".mb-3");

                if (wrapper) {
                    wrapper.style.transform =
                        "translateY(-1px)";
                    wrapper.style.transition =
                        "transform .2s ease";
                }

            }
        );


        input.addEventListener(
            "blur",
            () => {

                const wrapper =
                    input.closest(".mb-3");

                if (wrapper) {
                    wrapper.style.transform =
                        "translateY(0)";
                }

            }
        );

    });

});