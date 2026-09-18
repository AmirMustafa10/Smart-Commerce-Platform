document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       Small entrance animation
    ===================================================== */

    const animatedItems = document.querySelectorAll(
        ".shipper-stat-card, " +
        ".shipper-orders-card, " +
        ".shipper-quick-card, " +
        ".shipper-tip-banner"
    );

    animatedItems.forEach(function (item, index) {

        item.style.animationDelay =
            `${index * 0.05}s`;

    });


    /* =====================================================
       Button press interaction
    ===================================================== */

    document.querySelectorAll(
        ".shipper-quick-action, .shipper-view-all"
    ).forEach(function (element) {

        element.addEventListener(
            "mousedown",
            function () {
                element.style.transform =
                    "scale(0.98)";
            }
        );


        element.addEventListener(
            "mouseup",
            function () {
                element.style.transform = "";
            }
        );


        element.addEventListener(
            "mouseleave",
            function () {
                element.style.transform = "";
            }
        );

    });

});