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

    const searchInput = document.getElementById("team_membersSearch");

    const desktopRows = document.querySelectorAll(
      "#team_membersTableBody .team_members-row",
    );

    const mobileRows = document.querySelectorAll(
      "#team_membersMobileList .team_members-row",
    );

    const emptyState =
        document.getElementById("searchEmpty");

    const visibleCount =
        document.getElementById(
            "visibleMembersCount"
        );


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            () => {

                const query =
                    searchInput.value
                        .trim()
                        .toLowerCase();


                let visible = 0;


                desktopRows.forEach((row) => {

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


                mobileRows.forEach((row) => {

                    const searchable =
                        row.dataset.search || "";

                    row.style.display =
                        searchable.includes(query)
                            ? ""
                            : "none";

                });


                if (visibleCount) {
                    visibleCount.textContent =
                        visible;
                }


                if (emptyState) {

                    emptyState.classList.toggle(
                        "d-none",
                        visible > 0
                    );

                }

            }
        );

    }


    /* =====================================================
       ROLE SELECTOR
    ===================================================== */

    const roleCards =
        document.querySelectorAll(
            ".team-role-card"
        );

    const selectedRole =
        document.getElementById(
            "selectedRole"
        );


    roleCards.forEach((card) => {

        card.addEventListener(
            "click",
            () => {

                roleCards.forEach((item) => {

                    item.classList.remove(
                        "active"
                    );

                    item.setAttribute(
                        "aria-selected",
                        "false"
                    );

                });


                card.classList.add(
                    "active"
                );

                card.setAttribute(
                    "aria-selected",
                    "true"
                );


                const role =
                    card.dataset.role;


                if (selectedRole && role) {
                    selectedRole.value = role;
                }


                /*
                 * Small visual feedback.
                 */

                card.animate(
                    [
                        {
                            transform: "scale(.985)"
                        },
                        {
                            transform: "scale(1)"
                        }
                    ],
                    {
                        duration: 180,
                        easing: "ease-out"
                    }
                );

            }
        );

    });


    /* =====================================================
       CREATE FORM
    ===================================================== */

    const createForm =
        document.getElementById(
            "shipperCreateForm"
        );

    const createButton = document.getElementById("createteam_membersSubmit");


    if (createForm && createButton) {

        createForm.addEventListener(
            "submit",
            (event) => {

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
            input.closest(".mb-3") ||
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

        field.addEventListener(
            "focus",
            () => {

                const wrapper =
                    field.closest(".mb-3");

                if (wrapper) {

                    wrapper.style.transform =
                        "translateY(-1px)";

                    wrapper.style.transition =
                        "transform .2s ease";

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


    /* =====================================================
       DEFAULT ROLE
    ===================================================== */

    const defaultRole =
        document.querySelector(
            '.team-role-card[data-role="SHIPPER"]'
        );

    if (defaultRole) {

        defaultRole.setAttribute(
            "aria-selected",
            "true"
        );

    }

});