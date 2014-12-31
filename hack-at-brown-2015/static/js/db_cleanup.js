function propertySelected(value) {

  $('#displayProperty').text(value);

  $.ajax({
    url : '/dashboard/__breakdown/' + value,
    type : 'GET',
    success : function(response) {
      console.log(JSON.parse(response))
      populateTable(JSON.parse(response));
    },
    failure : function(response) {
      console.log(response);
    }
  });
}

function populateTable(groups) {
  var $table = $('#table');
  var $input = $('#submit');
  var keys = Object.keys(groups);
  $table.empty();
  $table.append("<th>Property<td>Number of Hackers</td></th>");
  for (var i = 0; i < keys.length; i++) {
    var $row = $('<tr class="property-value"><td class="prop">' + keys[i] + '</td><td class="count">' + groups[keys[i]] + '</td></tr>');
    $row.click(function() {
       $(this).toggleClass("selected");
        $input.prop('disabled', !$table.has('.selected').length);
    });
    $table.append($row);
  }
}

function cleanup() {
    var property = $('#property-selector').val();
    var replacedValues = {};
    var newValue = $('#newValue').val();
    $('#table').find('.selected .prop').each(function(index, elt) {
      replacedValues[elt.innerHTML] = newValue;
    });

    var $display = $('#display');
    function showStatus(success, msg) {
        $display.toggleClass('success', success);
        $display.toggleClass('failure', !success);
        if (msg) {
          $display.text(msg);
        }
    }

    if (!newValue) {
      showStatus(false, "You must input a replacement string");
      return;
    }

    if (!property) {
      showStatus(false, "You must choose a property");
      return;
    }

    data = {
      "property" : property,
      "jsonKeys" : replacedValues
    };

    $.ajax({
      url : '/dashboard/__cleanup',
      type : 'POST',
      data : JSON.stringify(data),
      success: function(response) {
        response = JSON.parse(response);
        showStatus(response.success, response.msg);
      },
      failure: function() {
        showStatus(false, "Server Error");
      }
    });
  }
