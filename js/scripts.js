var addTour = document.getElementById('addTour');

var genTour = document.getElementById('genTour');

$(addTour).click(function(e) {
  e.preventDefault();
  $('.exhibit-item').each(function() {
    var i = $(this).find('input:checked').length;
    if (i === 0) {
      $(this).remove();
    }
  });

  $(genTour).show();
  $('#socMedia').show();
  $(addTour).remove();

  $('.content-wrap')
    .find('h2').html('Selected Items')
  .end()
    .find('p').html("These are the items you've selected for your audio tour.");
});