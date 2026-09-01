document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       ALERTS
    ===================================================== */

    const alertButtons =
        document.querySelectorAll(".team-alert-close");

    alertButtons.forEach((button) => {

        button.addEventListener("click", () => {

            const alert =
                button.closest(".team-alert");

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
       TEAM SEARCH
    ===================================================== */

    const searchInput =
        document.getElementById("shipperSearch");

    const desktopRows =
        document.querySelectorAll(
            "#shipperTableBody .shipper-row"
        );

    const mobileRows =
        document.querySelectorAll(
            "#shipperMobileList .shipper-row"
        );

    const emptyState =
        document.getElementById("searchEmpty");

    const visibleCount =
        document.getElementById("visibleMembersCount");


    if (searchInput) {

        searchInput.addEventListener("input", () => {

            const query =
                searchInput.value
                    .trim()
                    .toLowerCase();

            let visible = 0;


            const filterRows = (rows) => {

                rows.forEach((row) => {

                    const searchable =
                        row.dataset.search || "";

                    const matches =
                        searchable.includes(query);

                    row.style.display =
                        matches ? "" : "none";

                    if (matches) {
                        visible++;
                    }

                });

            };


            /*
             * Desktop and mobile are separate representations
             * of the same members. Count only once using desktop
             * rows when available.
             */

            if (desktopRows.length) {

                desktopRows.forEach((row) => {

                    const searchable =
                        row.dataset.search || "";

                    const matches =
                        searchable.includes(query);

                    row.style.display =
                        matches ? "" : "none";

                });


                visible =
                    Array.from(desktopRows)
                        .filter((row) => {
                            return row.style.display !== "none";
                        })
                        .length;


                mobileRows.forEach((row) => {

                    const searchable =
                        row.dataset.search || "";

                    row.style.display =
                        searchable.includes(query)
                            ? ""
                            : "none";

                });

            } else {

                filterRows(mobileRows);

            }


            if (visibleCount) {
                visibleCount.textContent = visible;
            }


            if (emptyState) {

                emptyState.classList.toggle(
                    "d-none",
                    visible > 0
                );

            }

        });

    }


    /* =====================================================
       CREATE FORM
    ===================================================== */

    const createForm =
        document.getElementById(
            "shipperCreateForm"
        );

    const createButton =
        document.getElementById(
            "createShipperSubmit"
        );


    if (createForm && createButton) {

        createForm.addEventListener(
            "submit",
            (event) => {

                /*
                 * Let browser validation work before
                 * activating loading state.
                 */

                if (!createForm.checkValidity()) {

                    event.preventDefault();

                    createForm.classList.add(
                        "was-validated"
                    );

                    return;

                }


                createButton.classList.add(
                    "loading"
                );

                createButton.disabled = true;

            }
        );

    }


    /* =====================================================
       PASSWORD TOGGLE
    ===================================================== */

    const passwordInputs =
        document.querySelectorAll(
            '#shipperCreateForm input[type="password"]'
        );


    passwordInputs.forEach((input) => {

        const wrapper =
            input.parentElement;

        if (!wrapper) {
            return;
        }


        wrapper.style.position =
            "relative";


        input.style.paddingRight =
            "42px";


        const toggle =
            document.createElement("button");


        toggle.type = "button";

        toggle.className =
            "password-toggle";


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
       FORM FIELD MICRO INTERACTION
    ===================================================== */

    const formFields =
        document.querySelectorAll(
            ".shipper-create-form .form-control"
        );


    formFields.forEach((field) => {

        field.addEventListener("focus", () => {

            const wrapper =
                field.closest(".mb-3");

            if (wrapper) {
                wrapper.style.transform =
                    "translateY(-1px)";
                wrapper.style.transition =
                    "transform .2s ease";
            }

        });


        field.addEventListener("blur", () => {

            const wrapper =
                field.closest(".mb-3");

            if (wrapper) {
                wrapper.style.transform =
                    "translateY(0)";
            }

        });

    });

});