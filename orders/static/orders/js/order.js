document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       Alerts
    ===================================================== */

    document.querySelectorAll(".order-alert-close").forEach(function (button) {

        button.addEventListener("click", function () {

            const alert = button.closest(".order-alert");

            if (!alert) {
                return;
            }

            alert.style.opacity = "0";
            alert.style.transform = "translateY(-5px)";

            setTimeout(function () {
                alert.remove();
            }, 200);

        });

    });


    /* =====================================================
   Server-side Search
===================================================== */

const searchInput =
    document.getElementById("orderSearch");

document.addEventListener(
    "keydown",
    function (event) {

        if (
            (event.ctrlKey || event.metaKey) &&
            event.key.toLowerCase() === "k" &&
            searchInput
        ) {

            event.preventDefault();

            searchInput.focus();
            searchInput.select();

        }

    }
);


    /* =====================================================
       Delete Modal
    ===================================================== */

    const deleteModal =
        document.getElementById("orderDeleteModal");

    const deleteForm =
        document.getElementById("orderDeleteForm");

    const deleteName =
        document.getElementById("deleteOrderName");

    const confirmDeleteBtn =
        document.getElementById(
            "confirmOrderDeleteBtn"
        );


    function openDeleteModal(name, deleteUrl) {

        if (
            !deleteModal ||
            !deleteForm
        ) {
            return;
        }


        if (deleteName) {

            deleteName.textContent =
                name;

        }


        deleteForm.action =
            deleteUrl;


        deleteModal.classList.add("show");

        deleteModal.setAttribute(
            "aria-hidden",
            "false"
        );

        document.body.style.overflow =
            "hidden";

    }


    function closeDeleteModal() {

        if (!deleteModal) {
            return;
        }


        deleteModal.classList.remove("show");

        deleteModal.setAttribute(
            "aria-hidden",
            "true"
        );

        document.body.style.overflow =
            "";

    }


    document.querySelectorAll(
        ".delete-order-btn"
    ).forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                const name =
                    button.dataset.orderName ||
                    "this order";

                const deleteUrl =
                    button.dataset.deleteUrl ||
                    "";

                openDeleteModal(
                    name,
                    deleteUrl
                );

            }
        );

    });


    document.querySelectorAll(
        "[data-close-order-delete]"
    ).forEach(function (element) {

        element.addEventListener(
            "click",
            closeDeleteModal
        );

    });


    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {

            closeDeleteModal();

        }

    });


    if (
        deleteForm &&
        confirmDeleteBtn
    ) {

        deleteForm.addEventListener(
            "submit",
            function () {

                confirmDeleteBtn.classList.add(
                    "is-loading"
                );

                confirmDeleteBtn.disabled =
                    true;

            }
        );

    }


    /* =====================================================
       Button Press Effect
    ===================================================== */

    document.querySelectorAll(
        ".order-btn, .order-view-details-btn, .order-icon-action, .order-sidebar-action"
    ).forEach(function (button) {

        button.addEventListener(
            "mousedown",
            function () {
                button.style.transform =
                    "scale(0.98)";
            }
        );


        button.addEventListener(
            "mouseup",
            function () {
                button.style.transform = "";
            }
        );


        button.addEventListener(
            "mouseleave",
            function () {
                button.style.transform = "";
            }
        );

    });


    /* =====================================================
       Order Detail Page
    ===================================================== */

    const detailPage =
        document.querySelector(
            ".order-detail-page"
        );


    if (detailPage) {

        /*
         * Small entrance effect for detail cards.
         */

        document.querySelectorAll(
            ".order-detail-card, .order-detail-sidebar > section"
        ).forEach(function (card, index) {

            card.style.animationDelay =
                `${index * 0.05}s`;

        });

    }


    /* =====================================================
       Order Form
    ===================================================== */

    const orderForm =
        document.getElementById("orderForm");

    const orderSubmitBtn =
        document.getElementById("orderSubmitBtn");


    if (
        orderForm &&
        orderSubmitBtn
    ) {

        orderForm.addEventListener(
            "submit",
            function () {

                orderSubmitBtn.classList.add(
                    "is-loading"
                );

                orderSubmitBtn.disabled =
                    true;

            }
        );

    }


    /* =====================================================
       Customer Toggle
    ===================================================== */

    const customerChoices =
        document.querySelectorAll(
            ".order-customer-choice-card"
        );

    const existingCustomerBox =
        document.querySelector(
            ".order-customer-existing"
        );

    const newCustomerBox =
        document.querySelector(
            ".order-new-customer-box"
        );

    const customerSelect =
        document.getElementById(
            "id_customer"
        );


    function setCustomerMode(mode) {

        customerChoices.forEach(
            function (choice, index) {

                const active =
                    mode === "existing"
                        ? index === 0
                        : index === 1;

                choice.classList.toggle(
                    "active",
                    active
                );

            }
        );


        if (existingCustomerBox) {

            existingCustomerBox.style.display =
                mode === "existing"
                    ? ""
                    : "none";

        }


        if (newCustomerBox) {

            newCustomerBox.classList.toggle(
                "is-visible",
                mode === "new"
            );

        }


        if (
            mode === "new" &&
            customerSelect
        ) {

            customerSelect.value = "";

        }

    }


    customerChoices.forEach(
        function (choice, index) {

            choice.addEventListener(
                "click",
                function () {

                    setCustomerMode(
                        index === 0
                            ? "existing"
                            : "new"
                    );

                }
            );

        }
    );


    /* =====================================================
       Initial customer mode
    ===================================================== */

    if (
        customerSelect &&
        customerChoices.length
    ) {

        if (customerSelect.value) {

            setCustomerMode(
                "existing"
            );

        }

    }


    /* =====================================================
       Order Formset
    ===================================================== */

    const itemsContainer =
        document.getElementById(
            "orderItemsContainer"
        );

    const totalFormsInput =
        document.querySelector(
            'input[name$="-TOTAL_FORMS"]'
        );

    const addItemBtn =
        document.getElementById(
            "addOrderItem"
        );

    const emptyTemplate =
        document.getElementById(
            "emptyOrderItemTemplate"
        );


    function updateItemIndexes() {

        if (!itemsContainer) {
            return;
        }


        const rows =
            itemsContainer.querySelectorAll(
                ".order-item-form-row"
            );


        rows.forEach(
            function (row, index) {

                const indexElement =
                    row.querySelector(
                        ".order-item-form-index"
                    );


                if (indexElement) {

                    indexElement.textContent =
                        String(index + 1)
                            .padStart(2, "0");

                }

            }
        );

    }


    function attachRemoveButton(row) {

        if (!row) {
            return;
        }


        const removeButton =
            row.querySelector(
                ".order-remove-item"
            );


        if (!removeButton) {
            return;
        }


        removeButton.addEventListener(
            "click",
            function () {

                const deleteInput =
                    row.querySelector(
                        'input[name$="-DELETE"]'
                    );


                if (deleteInput) {

                    deleteInput.checked =
                        true;

                    row.style.display =
                        "none";

                } else {

                    row.remove();

                }


                updateItemIndexes();

            }
        );

    }


    if (itemsContainer) {

        itemsContainer
            .querySelectorAll(
                ".order-item-form-row"
            )
            .forEach(
                function (row) {

                    attachRemoveButton(row);

                }
            );

    }


    if (
        addItemBtn &&
        totalFormsInput &&
        emptyTemplate &&
        itemsContainer
    ) {

        addItemBtn.addEventListener(
            "click",
            function () {

                const formIndex =
                    parseInt(
                        totalFormsInput.value,
                        10
                    );


                if (Number.isNaN(formIndex)) {
                    return;
                }


                let html =
                    emptyTemplate.innerHTML.replace(
                        /__prefix__/g,
                        formIndex
                    );


                const wrapper =
                    document.createElement("div");


                wrapper.innerHTML =
                    html.trim();


                const row =
                    wrapper.firstElementChild;


                if (!row) {
                    return;
                }


                itemsContainer.appendChild(row);


                totalFormsInput.value =
                    formIndex + 1;


                attachRemoveButton(row);

                updateItemIndexes();


                const productSelect =
                    row.querySelector(
                        'select[name$="-product"]'
                    );


                if (productSelect) {

                    productSelect.focus();

                }

            }
        );

    }

});