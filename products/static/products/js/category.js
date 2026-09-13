document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       Alerts
    ===================================================== */

    document.querySelectorAll(".category-alert-close").forEach(function (button) {

        button.addEventListener("click", function () {

            const alert = button.closest(".category-alert");

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
       Category Search
    ===================================================== */

    const searchInput =
        document.getElementById("categorySearch");

    const rows =
        document.querySelectorAll(".category-row");

    const searchEmpty =
        document.getElementById("categorySearchEmpty");


    if (searchInput && rows.length) {

        searchInput.addEventListener("input", function () {

            const searchValue =
                this.value.trim().toLowerCase();

            let visibleCount = 0;


            rows.forEach(function (row) {

                const searchText =
                    (row.dataset.search || "").toLowerCase();

                const matches =
                    searchValue === "" ||
                    searchText.includes(searchValue);

                row.style.display =
                    matches ? "" : "none";

                if (matches) {
                    visibleCount++;
                }

            });


            if (searchEmpty) {

                if (
                    searchValue !== "" &&
                    visibleCount === 0
                ) {
                    searchEmpty.classList.add("show");
                } else {
                    searchEmpty.classList.remove("show");
                }

            }

        });

    }


    /* =====================================================
       Search Shortcut
    ===================================================== */

    if (searchInput) {

        document.addEventListener("keydown", function (event) {

            if (
                (event.ctrlKey || event.metaKey) &&
                event.key.toLowerCase() === "k"
            ) {

                event.preventDefault();

                searchInput.focus();

                searchInput.select();

            }

        });

    }


    /* =====================================================
       Delete Modal
    ===================================================== */

    const deleteModal =
        document.getElementById("categoryDeleteModal");

    const deleteForm =
        document.getElementById("categoryDeleteForm");

    const deleteName =
        document.getElementById("deleteCategoryName");

    const confirmDeleteBtn =
        document.getElementById("confirmDeleteBtn");


    function openDeleteModal(name, deleteUrl) {

        if (!deleteModal || !deleteForm) {
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


    document.querySelectorAll(".delete-category-btn").forEach(function (button) {

        button.addEventListener("click", function () {

            const name =
                button.dataset.categoryName ||
                "this category";

            const deleteUrl =
                button.dataset.deleteUrl ||
                "";


            openDeleteModal(
                name,
                deleteUrl
            );

        });

    });


    /* =====================================================
       Close Delete Modal
    ===================================================== */

    document.querySelectorAll(
        "[data-close-delete-modal]"
    ).forEach(function (element) {

        element.addEventListener("click", function () {

            closeDeleteModal();

        });

    });


    /* =====================================================
       Escape
    ===================================================== */

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {

            closeDeleteModal();

        }

    });


    /* =====================================================
       Delete Loading
    ===================================================== */

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
       Form Submit Loading
    ===================================================== */

    const categoryForm =
        document.getElementById("categoryForm");

    const categorySubmitBtn =
        document.getElementById("categorySubmitBtn");


    if (
        categoryForm &&
        categorySubmitBtn
    ) {

        categoryForm.addEventListener(
            "submit",
            function () {

                categorySubmitBtn.classList.add(
                    "is-loading"
                );

                categorySubmitBtn.disabled =
                    true;

            }
        );

    }


    /* =====================================================
       Live Preview
    ===================================================== */

    const categoryNameInput =
        document.getElementById("id_name");

    const categoryDescriptionInput =
        document.getElementById("id_description");

    const previewName =
        document.getElementById("categoryPreviewName");

    const previewDescription =
        document.getElementById(
            "categoryPreviewDescription"
        );


    function updatePreview() {

        if (
            categoryNameInput &&
            previewName
        ) {

            const value =
                categoryNameInput.value.trim();

            previewName.textContent =
                value || "New category";

        }


        if (
            categoryDescriptionInput &&
            previewDescription
        ) {

            const value =
                categoryDescriptionInput.value.trim();

            previewDescription.textContent =
                value || "Category description";

        }

    }


    if (categoryNameInput) {

        categoryNameInput.addEventListener(
            "input",
            updatePreview
        );

    }


    if (categoryDescriptionInput) {

        categoryDescriptionInput.addEventListener(
            "input",
            updatePreview
        );

    }


    updatePreview();


    /* =====================================================
       Focus Interaction
    ===================================================== */

    document.querySelectorAll(
        ".category-input-wrapper input, .category-input-wrapper textarea"
    ).forEach(function (input) {

        input.addEventListener(
            "focus",
            function () {

                const wrapper =
                    input.closest(
                        ".category-input-wrapper"
                    );


                if (wrapper) {

                    wrapper.classList.add(
                        "is-focused"
                    );

                }

            }
        );


        input.addEventListener(
            "blur",
            function () {

                const wrapper =
                    input.closest(
                        ".category-input-wrapper"
                    );


                if (wrapper) {

                    wrapper.classList.remove(
                        "is-focused"
                    );

                }

            }
        );

    });


    /* =====================================================
       Button Press Effect
    ===================================================== */

    document.querySelectorAll(
        ".category-btn, .category-action-btn, .category-mobile-edit, .category-mobile-delete"
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

});