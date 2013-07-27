var addTour = document.getElementById('addTour');

var genTour = document.getElementById('genTour');

genTour.style.display = 'none';

$(addTour).click(function(e) {
  e.preventDefault();
  $('.exhibit-item').each(function() {
    var i = $(this).find('input:checked').length;
    if (i === 0) {
      $(this).remove();
    }
  });

  $(genTour).show();
  $(addTour).remove();
});