var GradeCard = {
    name: 'GradeCard',
    dom_target: undefined,
    term: null,

    render_init: function() {
        GradeCard.term = null;
        if (window.card_display_dates.is_after_last_day_of_classes) {
            GradeCard.term = 'current';
        }
        else if (window.card_display_dates.is_before_first_day_of_term) {
            // Fetch previous term's data...
            GradeCard.term = window.card_display_dates.last_term;
        }

        if (GradeCard.term) {
            WSData.fetch_course_data_for_term(GradeCard.term, GradeCard.render_upon_data, GradeCard.render_error);
        }
        else {
            GradeCard.dom_target.hide();
        }
    },

    render_upon_data: function() {
        if (!GradeCard._has_all_data()) {
            return;
        }
        GradeCard._render();
    },

    render_error: function() {
        var course_error_code = WSData.course_data_error_code();
        if (course_error_code === null || course_error_code === 404) {
            $("#GradeCard").hide();
            return;
        }
        GradeCard.dom_target.html(CardWithError.render("Final Grades"));
    },

    _has_all_data: function () {
        if (WSData.normalized_course_data(GradeCard.term)) {
            return true;
        }
        return false;
    },

    _render: function () {
        var term = GradeCard.term;
        var course_data = WSData.normalized_course_data(term);
        var has_section_to_display = false;
        course_data.display_grade_card = true;
        course_data.display_grades = true;
        course_data.display_note = true;
        if (course_data.sections.length === 0) {
            course_data.display_grade_card = false;
        }
        if (window.card_display_dates.is_after_grade_submission_deadline) {
            course_data.display_note = false;
        }
        var index;
        for (index = 0; index < course_data.sections.length; index += 1) {
            if (course_data.sections[index].is_primary_section && !course_data.sections[index].is_auditor) {
                course_data.sections[index].display_grade = true;
                has_section_to_display = true;
            } else {
                course_data.sections[index].display_grade = false;
            }

            if (course_data.sections[index].grade === 'X') {
                course_data.sections[index].no_grade = true;
            } else {
                course_data.sections[index].no_grade = false;
            }
        }
        if (!has_section_to_display) {
            course_data.display_grade_card = false;
        }

        var source = $("#grade_card_content").html();
        var grades_template = Handlebars.compile(source);
        GradeCard.dom_target.html(grades_template(course_data));
        GradeCard.add_events(term);
    },

    add_events: function(term) {
        $(".toggle_grade_card_resources").on("click", function(ev) {
            ev.preventDefault();
            var card = $(ev.target).closest("[data-type='card']");
            var div = $("#grade_card_resources");
            var expose = $("#show_grade_resources_wrapper");
            var hide = $("#hide_grade_resources_wrapper");

            if (div.css('display') == 'none') {
                div.show();
                div.attr("hidden", false);
                // Without this timeout, the animation doesn't happen - the block just appears.
                window.setTimeout(function() {
                    div.toggleClass("slide-show");
                    expose.attr("hidden", true);
                    expose.attr("aria-hidden", true);
                    hide.attr("hidden", false);
                    hide.attr("aria-hidden", false);

                    div.attr("aria-expanded", true);
                    div.focus();
                }, 0);

                window.myuw_log.log_card(card, "expand");
            }
            else {
                div.toggleClass("slide-show");
                window.myuw_log.log_card(card, "collapse");

                setTimeout(function() {
                    expose.attr("hidden", false);
                    expose.attr("aria-hidden", false);
                    hide.attr("hidden", true);
                    hide.attr("aria-hidden", true);
                    div.attr("aria-expanded", false);
                    div.attr("hidden", true);
                    div.hide();
                }, 700);
            }
        });

    },
};
