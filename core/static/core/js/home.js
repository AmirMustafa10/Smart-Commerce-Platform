document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       SCROLL REVEAL
    ===================================================== */

    const revealElements = document.querySelectorAll(".reveal");

    if ("IntersectionObserver" in window) {

        const observer = new IntersectionObserver(
            (entries, obs) => {

                entries.forEach((entry) => {

                    if (!entry.isIntersecting) {
                        return;
                    }

                    entry.target.classList.add("show");

                    obs.unobserve(entry.target);

                });

            },
            {
                threshold: 0.12,
                rootMargin: "0px 0px -40px 0px"
            }
        );

        revealElements.forEach((element) => {
            observer.observe(element);
        });

    } else {

        revealElements.forEach((element) => {
            element.classList.add("show");
        });

    }


    /* =====================================================
       COUNTER ANIMATION
    ===================================================== */

    const counters = document.querySelectorAll(".counter");

    const animateCounter = (element) => {

        const target = Number(element.dataset.value);

        if (!Number.isFinite(target)) {
            return;
        }

        const duration = 1400;
        const startTime = performance.now();

        const update = (currentTime) => {

            const elapsed = currentTime - startTime;

            const progress = Math.min(
                elapsed / duration,
                1
            );

            /*
             * Ease-out cubic
             */
            const eased =
                1 - Math.pow(1 - progress, 3);

            const value =
                Math.floor(target * eased);

            element.textContent =
                value.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(update);
            }

        };

        requestAnimationFrame(update);
    };


    if ("IntersectionObserver" in window) {

        const counterObserver =
            new IntersectionObserver(
                (entries, observer) => {

                    entries.forEach((entry) => {

                        if (!entry.isIntersecting) {
                            return;
                        }

                        animateCounter(entry.target);

                        observer.unobserve(entry.target);

                    });

                },
                {
                    threshold: .6
                }
            );

        counters.forEach((counter) => {
            counterObserver.observe(counter);
        });

    } else {

        counters.forEach((counter) => {
            animateCounter(counter);
        });

    }


    /* =====================================================
       PRODUCT MOCKUP PARALLAX
    ===================================================== */

    const preview =
        document.getElementById("productPreview");

    const productWrap =
        document.querySelector(".hero-product-wrap");

    const supportsFinePointer =
        window.matchMedia(
            "(pointer: fine)"
        ).matches;


    if (preview && productWrap && supportsFinePointer) {

        productWrap.addEventListener("mousemove", (event) => {

            const rect =
                productWrap.getBoundingClientRect();

            const x =
                event.clientX - rect.left;

            const y =
                event.clientY - rect.top;

            const rotateX =
                ((y / rect.height) - .5) * -5;

            const rotateY =
                ((x / rect.width) - .5) * 7;

            preview.style.transform = `
                rotateX(${rotateX}deg)
                rotateY(${rotateY}deg)
                translateY(-7px)
            `;

        });

        productWrap.addEventListener("mouseleave", () => {

            preview.style.transform = `
                rotateY(-5deg)
                rotateX(2deg)
            `;

        });

    }


    /* =====================================================
       CHART TOOLTIP
    ===================================================== */

    const bars =
        document.querySelectorAll(".chart-bar");

    bars.forEach((bar) => {

        const day = bar.dataset.day;

        if (!day) {
            return;
        }

        bar.addEventListener("mouseenter", () => {

            bar.setAttribute(
                "data-tooltip",
                day
            );

        });

    });


    /* =====================================================
       NOTIFICATION INTERACTION
    ===================================================== */

    const notificationBtn =
        document.querySelector(".notification-btn");

    if (notificationBtn) {

        notificationBtn.addEventListener(
            "click",
            () => {

                const badge =
                    notificationBtn.querySelector(
                        ".notification-badge"
                    );

                if (badge) {

                    badge.textContent = "0";

                    badge.style.transform =
                        "scale(0)";

                    setTimeout(() => {

                        badge.style.display =
                            "none";

                    }, 200);

                }

            }
        );

    }


    /* =====================================================
       QUICK ACTION FEEDBACK
    ===================================================== */

    const quickActions =
        document.querySelectorAll(".quick-action");

    quickActions.forEach((action) => {

        action.addEventListener("mouseenter", () => {

            const icon =
                action.querySelector(
                    ".quick-action-icon"
                );

            if (icon) {
                icon.style.transform =
                    "scale(1.08)";
            }

        });

        action.addEventListener("mouseleave", () => {

            const icon =
                action.querySelector(
                    ".quick-action-icon"
                );

            if (icon) {
                icon.style.transform =
                    "scale(1)";
            }

        });

    });


    /* =====================================================
       BUTTON RIPPLE
    ===================================================== */

    const rippleTargets =
        document.querySelectorAll(
            ".btn-wa-green, .btn-hero-secondary"
        );

    rippleTargets.forEach((button) => {

        button.style.position = "relative";
        button.style.overflow = "hidden";

        button.addEventListener("click", (event) => {

            const rect =
                button.getBoundingClientRect();

            const ripple =
                document.createElement("span");

            const size =
                Math.max(
                    rect.width,
                    rect.height
                );

            const x =
                event.clientX -
                rect.left -
                size / 2;

            const y =
                event.clientY -
                rect.top -
                size / 2;

            ripple.style.position = "absolute";
            ripple.style.width = `${size}px`;
            ripple.style.height = `${size}px`;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            ripple.style.borderRadius = "50%";
            ripple.style.background =
                "rgba(255,255,255,.25)";
            ripple.style.pointerEvents = "none";
            ripple.style.transform = "scale(0)";
            ripple.style.transition =
                "transform .55s ease, opacity .55s ease";

            button.appendChild(ripple);

            requestAnimationFrame(() => {

                ripple.style.transform =
                    "scale(2)";

                ripple.style.opacity = "0";

            });

            setTimeout(() => {

                ripple.remove();

            }, 600);

        });

    });


    /* =====================================================
       STATUS LIVE EFFECT
    ===================================================== */

    const liveElements =
        document.querySelectorAll(
            ".automation-live"
        );

    liveElements.forEach((element, index) => {

        setTimeout(() => {

            element.animate(
                [
                    {
                        opacity: .4,
                        transform: "scale(.9)"
                    },
                    {
                        opacity: 1,
                        transform: "scale(1)"
                    }
                ],
                {
                    duration: 450,
                    easing: "ease-out"
                }
            );

        }, index * 180);

    });


    /* =====================================================
       REDUCE MOTION SUPPORT
    ===================================================== */

    const prefersReducedMotion =
        window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;

    if (prefersReducedMotion) {

        document
            .querySelectorAll(".reveal")
            .forEach((element) => {

                element.classList.add("show");

            });

        if (preview) {

            preview.style.transform = "none";

            if (productWrap) {

                productWrap.onmousemove =
                    null;

            }

        }

    }

});