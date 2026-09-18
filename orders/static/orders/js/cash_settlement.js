document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       Search
       ========================================================= */

    const searchInput =
        document.getElementById("shipperSearch");

    const clearSearchButton =
        document.getElementById("clearSearch");

    const resetSearchButton =
        document.getElementById("resetSearch");

    const noResults =
        document.getElementById("noSearchResults");

    const cards =
        document.querySelectorAll(".settlement-card");


    function filterCards() {

        if (!searchInput) {
            return;
        }

        const query =
            searchInput.value
                .trim()
                .toLowerCase();

        let visibleCount = 0;


        cards.forEach(function (card) {

            const shipperName =
                card.dataset.shipperName || "";

            const matches =
                shipperName.includes(query);


            if (matches) {

                card.hidden = false;

                visibleCount++;

            } else {

                card.hidden = true;

            }

        });


        if (clearSearchButton) {

            clearSearchButton.hidden =
                query.length === 0;

        }


        if (noResults) {

            noResults.hidden =
                visibleCount !== 0;

        }

    }


    function clearSearch() {

        if (!searchInput) {
            return;
        }

        searchInput.value = "";

        filterCards();

        searchInput.focus();

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterCards
        );

    }


    if (clearSearchButton) {

        clearSearchButton.addEventListener(
            "click",
            clearSearch
        );

    }


    if (resetSearchButton) {

        resetSearchButton.addEventListener(
            "click",
            clearSearch
        );

    }


    /* =========================================================
       Settlement Confirmation Modal
       ========================================================= */

    const confirmationModal =
        document.getElementById(
            "settlementConfirmModal"
        );

    const confirmShipperName =
        document.getElementById(
            "confirmShipperName"
        );

    const confirmSettlementAmount =
        document.getElementById(
            "confirmSettlementAmount"
        );

    const confirmSettlementButton =
        document.getElementById(
            "confirmSettlementButton"
        );


    let activeForm = null;

    let activeCard = null;


    if (confirmationModal) {

        confirmationModal.addEventListener(
            "show.bs.modal",
            function (event) {

                const trigger =
                    event.relatedTarget;


                if (!trigger) {
                    return;
                }


                const formId =
                    trigger.dataset.settlementForm;

                const shipperName =
                    trigger.dataset.shipperName;

                const amount =
                    trigger.dataset.settlementAmount;


                activeForm =
                    formId
                        ? document.getElementById(formId)
                        : null;


                activeCard =
                    trigger.closest(
                        ".settlement-card"
                    );


                if (confirmShipperName) {

                    confirmShipperName.textContent =
                        shipperName || "this shipper";

                }


                if (confirmSettlementAmount) {

                    confirmSettlementAmount.textContent =
                        amount || "0";

                }


                if (confirmSettlementButton) {

                    confirmSettlementButton.disabled =
                        false;

                    confirmSettlementButton.innerHTML = `
                        <span class="settlement-confirm-content">
                            <i class="fas fa-check"></i>
                            Confirm Settlement
                        </span>
                    `;

                }

            }
        );


        confirmationModal.addEventListener(
            "hidden.bs.modal",
            function () {

                activeForm = null;

                activeCard = null;

            }
        );

    }


    /* =========================================================
       Confirm Settlement
       ========================================================= */

    if (confirmSettlementButton) {

        confirmSettlementButton.addEventListener(
            "click",
            function () {

                if (
                    !activeForm ||
                    !activeCard
                ) {
                    return;
                }


                confirmSettlementButton.disabled =
                    true;


                confirmSettlementButton.innerHTML = `
                    <span class="settlement-confirm-content">
                        <i class="fas fa-spinner fa-spin"></i>
                        Processing...
                    </span>
                `;


                activeCard.classList.add(
                    "is-submitting"
                );


                /*
                 * Use the native form submit so
                 * this does not trigger the
                 * confirmation logic again.
                 */

                activeForm.submit();

            }
        );

    }

});