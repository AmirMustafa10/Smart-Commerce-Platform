document.addEventListener("DOMContentLoaded", () => {

    const form =
        document.getElementById("signupForm");

    const submitButton =
        document.getElementById("signupSubmit");

    const termsCheckbox =
        document.getElementById("termsCheckbox");

    const progressBar =
        document.getElementById("signupProgressBar");

    const progressText =
        document.getElementById("signupProgressText");


    /* =====================================================
       FORM ELEMENTS
    ===================================================== */

    if (!form) {
        return;
    }

    const inputs =
        form.querySelectorAll(
            "input:not([type='hidden']):not([type='checkbox']), select, textarea"
        );


    /* =====================================================
       PASSWORD TOGGLE
    ===================================================== */

    const passwordInputs =
        form.querySelectorAll(
            "input[type='password']"
        );


    passwordInputs.forEach((input) => {

        const parent =
            input.parentElement;

        if (!parent) {
            return;
        }

        parent.classList.add(
            "password-field"
        );


        const button =
            document.createElement("button");

        button.type = "button";

        button.className =
            "password-toggle";

        button.setAttribute(
            "aria-label",
            "Show password"
        );

        button.innerHTML =
            '<i class="fas fa-eye"></i>';


        parent.appendChild(button);


        button.addEventListener(
            "click",
            () => {

                const isPassword =
                    input.type === "password";


                input.type =
                    isPassword
                        ? "text"
                        : "password";


                button.innerHTML =
                    isPassword
                        ? '<i class="fas fa-eye-slash"></i>'
                        : '<i class="fas fa-eye"></i>';


                button.setAttribute(
                    "aria-label",
                    isPassword
                        ? "Hide password"
                        : "Show password"
                );


                input.focus();

            }
        );

    });


    /* =====================================================
       FORM PROGRESS
    ===================================================== */

    const updateProgress = () => {

        if (!inputs.length) {
            return;
        }


        let completed = 0;


        inputs.forEach((input) => {

            if (
                input.value &&
                input.value.trim() !== ""
            ) {
                completed++;
            }

        });


        const percentage =
            Math.round(
                (completed / inputs.length) * 100
            );


        if (progressBar) {

            progressBar.style.width =
                `${percentage}%`;

        }


        if (progressText) {

            progressText.textContent =
                `${percentage}%`;

        }

    };


    inputs.forEach((input) => {

        input.addEventListener(
            "input",
            updateProgress
        );

        input.addEventListener(
            "change",
            updateProgress
        );

    });


    updateProgress();


    /* =====================================================
       TERMS
    ===================================================== */

    const updateSubmitState = () => {

        if (!submitButton) {
            return;
        }


        const termsAccepted =
            termsCheckbox
                ? termsCheckbox.checked
                : true;


        /*
         * We only use the terms checkbox here.
         * Django remains responsible for actual server validation.
         */

        submitButton.disabled =
            !termsAccepted;

    };


    if (termsCheckbox) {

        termsCheckbox.addEventListener(
            "change",
            updateSubmitState
        );

    }


    updateSubmitState();


    /* =====================================================
       DJANGO ALERTS
    ===================================================== */

    const alertCloseButtons =
        document.querySelectorAll(
            ".signup-alert-close"
        );


    alertCloseButtons.forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                const alert =
                    button.closest(
                        ".signup-alert"
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
       SUBMIT LOADING
    ===================================================== */

    form.addEventListener(
        "submit",
        () => {

            if (!submitButton) {
                return;
            }


            /*
             * Native HTML validation should still work.
             */
            if (!form.checkValidity()) {
                return;
            }


            submitButton.classList.add(
                "loading"
            );

            submitButton.disabled = true;

        }
    );


    /* =====================================================
       RIPPLE
    ===================================================== */

    if (submitButton) {

        submitButton.addEventListener(
            "pointerdown",
            (event) => {

                if (
                    submitButton.disabled ||
                    submitButton.classList.contains(
                        "loading"
                    )
                ) {
                    return;
                }


                const rect =
                    submitButton.getBoundingClientRect();


                const size =
                    Math.max(
                        rect.width,
                        rect.height
                    );


                const ripple =
                    document.createElement("span");


                ripple.style.position =
                    "absolute";

                ripple.style.width =
                    `${size}px`;

                ripple.style.height =
                    `${size}px`;

                ripple.style.left =
                    `${event.clientX - rect.left - size / 2}px`;

                ripple.style.top =
                    `${event.clientY - rect.top - size / 2}px`;

                ripple.style.borderRadius =
                    "50%";

                ripple.style.background =
                    "rgba(255,255,255,.22)";

                ripple.style.pointerEvents =
                    "none";

                ripple.style.transform =
                    "scale(0)";

                ripple.style.transition =
                    "transform .5s ease, opacity .5s ease";


                submitButton.appendChild(
                    ripple
                );


                requestAnimationFrame(() => {

                    ripple.style.transform =
                        "scale(2.2)";

                    ripple.style.opacity =
                        "0";

                });


                setTimeout(() => {

                    ripple.remove();

                }, 550);

            }
        );

    }


    /* =====================================================
       PASSWORD FIELD CSS INJECTION
       Makes the eye button work with crispy fields
    ===================================================== */

    const passwordFields =
        document.querySelectorAll(
            ".password-field"
        );


    passwordFields.forEach((field) => {

        const input =
            field.querySelector(
                "input"
            );

        if (!input) {
            return;
        }


        input.style.paddingRight =
            "43px";


        field.style.position =
            "relative";


        const toggle =
            field.querySelector(
                ".password-toggle"
            );

        if (!toggle) {
            return;
        }


        Object.assign(
            toggle.style,
            {
                position: "absolute",
                right: "8px",
                top: "50%",
                width: "31px",
                height: "31px",
                transform: "translateY(-50%)",
                border: "0",
                background: "transparent",
                color: "#98a2b3",
                borderRadius: "8px",
                display: "grid",
                placeItems: "center",
                cursor: "pointer"
            }
        );

    });


    /* =====================================================
       FOCUS MICRO-INTERACTION
    ===================================================== */

    inputs.forEach((input) => {

        input.addEventListener(
            "focus",
            () => {

                const wrapper =
                    input.closest(".mb-3");

                if (wrapper) {
                    wrapper.style.transform =
                        "translateY(-1px)";
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