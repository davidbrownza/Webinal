function ErrorMessage() {
    this.error = ko.observable(false);
    this.message = ko.observable("");
}

$(function() {

    $('#side-menu').metisMenu();

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
	
	
});

var nav_hidden = false;
var footer_level = 1;

$("#max_footer").click(function() {
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

$("#min_footer").click(function() {
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

$("#min_footer").click();

/***
* SETUP AJAX CSRF TOKEN
***/

var csrftoken;

function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
		    var cookie = jQuery.trim(cookies[i]);
		    // Does this cookie string begin with the name we want?
		    if (cookie.substring(0, name.length + 1) == (name + '=')) {
		        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		        break;
		    }
		}
	}
	return cookieValue;
}
	
function csrfSafeMethod(method) {
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
		
function sameOrigin(url) {
	// test that a given url is a same-origin URL
	// url could be relative or scheme relative or absolute
	var host = document.location.host; // host + port
	var protocol = document.location.protocol;
	var sr_origin = '//' + host;
	var origin = protocol + sr_origin;
	// Allow absolute or scheme relative URLs to same origin
	return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
		(url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
		// or any other URL that isn't scheme relative or absolute i.e relative.
		!(/^(\/\/|http:|https:).*/.test(url));
}
		
function setupAjax() {
	csrftoken = getCookie('csrftoken');
	
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
				// Send the token to same-origin, relative URLs only.
				// Send the token only if the method warrants CSRF protection
				// Using the CSRFToken value acquired earlier
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});
}

setupAjax();
