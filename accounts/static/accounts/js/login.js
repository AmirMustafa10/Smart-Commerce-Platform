document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       LOGIN FORM
    ===================================================== */

    const form =
        document.getElementById("loginForm");

    const submitButton =
        document.getElementById("loginSubmit");


    if (form && submitButton) {

        form.addEventListener("submit", () => {

            /*
             * Don't block submission.
             * Just give the user immediate visual feedback.
             */

            submitButton.classList.add("loading");

            submitButton.disabled = true;

        });

    }


    /* =====================================================
       PASSWORD TOGGLE
    ===================================================== */

    const passwordInputs =
        document.querySelectorAll(
            'input[type="password"]'
        );


    passwordInputs.forEach((input) => {

        /*
         * Crispy forms may wrap the input differently,
         * so we operate directly on the input's parent.
         */

        const parent =
            input.parentElement;

        if (!parent) {
            return;
        }

        parent.classList.add("password-field");


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


        button.addEventListener("click", () => {

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


            /*
             * Keep cursor focus inside the input.
             */
            input.focus();

        });

    });


    /* =====================================================
       DISMISS DJANGO MESSAGES
    ===================================================== */

    const alertCloseButtons =
        document.querySelectorAll(
            ".auth-alert-close"
        );


    alertCloseButtons.forEach((button) => {

        button.addEventListener("click", () => {

            const alert =
                button.closest(".auth-alert");

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

        });

    });


    /* =====================================================
       INPUT MICRO INTERACTION
    ===================================================== */

    const inputs =
        document.querySelectorAll(
            ".auth-form .form-control"
        );


    inputs.forEach((input) => {

        input.addEventListener("focus", () => {

            const wrapper =
                input.closest(".mb-3");

            if (wrapper) {
                wrapper.classList.add("field-focused");
            }

        });


        input.addEventListener("blur", () => {

            const wrapper =
                input.closest(".mb-3");

            if (wrapper) {
                wrapper.classList.remove(
                    "field-focused"
                );
            }

        });

    });


    /* =====================================================
       BUTTON RIPPLE
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


                const ripple =
                    document.createElement("span");


                const size =
                    Math.max(
                        rect.width,
                        rect.height
                    );


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

                ripple.style.opacity =
                    "1";

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
       PREVIEW ACTIVITY PULSE
    ===================================================== */

    const previewOrders =
        document.querySelectorAll(
            ".preview-order"
        );


    previewOrders.forEach((order, index) => {

        setTimeout(() => {

            order.animate(
                [
                    {
                        opacity: .45,
                        transform: "translateX(-5px)"
                    },
                    {
                        opacity: 1,
                        transform: "translateX(0)"
                    }
                ],
                {
                    duration: 500,
                    easing: "cubic-bezier(.2,.8,.2,1)"
                }
            );

        }, 250 + (index * 120));

    });

});