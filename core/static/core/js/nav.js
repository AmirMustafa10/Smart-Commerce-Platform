document.addEventListener("DOMContentLoaded", () => {

    const navbar =
        document.querySelector(".wf-navbar");

    if (!navbar) {
        return;
    }


    /* =====================================================
       NAVBAR SCROLL EFFECT
    ===================================================== */

    const updateNavbar = () => {

        if (window.scrollY > 12) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }

    };


    updateNavbar();

    window.addEventListener(
        "scroll",
        updateNavbar,
        {
            passive: true
        }
    );


    /* =====================================================
       CLOSE MOBILE MENU AFTER CLICK
    ===================================================== */

    const mobileMenu =
        document.getElementById("wfMobileMenu");

    if (mobileMenu) {

        const links =
            mobileMenu.querySelectorAll("a");

        links.forEach((link) => {

            link.addEventListener("click", () => {

                const collapse =
                    bootstrap.Collapse
                        .getInstance(mobileMenu);

                if (collapse) {
                    collapse.hide();
                }

            });

        });

    }

});