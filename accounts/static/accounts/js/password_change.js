document.addEventListener("DOMContentLoaded", () => {

    const form =
        document.getElementById("passwordChangeForm");

    const submitButton =
        document.getElementById("passwordSubmit");

    const strengthBox =
        document.getElementById("passwordStrength");

    const strengthLabel =
        document.getElementById("strengthLabel");


    /* =====================================================
       PASSWORD TOGGLES
    ===================================================== */

    const passwordInputs =
        document.querySelectorAll(
            '#passwordChangeForm input[type="password"]'
        );


    passwordInputs.forEach((input) => {

        const wrapper =
            input.closest(".mb-3");

        if (!wrapper) {
            return;
        }


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


        wrapper.appendChild(toggle);


        toggle.addEventListener(
            "click",
            () => {

                const show =
                    input.type === "password";


                input.type =
                    show
                        ? "text"
                        : "password";


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
       PASSWORD STRENGTH
    ===================================================== */

    const newPasswordInput =
        document.querySelector(
            '#passwordChangeForm input[name="new_password1"]'
        );


    const calculateStrength = (password) => {

        if (!password) {
            return {
                score: 0,
                label: "—"
            };
        }


        let score = 0;


        if (password.length >= 8) {
            score++;
        }

        if (password.length >= 12) {
            score++;
        }

        if (/[a-z]/.test(password)) {
            score++;
        }

        if (/[A-Z]/.test(password)) {
            score++;
        }

        if (/[0-9]/.test(password)) {
            score++;
        }

        if (/[^A-Za-z0-9]/.test(password)) {
            score++;
        }


        if (score <= 1) {

            return {
                score: 1,
                label: "Weak"
            };

        }


        if (score <= 3) {

            return {
                score: 2,
                label: "Fair"
            };

        }


        if (score <= 4) {

            return {
                score: 3,
                label: "Good"
            };

        }


        return {
            score: 4,
            label: "Strong"
        };

    };


    const updateStrength = () => {

        if (!newPasswordInput || !strengthBox) {
            return;
        }


        const result =
            calculateStrength(
                newPasswordInput.value
            );


        strengthBox.classList.remove(
            "weak",
            "fair",
            "good",
            "strong"
        );


        if (result.score > 0) {

            const classes = [
                "weak",
                "fair",
                "good",
                "strong"
            ];

            strengthBox.classList.add(
                classes[result.score - 1]
            );

        }


        if (strengthLabel) {

            strengthLabel.textContent =
                result.label;

        }

    };


    if (newPasswordInput) {

        newPasswordInput.addEventListener(
            "input",
            updateStrength
        );

    }


    /* =====================================================
       FORM SUBMIT
    ===================================================== */

    if (form && submitButton) {

        form.addEventListener(
            "submit",
            (event) => {

                if (!form.checkValidity()) {

                    event.preventDefault();

                    form.classList.add(
                        "was-validated"
                    );

                    return;

                }


                submitButton.classList.add(
                    "loading"
                );

                submitButton.disabled =
                    true;

            }
        );

    }


    /* =====================================================
       ALERT CLOSE
    ===================================================== */

    const alertButtons =
        document.querySelectorAll(
            ".password-alert-close"
        );


    alertButtons.forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                const alert =
                    button.closest(
                        ".password-alert"
                    );


                if (!alert) {
                    return;
                }


                alert.style.opacity =
                    "0";

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
            "#passwordChangeForm .form-control"
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

});