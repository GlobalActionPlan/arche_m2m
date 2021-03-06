/* Drag-drop questions to survey sections */

var unsaved = false;
var edit_variant = "";

/*
$('#deformsave').on('click', function() {
    unsaved = false;
});
$(window).on('beforeunload', function() {
    if (unsaved) {
        return "You have unsaved changes";
    }
});
*/

$(document).ready(function(){

  /* Attach sort function */
  $('.pickable_questions').sortable({
    connectWith: '.pickable_questions',
    receive: function(event, ui) {
      var name = ui.item.parents('ul').attr('name');
      ui.item.children('input').attr('name', name);
    },
    update: function(event, ui) {
      if (! unsaved) {
        unsaved = true;
      }
    }
  });

  /* Attach functions for add all/remove all-buttons */
  var processed_tags = [];

  /* Collect tags from question pool */
  $('.pickable_questions .question input').each(function() {
    var tags = $(this).attr('class').split(' ');
    for (i = 0; i < tags.length; ++i) {
      tag = tags[i].substring(4);
      if ((tags[i].substring(0, 4) == 'tag_') && (processed_tags.indexOf(tag) == -1)) {
        processed_tags.push(tag);
      }
    }
  });

  /* Insert option tag */
  processed_tags.sort();
  for (i = 0; i < processed_tags.length; ++i) {
    $('.add_from_tag').append('<option>' + processed_tags[i] + '</option>');
  }

  /* Click handler for add-from-tag-button */
  $('.add_questions').click(function() {
    var tag = $(this).siblings('.add_from_tag').val();
    var name = $(this).attr('name');
    if (tag != '') {
      $('#tag_listing .tag_' + tag).attr('name', name);
      $('#tag_listing .tag_' + tag).parent().appendTo( $('.survey_section[name=' + name + ']') );
    }
  });

  
  /* Display and sort questions by title in the question pool */
  $('.select_questions').click(function() {
  	var tag = $(this).siblings('.add_from_tag').val();
  	var name = $(this).attr('name');
  	var lis = document.querySelectorAll('#tag_listing li.question');
  	var array = new Array()
  	$('#tag_listing li.question').show();
  	for(var i=0; li=lis[i]; i++) {
  		if(tag != '' && $(li).find('.tag[name="' + tag + '"]').length == 0) {
  			$(li).hide();
  		} 
  		else
  		{
  			array.push($(li))
  		}	
  	}		
  	array.sort(function(a,b)
    	{
  	    return a.find('.question_text').html().toLowerCase().localeCompare(b.find('.question_text').html().toLowerCase())
    	});
  	$('#tag_listing').append(array);
  });

  /* Click handler for del-from-tag-button */
  $('.del_questions').click( function() {
    var tag = $(this).siblings('.add_from_tag').val();
    var name = $(this).attr('name');
    if (tag != '') {
      var section = $('.survey_section[name=' + name + ']');
      section.find('.question .tag_' + tag).attr('name', '');
      section.find('.question .tag_' + tag).parent().appendTo($('#tag_listing'));
	}
  });
});
