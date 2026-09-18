document.addEventListener("DOMContentLoaded", () => {

    /* =========================================================
       MARK AS DELIVERED
    ========================================================= */

    const deliverForms = document.querySelectorAll("[data-deliver-form]");

    deliverForms.forEach((form) => {

        form.addEventListener("submit", (event) => {

            const button = form.querySelector(".shipper-deliver-btn");

            if (!button) {
                return;
            }

            if (button.disabled) {
                event.preventDefault();
                return;
            }

            const confirmed = window.confirm(
                "Are you sure you want to mark this order as delivered?"
            );

            if (!confirmed) {
                event.preventDefault();
                return;
            }

            button.disabled = true;
            button.classList.add("loading");
            button.setAttribute("aria-busy", "true");

        });

    });


    /* =========================================================
       DELIVERED ORDER ACCORDION
    ========================================================= */

    const deliveredCards = document.querySelectorAll(
        "[data-delivered-card]"
    );

    deliveredCards.forEach((card) => {

        const toggle = card.querySelector(
            ".shipper-delivered-toggle"
        );

        if (!toggle) {
            return;
        }

        toggle.addEventListener("click", () => {

            const isOpen = card.classList.contains("open");

            /* Close all other cards */
            deliveredCards.forEach((otherCard) => {

                if (otherCard === card) {
                    return;
                }

                otherCard.classList.remove("open");

                const otherToggle =
                    otherCard.querySelector(
                        ".shipper-delivered-toggle"
                    );

                if (otherToggle) {
                    otherToggle.setAttribute(
                        "aria-expanded",
                        "false"
                    );
                }

            });


            /* Toggle current card */
            card.classList.toggle("open", !isOpen);

            toggle.setAttribute(
                "aria-expanded",
                String(!isOpen)
            );

        });

    });


    /* =========================================================
       QUICK ACTION KEYBOARD FEEDBACK
    ========================================================= */

    const interactiveElements = document.querySelectorAll(
        ".shipper-quick-action, .shipper-deliver-btn, .shipper-delivered-toggle"
    );

    interactiveElements.forEach((element) => {

        element.addEventListener("mousedown", () => {
            element.classList.add("is-pressed");
        });

        element.addEventListener("mouseup", () => {
            element.classList.remove("is-pressed");
        });

        element.addEventListener("mouseleave", () => {
            element.classList.remove("is-pressed");
        });

    });


    /* =========================================================
       DELIVERY ACTION FEEDBACK
    ========================================================= */

    const activeCards = document.querySelectorAll(
        "[data-order-card]"
    );

    activeCards.forEach((card) => {

        const deliverForm = card.querySelector(
            "[data-deliver-form]"
        );

        if (!deliverForm) {
            return;
        }

        deliverForm.addEventListener("submit", () => {

            card.classList.add("is-updating");

        });

    });

});