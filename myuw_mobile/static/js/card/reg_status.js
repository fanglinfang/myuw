var RegStatusCard = {
    name: 'RegStatusCard',
    dom_target: undefined,

    render_init: function() {
        if (window.card_display_dates.is_after_start_of_registration_display_period &&
            window.card_display_dates.is_before_end_of_registration_display_period) {
            WSData.fetch_notice_data(RegStatusCard.render_upon_data,RegStatusCard.render_error);
            WSData.fetch_oquarter_data(RegStatusCard.render_upon_data, RegStatusCard.render_error);
        }
        else {
            $("#RegStatusCard").hide();
        }
    },
    render_upon_data: function() {
        //If more than one data source, multiple callbacks point to this function
        //Delay rendering until all requests are complete
        //Do something smart about not showing error if AJAX is pending
        if (!RegStatusCard._has_all_data()) {
            return;
        }
        RegStatusCard._render();
    },

    _has_all_data: function () {
        if (WSData.notice_data() && WSData.oquarter_data()) {
            return true;
        }
        return false;
    },
    render_error: function () {
        RegStatusCard.dom_target.html(CardWithError.render("Registration"));
    },

    _render_for_term: function(quarter, card) {
        var source = $("#reg_status_card").html();
        var template = Handlebars.compile(source);
        var reg_notices = Notices.get_notices_for_tag("reg_card_messages");
        var reg_holds = Notices.get_notices_for_tag("reg_card_holds");
        var reg_date = Notices.get_notices_for_tag("est_reg_date");     
        var i, j;

        // Filter estimated registration dates for summer...
        // Having this notice is being used a proxy for registration not being open yet.
        // If the notice is gone, registration is open?
        var registration_is_open = true;
        var display_reg_dates = [];
        for (i = 0; i < reg_date.length; i++) {
            var notice = reg_date[i];
            var show_notice = false;
            var registration_date = null;
            for (j = 0; j < notice.attributes.length; j++) {
                var attribute = notice.attributes[j];
                // Extract the registration date:
                if (attribute.name == "Date") {
                    registration_date = attribute.value;
                }

                if (quarter == "Summer") {
                    if ((attribute.name == "Quarter") && (attribute.value == "Summer")) {
                        show_notice = true;
                    }
                }
                else {
                    if ((attribute.name == "Quarter") && (attribute.value == quarter)) {
                        show_notice = true;
                    }
                }

                if (show_notice) {
                    display_reg_dates.push({ "notice": notice, "date": registration_date });
                    registration_is_open = false;
                }
            }
        }

        var year, has_registration, next_term_data;
        if (quarter == "Summer") {
            next_term_data = WSData.oquarter_data().next_term_data;
            var terms = WSData.oquarter_data().terms;
            year = next_term_data.year;

            for (i = 0; i < terms.length; i++) {
                var term = terms[i];
                if ((term.quarter == quarter) && term.section_count) {
                    has_registration = true;
                }
            }
        }
        else {
            next_term_data = WSData.oquarter_data().next_term_data;
            quarter = next_term_data.quarter;
            year = next_term_data.year;
            has_registration = next_term_data.has_registration;
        }

        if (has_registration) {
            return;
        }

        var all_plan_data = WSData.myplan_data(year, quarter);
        var plan_data = {};
        if (all_plan_data && all_plan_data.terms) {
            plan_data = all_plan_data.terms[0];
        }

        //Get hold count from notice attrs
        var hold_count = reg_holds.length;
        return template({"reg_notices": reg_notices,
                         "reg_holds": reg_holds,
                         "card": card,
                         "registration_is_open": registration_is_open,
                         "is_tacoma": window.user.tacoma || window.user.tacoma_affil,
                         "is_bothell": window.user.bothell || window.user.bothell_affil,
                         "is_seattle": window.user.seattle || window.user.seattle_affil,
                         "hold_count": hold_count,
                         "est_reg_date": display_reg_dates,
                         "reg_next_quarter" : quarter,
                         "reg_next_year": year,
                         "plan_data": plan_data
                         });
    },

    _add_events: function(card) {
        // show registration resources
        var id, holds_class, unready_courses;
        if (card) {
            id = "#show_reg_resources_"+card;
            holds_class = ".reg_disclosure_"+card;
            unready_courses = "#show_unready_courses_"+card;
        }
        else {
            id = "#show_reg_resources";
            holds_class = ".reg_disclosure";
            unready_courses = "#show_unready_courses";
        }

        // Prevent a closure on card
        (function(label) {
            $('body').on('click', id, function (ev) {
                var div, expose, show_expose, hide_expose;
                if (label) {
                    div = $("#reg_resources_"+label);
                    expose = $("#show_reg_resources_"+label);
                    show_expose = $("#show_reg_label_"+label).html();
                    hide_expose = $("#hide_reg_label_"+label).html();
                }
                else {
                    div = $("#reg_resources");
                    expose = $("#show_reg_resources");
                    show_expose = $("#show_reg_label").html();
                    hide_expose = $("#hide_reg_label").html();
                }

                ev.preventDefault();
                var card = $(ev.target).closest("[data-type='card']");

                div.toggleClass("slide-show");

                if (div.hasClass("slide-show")) {
                    expose.text(hide_expose);
                    div.attr('aria-hidden', 'false');
                    expose.attr('title', 'Collapse to hide additional registration resources');
                    window.myuw_log.log_card(card, "expand");
                } else {
                    div.attr('aria-hidden', 'true');
                    expose.attr('title', 'Expand to show additional registration resources');
                    window.myuw_log.log_card(card, "collapse");

                    setTimeout(function() {
                        expose.text(show_expose);
                    }, 700);
                }
            });

            // show myplan unready course details
            $('body').on('click', unready_courses, function (ev) {
                ev.preventDefault();
                var div, expose;
                if (label) {
                    div = $("#myplan_unready_courses_"+label);
                    expose = $("#show_unready_courses_"+label);
                }
                else {
                    div = $("#myplan_unready_courses");
                    expose = $("#show_unready_courses");
                }

                ev.preventDefault();
                var card = $(ev.target).closest("[data-type='card']");

                div.toggleClass("slide-show");

                if (div.hasClass("slide-show")) {
                    expose.text("Hide details");
                    div.attr('aria-hidden', 'false');
                    // expose.attr('title', '');
                } else {
                    div.attr('aria-hidden', 'true');
                    // expose.attr('title', '');

                    setTimeout(function() {
                        expose.text("See details");
                    }, 700);
                }

            });


            // show hold details
            $('body').on('click', holds_class, function (ev) {
                ev.preventDefault();
                var div, expose, hide;
                if (label) {
                    div = $("#reg_holds_"+label);
                    expose = $("#show_reg_holds_wrapper_"+label);
                    hide = $("#hide_reg_holds_wrapper_"+label);
                }
                else {
                    div = $("#reg_holds");
                    expose = $("#show_reg_holds_wrapper");
                    hide = $("#hide_reg_holds_wrapper");
                }

                div.toggleClass("slide-show");
                if (div.hasClass("slide-show")) {
                    expose.attr("hidden", true);
                    expose.attr("aria-hidden", true);
                    hide.attr("hidden", false);
                    hide.attr("aria-hidden", false);
                    div.attr("aria-hidden", false);
                    window.myuw_log.log_card("RegHolds", "expand");
                }
                else {
                    window.myuw_log.log_card("RegHolds", "collapse");
                    setTimeout(function () {
                        expose.attr("hidden", false);
                        expose.attr("aria-hidden", false);
                        hide.attr("hidden", true);
                        hide.attr("aria-hidden", true);
                        div.attr("aria-hidden", true);
                    }, 700);
                }
            });

        })(card);
    },

    _render: function () {
        var next_term_data = WSData.oquarter_data().next_term_data;
        var reg_next_quarter = next_term_data.quarter;

        if (WSData.myplan_data(next_term_data.year, next_term_data.quarter)) {
            content = RegStatusCard._render_for_term(reg_next_quarter);

            if (!content) {
                RegStatusCard.dom_target.hide();
                return;
            }

            RegStatusCard._add_events();

            RegStatusCard.dom_target.html(content);
        }
        else {
            WSData.fetch_myplan_data(next_term_data.year, next_term_data.quarter, RegStatusCard.render_upon_data,RegStatusCard.render_error);
        }
    }
};
