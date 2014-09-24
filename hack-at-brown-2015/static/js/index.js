$(document).ready(function() {
	
	var $signUpForUpdatesForm = $("#sign-up-for-updates");
	$signUpForUpdatesForm.submit(function(e) {
		e.preventDefault();
		$signUpForUpdatesForm.addClass('loading');
		$.ajax({
			url: $signUpForUpdatesForm.attr('action'),
			data: $signUpForUpdatesForm.serialize(),
			method: 'POST',
			success: function() {
				$signUpForUpdatesForm.removeClass('loading').addClass('signed-up');
				$signUpForUpdatesForm.find('input[type=email]').attr('placeholder', "✓   we'll keep you posted")
			}
		})
		$signUpForUpdatesForm.find('input[type=email]').blur().val("");
	})
	$signUpForUpdatesForm.find('input[type=email]').focus(function() {
		$(this).attr('placeholder', 'email@school.edu');
	}).blur(function() {
		$(this).attr('placeholder', 'subscribe for updates');
	})
});
