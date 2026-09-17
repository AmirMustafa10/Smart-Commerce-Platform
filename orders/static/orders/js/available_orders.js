document.addEventListener("DOMContentLoaded", function () {

    /*
     * Make the entire order card clickable.
     * The Take Order form/button remains independent.
     */
    const orderCards = document.querySelectorAll(".available-order-package");

    orderCards.forEach(function (card) {

        const detailUrl = card.dataset.orderDetailUrl;

        if (!detailUrl) {
            return;
        }

        card.addEventListener("click", function (event) {

            /*
             * Do not navigate when the user clicks
             * the Take Order form or button.
             */
            if (
                event.target.closest(".take-order-form") ||
                event.target.closest(".take-order-btn")
            ) {
                return;
            }

            window.location.href = detailUrl;
        });


        /*
         * Keyboard accessibility.
         * Enter or Space opens order details.
         */
        card.addEventListener("keydown", function (event) {

            if (event.key === "Enter" || event.key === " ") {

                /*
                 * Prevent page scrolling when Space is used.
                 */
                event.preventDefault();

                window.location.href = detailUrl;
            }

        });

    });


    /*
     * Prevent clicks inside the Take Order form
     * from bubbling to the order card.
     */
    const takeOrderForms = document.querySelectorAll(".take-order-form");

    takeOrderForms.forEach(function (form) {

        form.addEventListener("click", function (event) {
            event.stopPropagation();
        });

    });


    /*
     * Add a small loading state after submitting Take Order.
     * This prevents double clicks while the request is being sent.
     */
    const takeOrderButtons = document.querySelectorAll(".take-order-btn");

    takeOrderButtons.forEach(function (button) {

        const form = button.closest(".take-order-form");

        if (!form) {
            return;
        }

        form.addEventListener("submit", function () {

            /*
             * Avoid changing the button more than once.
             */
            if (button.dataset.submitting === "true") {
                return;
            }

            button.dataset.submitting = "true";

            button.disabled = true;

            button.innerHTML = `
                <span>Taking Order...</span>
                <i class="fas fa-spinner fa-spin"></i>
            `;

        });

    });

});