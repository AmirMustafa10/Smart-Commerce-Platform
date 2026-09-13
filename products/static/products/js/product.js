document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       HELPERS
    ========================================================= */

    function qs(selector, parent = document) {
        return parent.querySelector(selector);
    }

    function qsa(selector, parent = document) {
        return parent.querySelectorAll(selector);
    }


    /* =========================================================
       ALERTS
    ========================================================= */

    qsa(".product-alert-close").forEach(function (button) {

        button.addEventListener("click", function () {

            const alert =
                button.closest(".product-alert");

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


    /* =========================================================
       SEARCH
    ========================================================= */

    const searchInput =
        qs("#productSearch");

    const rows =
        qsa(".product-row");

    const searchEmpty =
        qs("#productSearchEmpty");


    function filterProducts(value) {

        const searchValue =
            value
                .trim()
                .toLowerCase();

        let visibleCount = 0;


        rows.forEach(function (row) {

            const text =
                (row.dataset.search || "")
                    .replace(/\s+/g, " ")
                    .toLowerCase();


            const matches =
                searchValue === "" ||
                text.includes(searchValue);


            row.style.display =
                matches ? "" : "none";


            if (matches) {
                visibleCount++;
            }

        });


        if (!searchEmpty) {
            return;
        }


        if (
            searchValue !== "" &&
            visibleCount === 0
        ) {

            searchEmpty.classList.add("show");

        } else {

            searchEmpty.classList.remove("show");

        }

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {
                filterProducts(this.value);
            }
        );

    }


    /* =========================================================
       SEARCH SHORTCUT
       Ctrl + K / Cmd + K
    ========================================================= */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                (event.ctrlKey || event.metaKey) &&
                event.key.toLowerCase() === "k"
            ) {

                if (!searchInput) {
                    return;
                }

                event.preventDefault();

                searchInput.focus();
                searchInput.select();

            }

        }
    );


    /* =========================================================
       DELETE MODAL
    ========================================================= */

    const deleteModal =
        qs("#productDeleteModal");

    const deleteForm =
        qs("#productDeleteForm");

    const deleteProductName =
        qs("#deleteProductName");

    const confirmDeleteButton =
        qs("#confirmProductDeleteBtn");


    function openDeleteModal(
        productName,
        deleteUrl
    ) {

        if (
            !deleteModal ||
            !deleteForm
        ) {
            return;
        }


        if (deleteProductName) {

            deleteProductName.textContent =
                productName ||
                "this product";

        }


        deleteForm.action =
            deleteUrl || "";


        deleteModal.classList.add("show");

        deleteModal.setAttribute(
            "aria-hidden",
            "false"
        );


        document.body.style.overflow =
            "hidden";


        setTimeout(function () {

            if (confirmDeleteButton) {
                confirmDeleteButton.focus();
            }

        }, 100);

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


    qsa(".delete-product-btn").forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const productName =
                        button.dataset.productName ||
                        "this product";


                    const deleteUrl =
                        button.dataset.deleteUrl ||
                        "";


                    openDeleteModal(
                        productName,
                        deleteUrl
                    );

                }
            );

        }
    );


    qsa("[data-close-product-modal]").forEach(
        function (element) {

            element.addEventListener(
                "click",
                function () {
                    closeDeleteModal();
                }
            );

        }
    );


    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                deleteModal &&
                deleteModal.classList.contains("show")
            ) {

                closeDeleteModal();

            }

        }
    );


    /* =========================================================
       DELETE SUBMIT
    ========================================================= */

    if (
        deleteForm &&
        confirmDeleteButton
    ) {

        deleteForm.addEventListener(
            "submit",
            function () {

                confirmDeleteButton.classList.add(
                    "is-loading"
                );

                confirmDeleteButton.disabled =
                    true;

            }
        );

    }


    /* =========================================================
       FORM SUBMIT
    ========================================================= */

    const productForm =
        qs("#productForm");

    const productSubmitButton =
        qs("#productSubmitBtn");


    if (
        productForm &&
        productSubmitButton
    ) {

        productForm.addEventListener(
            "submit",
            function () {

                if (
                    !productForm.checkValidity()
                ) {
                    return;
                }


                productSubmitButton.classList.add(
                    "loading"
                );

                productSubmitButton.disabled =
                    true;

            }
        );

    }


    /* =========================================================
       FORM INPUTS
    ========================================================= */

    const nameInput =
        qs("#id_name");

    const categoryInput =
        qs("#id_category");

    const skuInput =
        qs("#id_sku");

    const priceInput =
        qs("#id_price");

    const discountInput =
        qs("#id_discount_price");

    const stockInput =
        qs("#id_stock_quantity");


    /* =========================================================
       PREVIEW ELEMENTS
    ========================================================= */

    const previewName =
        qs("#productPreviewName");

    const previewCategory =
        qs("#productPreviewCategory");

    const previewSku =
        qs("#productPreviewSku");

    const previewPrice =
        qs("#productPreviewPrice");

    const previewOldPrice =
        qs("#productPreviewOldPrice");

    const previewStock =
        qs("#productPreviewStock");

    const stockCounter =
        qs("#stockCounter");


    /* =========================================================
       CATEGORY TEXT
    ========================================================= */

    function getCategoryText() {

        if (!categoryInput) {
            return "";
        }


        if (
            categoryInput.tagName.toLowerCase() ===
            "select"
        ) {

            const option =
                categoryInput.options[
                    categoryInput.selectedIndex
                ];


            if (
                option &&
                option.value
            ) {

                return option.text.trim();

            }

        }


        return categoryInput.value
            ? categoryInput.value.trim()
            : "";

    }


    /* =========================================================
       MONEY
    ========================================================= */

    function formatMoney(value) {

        const number =
            parseFloat(
                String(value)
                    .replace(/,/g, "")
                    .trim()
            );


        if (
            Number.isNaN(number)
        ) {

            return "0.00";

        }


        return number.toFixed(2);

    }


    /* =========================================================
       STOCK
    ========================================================= */

    function formatStock(value) {

        const number =
            parseInt(
                String(value)
                    .replace(/[^\d-]/g, ""),
                10
            );


        if (
            Number.isNaN(number)
        ) {

            return "0";

        }


        return String(
            Math.max(number, 0)
        );

    }


    /* =========================================================
       LIVE PREVIEW
    ========================================================= */

    function updatePreview() {

        /* Product name */

        if (previewName) {

            const value =
                nameInput
                    ? nameInput.value.trim()
                    : "";


            previewName.textContent =
                value || "New product";

        }


        /* Category */

        if (previewCategory) {

            const category =
                getCategoryText();


            previewCategory.textContent =
                category || "Uncategorized";

        }


        /* SKU */

        if (previewSku) {

            const sku =
                skuInput
                    ? skuInput.value.trim()
                    : "";


            previewSku.textContent =
                sku
                    ? `SKU: ${sku}`
                    : "SKU: —";

        }


        /* Price */

        if (previewPrice) {

            const price =
                priceInput
                    ? priceInput.value
                    : "";


            previewPrice.textContent =
                formatMoney(price);

        }


        /* Old price */

        if (previewOldPrice) {

            const price =
                priceInput
                    ? priceInput.value
                    : "";

            const discount =
                discountInput
                    ? discountInput.value
                    : "";


            if (
                price.trim() !== "" &&
                discount.trim() !== ""
            ) {

                previewOldPrice.textContent =
                    formatMoney(price);

            } else {

                previewOldPrice.textContent =
                    "—";

            }

        }


        /* Stock */

        if (previewStock) {

            const stock =
                stockInput
                    ? formatStock(
                        stockInput.value
                    )
                    : "0";


            previewStock.textContent =
                `Stock: ${stock}`;

        }


        /* Counter */

        if (stockCounter) {

            const stock =
                stockInput
                    ? formatStock(
                        stockInput.value
                    )
                    : "0";


            stockCounter.textContent =
                stock;

        }

    }


    /* =========================================================
       PREVIEW EVENTS
    ========================================================= */

    [
        nameInput,
        categoryInput,
        skuInput,
        priceInput,
        discountInput,
        stockInput
    ].forEach(function (input) {

        if (!input) {
            return;
        }


        input.addEventListener(
            "input",
            updatePreview
        );


        input.addEventListener(
            "change",
            updatePreview
        );

    });


    updatePreview();


    /* =========================================================
       FIELD FOCUS
    ========================================================= */

    qsa(
        ".product-field input, " +
        ".product-field select, " +
        ".product-field textarea, " +
        ".product-stock-form-content input"
    ).forEach(function (field) {

        field.addEventListener(
            "focus",
            function () {

                const wrapper =
                    field.closest(
                        ".product-field, " +
                        ".product-stock-form-content"
                    );


                if (wrapper) {

                    wrapper.classList.add(
                        "is-focused"
                    );

                }

            }
        );


        field.addEventListener(
            "blur",
            function () {

                const wrapper =
                    field.closest(
                        ".product-field, " +
                        ".product-stock-form-content"
                    );


                if (wrapper) {

                    wrapper.classList.remove(
                        "is-focused"
                    );

                }

            }
        );

    });


    /* =========================================================
       ESCAPE MODAL
    ========================================================= */

    if (deleteModal) {

        deleteModal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target ===
                    deleteModal
                ) {

                    closeDeleteModal();

                }

            }
        );

    }


    /* =========================================================
       BUTTON PRESS EFFECT
    ========================================================= */

    qsa(
        ".product-add-btn, " +
        ".product-toolbar-add, " +
        ".product-empty-btn, " +
        ".product-form-submit, " +
        ".product-delete-confirm, " +
        ".product-delete-cancel"
    ).forEach(function (button) {

        button.addEventListener(
            "mousedown",
            function () {

                if (button.disabled) {
                    return;
                }

                button.style.transform =
                    "translateY(0) scale(0.985)";

            }
        );


        button.addEventListener(
            "mouseup",
            function () {

                button.style.transform =
                    "";

            }
        );


        button.addEventListener(
            "mouseleave",
            function () {

                button.style.transform =
                    "";

            }
        );

    });


    /* =========================================================
       INITIAL REVEAL
    ========================================================= */

    const revealItems =
        qsa(
            ".product-stat-card, " +
            ".product-card, " +
            ".product-info-banner"
        );


    revealItems.forEach(
        function (element, index) {

            element.style.opacity =
                "0";

            element.style.transform =
                "translateY(7px)";


            setTimeout(
                function () {

                    element.style.transition =
                        "opacity .35s ease, " +
                        "transform .35s ease";

                    element.style.opacity =
                        "1";

                    element.style.transform =
                        "translateY(0)";

                },
                55 + (index * 55)
            );

        }
    );

});