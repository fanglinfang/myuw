var VisualScheduleCard = {
    // This is the height of the days bar... needed for positioning math below
    day_label_offset: 0,

    // The course_index will be given when a modal is shown.
    render: function(course_data, term, course_index) {
        VisualScheduleCard.shown_am_marker = false;
        Modal.hide();
        var visual_data = {
            total_sections: course_data.sections.length,
            year: course_data.year, 
            quarter: course_data.quarter,
            term: term,
            summer_term: course_data.summer_term,
            latest_ending: 0,
            earliest_start: 24*60,
            monday: [],
            tuesday: [],
            wednesday: [],
            thursday: [],
            friday: [],
            saturday: [],
            display_hours: [],
            has_6_days: false,
            courses_meeting_tbd: []
        };

        var index = 0;
        for (index = 0; index < course_data.sections.length; index++) {
            var section = course_data.sections[index];

            var meeting_index = 0;
            for (meeting_index = 0; meeting_index < section.meetings.length; meeting_index++) {
                var meeting = section.meetings[meeting_index];
                if (!meeting.days_tbd) {

                    var start_parts = meeting.start_time.split(":");
                    var start_minutes = parseInt(start_parts[0], 10) * 60 + parseInt(start_parts[1], 10);


                    var end_parts = meeting.end_time.split(":");
                    var end_minutes = parseInt(end_parts[0], 10) * 60 + parseInt(end_parts[1], 10);

                    if (start_minutes < visual_data.earliest_start) {
                        visual_data.earliest_start = start_minutes;
                    }
                    if (end_minutes > visual_data.latest_ending) {
                        visual_data.latest_ending = end_minutes;
                    }

                    var meeting_info = {
                        start: start_minutes,
                        end: end_minutes,
                        color_id: section.color_id,
                        curriculum: section.curriculum_abbr,
                        course_number: section.course_number,
                        section_id: section.section_id,
                        section_index: index,
                        building_tbd: meeting.building_tbd,
                        building: meeting.building,
                        building_name: meeting.building_name,
                        room_tbd: meeting.room_tbd,
                        room: meeting.room,
                        latitude: meeting.latitude,
                        longitude: meeting.longitude
                    };

                    var days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
                    var day_index = 0;
                    for (day_index = 0; day_index < days.length; day_index++) {
                        var day = days[day_index];

                        if (meeting.meeting_days[day]) {
                            if (day === "saturday") {
                                visual_data.has_6_days = true;
                            }
                            meeting_info.term = term;
                            visual_data[day].push(meeting_info);
                        }
                    }
                }
                else {
                    visual_data["courses_meeting_tbd"].push({
                        color_id: section.color_id,
                        curriculum: section.curriculum_abbr,
                        course_number: section.course_number,
                        section_id: section.section_id,
                        section_index: index
                    });
                }
            }
        }

        // Make it so the start and end times are always on the hour:
        var start_hour = parseInt(visual_data.earliest_start / 60, 10);
        if ((start_hour * 60) === visual_data.earliest_start) {
            visual_data.start_time = (start_hour * 60) - 60;
        }
        else {
            visual_data.start_time = (start_hour * 60);
        }

        var end_hour = parseInt(visual_data.latest_ending / 60, 10) + 1;
        if ((end_hour * 60) === visual_data.latest_ending) {
            visual_data.end_time = (end_hour * 60) - 60;
        }
        else {
            visual_data.end_time = (end_hour * 60);
        }

        var i = 0;
        // We don't want to add the last hour - it's just off the end of the visual schedule
        for (i = visual_data.start_time; i <= visual_data.end_time - 1; i += 60) {
            visual_data.display_hours.push({
                hour: (i / 60),
                position: i
            });
        }

        visual_data.total_hours = (visual_data.end_time - visual_data.start_time) / 60;

        var hours_count = parseInt((visual_data.end_time - visual_data.start_time) / 60, 0);
        if (hours_count <= 6) {
            visual_data.schedule_hours_class = "six-hour";
        }
        else if (hours_count <= 12) {
            visual_data.schedule_hours_class = "twelve-hour";
        }
        else {
            visual_data.schedule_hours_class = "twelve-plus";
        }

        source   = $("#visual_schedule_card_content").html();
        template = Handlebars.compile(source);
        return template(visual_data);
    },


    render_init: function(term, course_index) {
        var course_data =  WSData.normalized_course_data(term);
        if (course_data === undefined) {
            return CardLoading.render("Visual Schedule");
        } else {
            if (course_data.sections.length == 0) {
                return NoCourse.render("this quarter");
            }
            
            var html_content = VisualScheduleCard.render(course_data, 
                                                         term, 
                                                         course_index);
            VisualScheduleCard.add_events(term);
            return html_content;
        }
    },

    render_upon_data: function(term, course_index) {
        var course_data =  WSData.normalized_course_data(term);
        var html_content;
        if (course_data.sections.length == 0) {
            html_content = NoCourse.render("this quarter");
        } else {
            html_content = VisualScheduleCard.render(course_data,
                                                     term, 
                                                     course_index);
        }
        $("#visual_schedule_card").html(html_content);
        if (course_data.sections.length > 0) {
            VisualScheduleCard.add_events(term);
        }
    },
            
    add_events: function(term) {
        $(".show_section_details").bind("click", function(ev) {
            var course_id = this.rel;
            var log_course_id = ev.currentTarget.getAttribute("class").replace(/[^a-z0-9]/gi, '_');
            WSData.log_interaction("open_modal_"+log_course_id, term);
            var hist = window.History;
            if (term) {
                hist.pushState({
                    state: "visual",
                    course_index: course_id,
                    term: term
                },  "", "/mobile/visual/"+term+"/"+course_id);
            }
            else {
                hist.pushState({
                    state: "visual",
                    course_index: course_id,
                },  "", "/mobile/visual/"+course_id);
            }
            CourseModal.show_course_modal(term, course_id);

            return false;
        });
        
        $(".show_map").on("click", function(ev) {
            var course_id = ev.currentTarget.getAttribute("rel");
            course_id = course_id.replace(/[^a-z0-9]/gi, '_');
            var building = ev.currentTarget.getAttribute("rel");
            building = building.replace(/[^a-z0-9]/gi, '_');
            WSData.log_interaction("show_map_from_visual_card_"+building, term);
        });
    },
};