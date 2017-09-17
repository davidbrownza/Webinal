$(function() {

    $('#side-menu').metisMenu();

});

var nav_hidden = false;
var footer_level = 1;

//Loads the correct sidebar on window load,
//collapses the sidebar on window resize.
// Sets the min-height of #page-wrapper to window size
$(function() {
    $(window).bind("load resize", function() {
        topOffset = 50;
        width = (this.window.innerWidth > 0) ? this.window.innerWidth : this.screen.width;
        if (width < 768) {
            $('div.navbar-collapse').addClass('collapse');
            topOffset = 100; // 2-row-menu
        } else {
            $('div.navbar-collapse').removeClass('collapse');
        }

        height = (this.window.innerHeight > 0) ? this.window.innerHeight : this.screen.height;
        height = height - topOffset;
        if (height < 1) height = 1;
        if (height > topOffset) {
            $("#page-wrapper").css("min-height", (height) + "px");
        }
    });
	
	$("#hide-nav").bind("click", function() {
		if(nav_hidden) {
			$("#nav-wrapper").removeClass("nav-hidden");
			$("#page").removeClass("full-page");
			$("#page").addClass("part-page");
			nav_hidden = false;
		} else {
			$("#nav-wrapper").addClass("nav-hidden");
			$("#page").addClass("full-page");
			$("#page").removeClass("part-page");
			nav_hidden = true;
		}
	});
	
	$("#max_footer").bind("click", function() {
		if(footer_level < 2) {
			footer_level++;
			if(footer_level == 2) {
				$("#footer").removeClass("level_1");
				$("#footer").addClass("level_2");
			} else if (footer_level == 1) {
				$("#footer").removeClass("level_0");
				$("#page-container").removeClass("page-container_0");
				
				$("#page-container").addClass("page-container_1");
				$("#footer").addClass("level_1");
			} 
		}
	});
	
	$("#min_footer").bind("click", function() {
		if(footer_level > 0) {
			footer_level--;
			if(footer_level == 0) {
				$("#footer").removeClass("level_1");
				$("#page-container").removeClass("page-container_1");
				
				$("#page-container").addClass("page-container_0");
				$("#footer").addClass("level_0");
			} else if (footer_level == 1) {
				$("#footer").removeClass("level_2");
				$("#footer").addClass("level_1");
			}
		}
	});
});
